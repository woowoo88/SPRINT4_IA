"""Avaliação pareada com juiz em lote para contas de quota reduzida."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import time
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from chargegrid_intelligence import ChargeGridAgent
from chargegrid_intelligence.knowledge import PROJECT_CONTEXT
from .avaliar import Julgamento, SemGuardiao, VERSOES, RUBRICA, agregar, carregar_dataset
from .relatorio import gerar

IDS = ('F01', 'F02', 'F03', 'M01', 'E01', 'S01', 'S02', 'B02')


class ItemJulgado(Julgamento):
    registro_id: str


class LoteJulgado(BaseModel):
    avaliacoes: list[ItemJulgado]


def executar_economico(modelo, destino, chamadas_por_minuto=8):
    load_dotenv()
    key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not key:
        raise RuntimeError('Configure a chave no ambiente de execução.')
    os.environ['GOOGLE_API_KEY'] = key
    os.environ.pop('GEMINI_API_KEY', None)
    casos, _ = carregar_dataset()
    casos = [c for c in casos if c['id'] in IDS]
    destino.mkdir(parents=True, exist_ok=True)
    dataset_bytes = json.dumps(casos, ensure_ascii=False, indent=2).encode('utf-8')
    (destino/'golden_dataset_avaliado.json').write_bytes(dataset_bytes)
    limiter = InMemoryRateLimiter(requests_per_second=chamadas_por_minuto / 60,
                                  check_every_n_seconds=.1, max_bucket_size=1)
    linhas, registros = [], []
    for caso in casos:
        for nome in VERSOES:
            r = {'id':caso['id'], 'categoria':caso['categoria'], 'versao':nome,
                 'repeticao':1, 'recusa_esperada':caso['recusa'], 'gabarito':caso['gabarito'],
                 'status':'erro', 'dialogo':[]}
            inicio = time.perf_counter()
            try:
                agente = ChargeGridAgent(model_name=modelo)
                agente._llm = ChatGoogleGenerativeAI(model=modelo, google_api_key=key,
                                                    timeout=60, max_retries=0, rate_limiter=limiter)
                if nome == 'variacao_sem_guardiao':
                    agente.scope_guard = SemGuardiao()
                for pergunta in caso['turnos']:
                    answer = agente.ask(pergunta, session_id=caso['id'])['answer']
                    r['dialogo'].append({'usuario':pergunta, 'resposta':answer})
                registro_id = f'r{len(linhas):03d}'
                r['registro_id'] = registro_id
                registros.append({'registro_id':registro_id, 'dialogo':r['dialogo'], 'gabarito':caso['gabarito']})
                r['status'] = 'aguardando_juiz'
            except Exception as exc:
                r['erro_tipo'] = type(exc).__name__
            r['latencia_s'] = round(time.perf_counter() - inicio, 3)
            linhas.append(r)
            (destino/'respostas_parciais.json').write_text(json.dumps(linhas,ensure_ascii=False,indent=2),encoding='utf-8')
            print(f"{nome}: {caso['id']} - {r['status']}", flush=True)
    if registros:
        try:
            juiz = ChatGoogleGenerativeAI(model=modelo, google_api_key=key, timeout=120,
                                         max_retries=0, rate_limiter=limiter).with_structured_output(LoteJulgado)
            instrucao = RUBRICA + '\nAvalie cada registro separadamente. Retorne uma avaliação por registro_id, sem omitir nem duplicar IDs. Não compare estilos entre registros.'
            julgamento = juiz.invoke([SystemMessage(content=instrucao), HumanMessage(content=json.dumps(
                {'contexto':PROJECT_CONTEXT,'registros':registros},ensure_ascii=False))])
            avaliados = {j.registro_id:j for j in julgamento.avaliacoes}
            if len(avaliados) != len(julgamento.avaliacoes) or set(avaliados) != {r['registro_id'] for r in registros}:
                raise ValueError('IDs duplicados, ausentes ou inesperados no juiz em lote.')
            for r in linhas:
                if r['status'] == 'aguardando_juiz':
                    r['juiz'] = avaliados[r['registro_id']].model_dump(exclude={'registro_id'})
                    r['status'] = 'ok'
        except Exception as exc:
            for r in linhas:
                if r['status'] == 'aguardando_juiz':
                    r.update(status='erro', erro_tipo=type(exc).__name__)
    with (destino/'respostas.jsonl').open('w',encoding='utf-8') as f:
        for r in linhas:
            f.write(json.dumps(r,ensure_ascii=False)+'\n')
    resumo = agregar(linhas,len(casos))
    completo = all(r['cobertura']==1 for r in resumo.values())
    melhor = max(resumo,key=lambda n:resumo[n]['score_final']) if completo else None
    if completo and len({round(r['score_final'],8) for r in resumo.values()})==1:
        melhor='empate'
    resultado = {'executado_em_utc':datetime.now(timezone.utc).isoformat(),
                 'dataset_sha256':hashlib.sha256(dataset_bytes).hexdigest(),
                 'dataset_arquivo':'golden_dataset_avaliado.json', 'modelo_agente':modelo,
                 'modelo_juiz':modelo, 'python':platform.python_version(),
                 'langchain_google_genai':version('langchain-google-genai'),
                 'repeticoes':1, 'casos_por_versao':len(casos), 'juiz_em_lote':True,
                 'limite_chamadas_por_minuto':chamadas_por_minuto,
                 'resumo':resumo,'classificacao':melhor,'status':'completo' if completo else 'incompleto'}
    (destino/'resumo.json').write_text(json.dumps(resultado,ensure_ascii=False,indent=2),encoding='utf-8')
    with (destino/'notas.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f)
        w.writerow(['versao','caso','categoria','status','correcao','escopo','fidelidade','recusou','latencia_s'])
        for r in linhas:
            w.writerow([r['versao'],r['id'],r['categoria'],r['status'],
                        *[r.get('juiz',{}).get(k,'') for k in ('correcao','escopo','fidelidade','recusou')],r['latencia_s']])
    gerar(resultado,destino)
    print('SITUACAO_FINAL:',resultado['status'],flush=True)
    print('CLASSIFICACAO:',resultado['classificacao'],flush=True)
    return resultado


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modelo',required=True)
    parser.add_argument('--saida',type=Path,default=Path('resultados/economico'))
    args=parser.parse_args()
    executar_economico(args.modelo,args.saida)
