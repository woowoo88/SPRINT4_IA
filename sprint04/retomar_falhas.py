"""Retoma somente chamadas com erro técnico, preservando a primeira tentativa."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI

from chargegrid_intelligence import ChargeGridAgent
from chargegrid_intelligence.memory import update_facts
from chargegrid_intelligence.knowledge import PROJECT_CONTEXT
from .avaliar import SemGuardiao, RUBRICA, agregar
from .avaliar_economico import LoteJulgado
from .relatorio import gerar


def retomar(destino, juiz_modelo=None):
    key=os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not key:
        raise RuntimeError('Configure a chave no ambiente.')
    path=destino/'respostas.jsonl'
    original=path.read_text(encoding='utf-8')
    backup=destino/'respostas_tentativa_inicial.jsonl'
    if not backup.exists():
        backup.write_text(original,encoding='utf-8')
    linhas=[json.loads(l) for l in original.splitlines()]
    resultado=json.loads((destino/'resumo.json').read_text(encoding='utf-8'))
    casos={c['id']:c for c in json.loads((destino/resultado['dataset_arquivo']).read_text(encoding='utf-8'))}
    limiter=InMemoryRateLimiter(requests_per_second=8/60,check_every_n_seconds=.1,max_bucket_size=1)
    for r in linhas:
        if r['status']=='ok':
            continue
        anterior={'erro_tipo':r.get('erro_tipo'),'dialogo':list(r['dialogo']),
                  'latencia_s':r['latencia_s']}
        r.setdefault('tentativas_anteriores',[]).append(anterior)
        inicio=time.perf_counter()
        try:
            agente=ChargeGridAgent(model_name=resultado['modelo_agente'])
            agente._llm=ChatGoogleGenerativeAI(model=resultado['modelo_agente'],google_api_key=key,
                                             timeout=60,max_retries=0,rate_limiter=limiter)
            if r['versao']=='variacao_sem_guardiao':
                agente.scope_guard=SemGuardiao()
            facts={}
            history=agente._get_history(r['id'])
            for turno in r['dialogo']:
                facts=update_facts(turno['usuario'],facts)
                history.add_user_message(turno['usuario'])
                history.add_ai_message(turno['resposta'])
            agente._facts_by_session[r['id']]=facts
            for pergunta in casos[r['id']]['turnos'][len(r['dialogo']):]:
                answer=agente.ask(pergunta,session_id=r['id'])['answer']
                r['dialogo'].append({'usuario':pergunta,'resposta':answer})
            r['status']='aguardando_juiz'
            r.pop('erro_tipo',None)
        except Exception as exc:
            r.update(status='erro',erro_tipo=type(exc).__name__)
            print('Diagnóstico seguro:',type(exc).__name__,str(exc).replace(key,'[oculto]')[:500],flush=True)
        r['latencia_s']+=round(time.perf_counter()-inicio,3)
        print('Retomada:',r['id'],r['versao'],r['status'],flush=True)
    juiz_modelo=juiz_modelo or resultado['modelo_juiz']
    payload=[]
    for i,r in enumerate(linhas):
        if r['status']!='erro':
            r['registro_id']=f'r{i:03d}'
            payload.append({k:r[k] for k in ('registro_id','dialogo','gabarito')})
    try:
        juiz=ChatGoogleGenerativeAI(model=juiz_modelo,google_api_key=key,timeout=120,
                                   max_retries=0,rate_limiter=limiter).with_structured_output(LoteJulgado)
        j=juiz.invoke([SystemMessage(content=RUBRICA+'\nAvalie separadamente todos os registros por registro_id, sem omitir nem duplicar IDs.'),
                       HumanMessage(content=json.dumps({'contexto':PROJECT_CONTEXT,'registros':payload},ensure_ascii=False))])
        avaliados={x.registro_id:x for x in j.avaliacoes}
        if len(avaliados)!=len(j.avaliacoes) or set(avaliados)!={r['registro_id'] for r in payload}:
            raise ValueError('Juiz devolveu IDs incompatíveis.')
        for r in linhas:
            if r['status']!='erro':
                r['juiz']=avaliados[r['registro_id']].model_dump(exclude={'registro_id'})
                r['status']='ok'
        resultado['modelo_juiz']=juiz_modelo
    except Exception as exc:
        print('Juiz:',type(exc).__name__,str(exc).replace(key,'[oculto]')[:500],flush=True)
        for r in linhas:
            if r['status']=='aguardando_juiz':
                r.update(status='erro',erro_tipo=type(exc).__name__)
    with path.open('w',encoding='utf-8') as f:
        for r in linhas:
            f.write(json.dumps(r,ensure_ascii=False)+'\n')
    resultado['resumo']=agregar(linhas,len(casos))
    completo=all(r['cobertura']==1 for r in resultado['resumo'].values())
    resultado['status']='completo' if completo else 'incompleto'
    resultado['classificacao']=max(resultado['resumo'],key=lambda n:resultado['resumo'][n]['score_final']) if completo else None
    if completo and len({round(r['score_final'],8) for r in resultado['resumo'].values()})==1:
        resultado['classificacao']='empate'
    resultado['retomada_em_utc']=datetime.now(timezone.utc).isoformat()
    resultado['politica_retentativa']='Repetir apenas erros técnicos; respostas válidas não são regeneradas; juiz reavalia todo o lote.'
    (destino/'resumo.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2),encoding='utf-8')
    import csv
    with (destino/'notas.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f)
        w.writerow(['versao','caso','categoria','status','correcao','escopo','fidelidade','recusou','latencia_s'])
        for r in linhas:
            w.writerow([r['versao'],r['id'],r['categoria'],r['status'],
                        *[r.get('juiz',{}).get(k,'') for k in ('correcao','escopo','fidelidade','recusou')],r['latencia_s']])
    gerar(resultado,destino)
    print('SITUACAO_FINAL:',resultado['status'],flush=True)
    return resultado
