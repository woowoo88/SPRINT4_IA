from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

REFERENCIA = 'https://reference.langchain.com/python/langchain-google-genai/chat_models/ChatGoogleGenerativeAI/with_structured_output'

def gerar(resultado=None, destino=Path('resultados')):
    destino.mkdir(parents=True, exist_ok=True)
    dataset_path = destino/resultado['dataset_arquivo'] if resultado and resultado.get('dataset_arquivo') else Path(__file__).with_name('golden_dataset.json')
    dataset = json.loads(dataset_path.read_text(encoding='utf-8'))
    from collections import Counter
    categorias = Counter(c['categoria'] for c in dataset)
    rotulos = {'memoria':'memória', 'seguranca':'segurança'}
    distribuicao = '; '.join(f'{rotulos.get(k,k)}: {v}' for k,v in sorted(categorias.items()))
    titulo_equipe = '5. Divisão de responsabilidades da equipe'
    nomes = ['sprint03_atual', 'variacao_sem_guardiao']
    metricas = [
        ('correcao', 'Correção'), ('escopo', 'Aderência ao escopo'),
        ('fidelidade', 'Fidelidade ao contexto'), ('adequacao_recusa', 'Adequação da recusa'),
        ('taxa_recusa_correta', 'Taxa de recusa correta'), ('score_final', 'Nota final'),
        ('cobertura', 'Cobertura válida'), ('latencia_media_s', 'Latência média por caso (s)'),
    ]
    tabela = [['Métrica', 'Sprint 03 atual', 'Variação sem guardião']]
    for chave, rotulo in metricas:
        linha = [rotulo]
        for nome in nomes:
            valor = resultado['resumo'][nome][chave] if resultado else None
            linha.append('Não medido' if valor is None else f'{valor:.3f}'.replace('.', ','))
        tabela.append(linha)
    if resultado and resultado['classificacao']:
        classificacao = f"Classificação: {resultado['classificacao']}. O resultado considera a média das quatro métricas e exige que todos os casos tenham sido avaliados."
        a, b = (resultado['resumo'][nome]['score_final'] for nome in nomes)
        valores = [f'{v:.3f}'.replace('.', ',') for v in (a,b,abs(a-b))]
        classificacao += f' Notas finais: versão atual {valores[0]}; sem guardião {valores[1]}; diferença {valores[2]}.'
        if resultado['classificacao']=='empate':
            classificacao += ' As duas versões tiveram o mesmo desempenho nas métricas de qualidade. O projeto mantém o guardião de escopo como uma camada de controle, mas os resultados desta bateria não demonstram vantagem dele na nota final.'
    else:
        classificacao = 'Classificação inconclusiva. Não há duas execuções completas que sustentem a escolha de uma versão vencedora.'
    if resultado and resultado['status'] == 'completo':
        c = resultado['resumo']['sprint03_atual']['correcao']
        confronto = (
            'Na Sprint 03, a avaliação manual classificou os testes como adequados. Nesta execução, '
            'a versão atual obteve correção média de ' + f'{c:.3f}'.replace('.', ',') + '. ' +
            ('O resultado concorda com a avaliação anterior nos cenários medidos.'
             if c >= .75 else 'O resultado diverge da avaliação anterior e exige análise das justificativas por caso.')
        )
    else:
        confronto = 'O registro manual anterior classifica os casos como adequados, mas não contém logs completos, tempos ou notas numéricas. Ainda não é possível confirmar concordância com o pipeline. Não foram atribuídas notas retrospectivas à Sprint 03.'
    secoes = [
        ('1. Objetivo e golden dataset', [
            'O objetivo da Sprint 04 foi medir o desempenho do ChargeGrid Intelligence de forma automatizada, usando a aplicação desenvolvida na Sprint 03.',
            f'Foram avaliados {len(dataset)} cenários ({distribuicao}). Cada caso reúne as mensagens do usuário, um critério de aceite e a indicação de quando a resposta deve recusar o pedido.',
            'O conjunto expandido contém 16 cenários baseados nos testes anteriores. Para a execução com quota reduzida, foram selecionados oito: disponibilidade de vagas, protocolos, pagamento, memória, escopo, prompt injection, segurança elétrica e transações sem integração. O arquivo golden_dataset_avaliado.json registra os casos utilizados.',
            'O gabarito é enviado somente ao avaliador. Cada caso começa em uma sessão independente, enquanto os turnos de uma mesma conversa compartilham o histórico. No teste de memória, o agente precisa recuperar o nome Solar Park e as 12 vagas informadas, em vez de repetir o padrão de quatro conectores.',
            'A aplicação utiliza dados operacionais simulados. Não há conexão ativa com sensores, meios de pagamento ou carregadores físicos.'
        ]),
        ('2. Pipeline, versões e métricas', [
            'A avaliação foi implementada em Python, com LangChain e Gemini no papel de juiz (LLM as a judge). A resposta estruturada do avaliador é validada com Pydantic. Essa abordagem permite verificar o sentido da resposta e a adequação das recusas, sem exigir uma redação idêntica ao gabarito.',
            'Foram comparadas duas variações da Sprint 03: a versão atual e a versão com o guardião de escopo desativado no adaptador de teste. As duas usam o mesmo modelo, prompt, memória e conjunto de casos. A comparação avalia o efeito desse componente dentro da arquitetura atual.',
            'O avaliador recebe o contexto, o diálogo completo e o gabarito, sem o nome da versão. Correção, aderência ao escopo e fidelidade ao contexto recebem notas de 0 a 4: 0 indica falha; 1, erro grave; 2, atendimento parcial; 3, resposta correta com pequena omissão; e 4, atendimento completo. A média de cada critério é dividida por quatro para ficar entre 0 e 1.',
            'A adequação da recusa corresponde à proporção de casos em que a decisão de recusar ou responder coincide com o gabarito. A taxa de recusa correta considera apenas os casos em que uma recusa era esperada.',
            'A nota final é a média simples de correção, escopo, fidelidade e adequação da recusa. Falhas técnicas recebem zero no cálculo. A cobertura é a razão entre casos avaliados e casos planejados; a classificação só é emitida quando as duas versões têm cobertura completa.',
            'A latência é medida por cenário e inclui a criação do agente, as respostas e a espera pelo limitador de chamadas, mas exclui o juiz. Os resultados são exportados em CSV, JSON, JSONL e PDF, com data UTC, versões das dependências e hash SHA-256 do dataset. A estimativa de tokens do código original não corresponde ao consumo faturado pela API.'
        ]),
        ('3. Resultados e confronto com a Sprint 03', [classificacao, confronto]),
        ('4. Limitações', [
            'O uso do mesmo modelo para gerar e avaliar respostas pode introduzir viés. Além disso, o avaliador pode ser influenciado pelo conteúdo recebido. O prompt orienta o juiz a tratar os diálogos como dados, mas essa medida não elimina o risco de manipulação.',
            f'O conjunto de {len(dataset)} casos cobre apenas parte da operação de um eletroposto. A comparação foi feita em uma única repetição e altera somente o guardião de escopo. Portanto, não permite generalizar o resultado para toda a aplicação ou concluir que ela supera a Sprint 02.',
            'A quota da API limitou o tamanho da bateria. O modo econômico utiliza 20 turnos de conversa e uma avaliação em lote, além das chamadas de retomada quando há erro. A latência também foi afetada pela rede e pela espera entre requisições.',
            titulo_equipe,
            'Curso e turma: Ciência da Computação, 1º ano. Responsabilidades organizadas por disciplina.',
            'Mateus de Oliveira Fernandes Neves - RM 572431: Data Structures and Algorithms.',
            'Angela Sousa Takezawa - RM 570797: Prompt and Artificial Intelligence.',
            'Pedro Soares de Souza - RM 571285: Modelagem Matemática e Computacional.',
            'Paulo Henrique Lira Bilac de Araújo - RM 569496: Computer Organization and Architecture / Computer Science.',
            'Olavo Dadario Vianna Barreto - RM 569272: Pensamento Computacional e Automação com Python / Soluções em Energias Renováveis e Sustentáveis.',
            'John Cutile Titirico - RM 571976: Modelagem Linear para Aprendizado de Máquina.',
            'Código, dataset e registros da avaliação: https://github.com/woowoo88/SPRINT3_IA.'
        ])
    ]
    if resultado:
        registro = datetime.fromisoformat(resultado.get('retomada_em_utc',resultado['executado_em_utc'])).strftime('%d/%m/%Y, %H:%M UTC')
        secoes[2][1].insert(0, 'Modelo do agente: ' + resultado['modelo_agente'] +
                           '. Modelo do juiz: ' + resultado['modelo_juiz'] + '. Repetições: ' + str(resultado['repeticoes']) +
                           '. Registro: ' + registro + '. Foram usados os parâmetros padrão do provedor.')
        if resultado.get('juiz_em_lote'):
            secoes[1][1].append('No modo econômico, as 16 respostas das duas versões são avaliadas em um único lote. O agente e o juiz usam o mesmo modelo em chamadas separadas. Isso reduz o número de requisições, mas pode tornar a avaliação sensível à ordem dos registros e ao viés do próprio modelo.')
        if resultado.get('retomada_em_utc'):
            secoes[1][1].append('As chamadas com erro técnico foram retomadas a partir do último turno respondido. As respostas válidas foram mantidas e o juiz avaliou novamente o lote completo. A primeira tentativa foi preservada em respostas_tentativa_inicial.jsonl. O tempo das tentativas anteriores foi somado à latência de cada caso.')
        backup=destino/'respostas_tentativa_inicial.jsonl'
        if backup.exists():
            antigos={(r['id'],r['versao']):r for r in map(json.loads,backup.read_text(encoding='utf-8').splitlines())}
            atuais=list(map(json.loads,(destino/'respostas.jsonl').read_text(encoding='utf-8').splitlines()))
            alterados=[r for r in atuais if antigos[(r['id'],r['versao'])]['status']=='ok' and
                       any(antigos[(r['id'],r['versao'])]['juiz'][k]!=r['juiz'][k] for k in ('correcao','escopo','fidelidade','recusou'))]
            secoes[2][1].append(f'O avaliador mudou a nota ou a decisão de recusa em {len(alterados)} registros cujas respostas permaneceram iguais. No caso F03 sem guardião, a primeira avaliação apontou uma ambiguidade sobre o processamento do pagamento; a segunda aceitou a mesma resposta. Em B02, mudou a interpretação da recusa. Essa variação limita a confiança nas notas máximas e justifica a análise das justificativas junto dos valores da tabela.')
            secoes[2][1].append('O teste de memória recuperou Solar Park e 12 vagas nas duas versões após a retomada da chamada com erro. O empate e as mudanças de parecer do juiz não sustentam uma conclusão de melhora na qualidade. Também faltam medições históricas equivalentes para atribuir uma redução de latência à nova arquitetura.')
    md = ['# Relatório final - ChargeGrid Intelligence - Sprint 04']
    for titulo, paragrafos in secoes:
        md.append('## ' + titulo)
        md.extend('## ' + texto if texto == titulo_equipe else texto for texto in paragrafos)
        if titulo.startswith('2.'):
            md.append(f'Referência: [LangChain, saída estruturada com Gemini]({REFERENCIA}).')
        if titulo.startswith('3.'):
            linhas_tabela = ['| ' + ' | '.join(tabela[0]) + ' |', '|---|---|---|']
            linhas_tabela.extend('| ' + ' | '.join(row) + ' |' for row in tabela[1:])
            md.append('\n'.join(linhas_tabela))
    if resultado:
        md.append('## Configuração registrada\n```json\n' + json.dumps(resultado, ensure_ascii=False, indent=2) + '\n```')
    (destino / 'relatorio_final.md').write_text('\n\n'.join(md), encoding='utf-8')
    styles = getSampleStyleSheet()
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 14
    story = []
    for i, (titulo, paragrafos) in enumerate(secoes):
        if i:
            story.append(PageBreak())
        story.extend([Paragraph('ChargeGrid Intelligence | Sprint 04', styles['Title']),
                      Paragraph(escape(titulo), styles['Heading1'])])
        for paragrafo in paragrafos:
            estilo = styles['Heading2'] if paragrafo == titulo_equipe else styles['BodyText']
            story.extend([Paragraph(escape(paragrafo), estilo), Spacer(1, 9)])
        if i == 1:
            story.append(Paragraph(f'Referência: <link href="{REFERENCIA}" color="#155e75">LangChain, saída estruturada com Gemini</link>.', styles['BodyText']))
        if i == 2:
            cells = [[Paragraph(escape(c), styles['BodyText']) for c in row] for row in tabela]
            table = Table(cells, colWidths=[7*cm, 4.3*cm, 4.3*cm], repeatRows=1)
            table.setStyle(TableStyle([('BACKGROUND', (0,0),(-1,0),colors.HexColor('#dcecf0')),
                                       ('GRID',(0,0),(-1,-1),.4,colors.grey),
                                       ('VALIGN',(0,0),(-1,-1),'TOP'),
                                       ('TOPPADDING',(0,0),(-1,-1),7),
                                       ('BOTTOMPADDING',(0,0),(-1,-1),7)]))
            story.append(table)
    def rodape(canvas, doc):
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(A4[0]-1.7*cm, 1*cm, str(doc.page))
    SimpleDocTemplate(str(destino/'relatorio_final.pdf'), pagesize=A4,
                      leftMargin=1.7*cm, rightMargin=1.7*cm, topMargin=1.5*cm,
                      bottomMargin=1.7*cm).build(story, onFirstPage=rodape, onLaterPages=rodape)


if __name__ == '__main__':
    gerar()
