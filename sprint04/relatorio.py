from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


def gerar(resultado=None, destino=Path('resultados')):
    destino.mkdir(parents=True, exist_ok=True)
    dataset_path = destino/resultado['dataset_arquivo'] if resultado and resultado.get('dataset_arquivo') else Path(__file__).with_name('golden_dataset.json')
    dataset = json.loads(dataset_path.read_text(encoding='utf-8'))
    from collections import Counter
    categorias = Counter(c['categoria'] for c in dataset)
    distribuicao = '; '.join(f'{k}: {v}' for k,v in sorted(categorias.items()))
    estado = 'PENDENTE DE EXECUÇÃO REAL' if resultado is None else resultado['status'].upper()
    nomes = ['sprint03_atual', 'variacao_sem_guardiao']
    metricas = [
        ('correcao', 'Correção'), ('escopo', 'Aderência ao escopo'),
        ('fidelidade', 'Fidelidade ao contexto'), ('adequacao_recusa', 'Adequação da recusa'),
        ('taxa_recusa_correta', 'Taxa de recusa correta'), ('score_final', 'Score final'),
        ('cobertura', 'Cobertura válida'), ('latencia_media_s', 'Latência média por caso (s)'),
    ]
    tabela = [['Métrica', 'Sprint 03 atual', 'Variação sem guardião']]
    for chave, rotulo in metricas:
        linha = [rotulo]
        for nome in nomes:
            valor = resultado['resumo'][nome][chave] if resultado else None
            linha.append('Não medido' if valor is None else f'{valor:.3f}')
        tabela.append(linha)
    if resultado and resultado['classificacao']:
        classificacao = f"Classificação: {resultado['classificacao']}. A decisão usa o maior score final, com todas as avaliações válidas."
        a, b = (resultado['resumo'][nome]['score_final'] for nome in nomes)
        classificacao += f' Scores finais: versão atual {a:.3f}; sem guardião {b:.3f}; diferença absoluta {abs(a-b):.3f}.'
        if resultado['classificacao']=='empate':
            classificacao += ' Esta bateria não demonstra superioridade de qualidade de uma versão. A versão atual é mantida com sua proteção explícita de escopo; essa escolha de implementação não equivale a uma vitória no score.'
    else:
        classificacao = 'Classificação inconclusiva. Não há duas execuções completas que sustentem a escolha de uma versão vencedora.'
    if resultado and resultado['status'] == 'completo':
        c = resultado['resumo']['sprint03_atual']['correcao']
        confronto = (
            f'A avaliação manual da Sprint 03 descreveu os casos como adequados. O pipeline mediu correção média '
            f'de {c:.3f} para a versão atual. ' +
            ('Há concordância geral com a percepção manual, embora a nota agregada não prove aprovação de todos os casos.'
             if c >= .75 else 'Há divergência em relação à avaliação manual otimista; revisar as justificativas por caso para localizar as falhas.')
        )
    else:
        confronto = 'O registro manual anterior classifica os casos como adequados, mas não contém logs completos, tempos ou notas numéricas. Ainda não é possível confirmar concordância com o pipeline. Não foram atribuídas notas retrospectivas à Sprint 03.'
    secoes = [
        ('1. Objetivo e golden dataset', [
            f'Esta entrega avalia o ChargeGrid Intelligence mantendo o núcleo da Sprint 03. Situação: {estado}.',
            f'O golden dataset avaliado contém {len(dataset)} cenários ({distribuicao}). Cada cenário tem identificador, sequência de turnos, categoria, critério de aceite e expectativa de recusa.',
            'O conjunto expandido retoma os fluxos das sprints anteriores. A bateria econômica seleciona disponibilidade, protocolos, pagamento, memória, escopo, prompt injection, segurança elétrica e transações sem integração. O JSON da execução documenta exatamente quais casos foram medidos.',
            'Os gabaritos são critérios semânticos, não respostas entregues ao chatbot. Apenas o avaliador recebe o gabarito. Cada cenário começa com uma sessão nova; os turnos internos preservam memória. Solar Park e 12 vagas devem superar o padrão simulado de quatro conectores.',
            'A base usa dados simulados explicitamente identificados. Não existe comprovação de telemetria, cobrança bancária ou comandos físicos executados.'
        ]),
        ('2. Pipeline, versões e métricas', [
            'Ferramenta: LangChain com Gemini e LLM as a judge. A saída do juiz é validada por Pydantic. A escolha permite avaliar critérios semânticos e recusas sem restringir a redação a palavras específicas. Referência: https://reference.langchain.com/python/langchain-google-genai/chat_models/ChatGoogleGenerativeAI/with_structured_output',
            'Versão A: cópia da Sprint 03 atual com guardião de escopo. Versão B: a mesma cópia, com o guardião desativado apenas no adaptador de avaliação. Prompt, memória, modelo e dataset permanecem iguais. Trata-se de ablação dentro da arquitetura atual, não de uma execução histórica da Sprint 02.',
            'O juiz recebe contexto, diálogo completo e gabarito, sem o nome da versão. Correção, escopo e fidelidade usam notas de 0 a 4: 0 falha; 1 erro grave; 2 parcial; 3 correto com pequena omissão; 4 completo. As médias normalizam essas notas dividindo por quatro.',
            'Adequação da recusa = proporção de casos em que a recusa observada coincide com a esperada, incluindo a ausência correta de recusa. Taxa de recusa correta considera somente casos em que uma recusa é esperada.',
            'Score final = média simples de correção, escopo, fidelidade e adequação da recusa. Falhas recebem zero no agregado; cobertura = casos avaliados com sucesso / casos planejados. Só há classificação quando ambas as versões alcançam cobertura 1.',
            'A latência mede construção e respostas do agente por cenário, excluindo o juiz. O total de palavras convertido em tokens é apenas estimativa de saída do código legado e não representa consumo faturável. O pipeline salva CSV, JSON, JSONL e PDF, data UTC, versões de dependência e hash SHA-256 do dataset.'
        ]),
        ('3. Resultados e confronto com a Sprint 03', [classificacao, confronto]),
        ('4. Limitações e equipe', [
            'Viés do juiz: um modelo pode favorecer respostas semelhantes às suas; usar outro modelo como juiz, auditar justificativas e repetir execuções reduz, mas não elimina, esse risco. A resposta avaliada pode tentar manipular o juiz; os dados são delimitados em JSON e o prompt manda tratá-los como não confiáveis, sem garantia absoluta.',
            f'Cobertura: {len(dataset)} casos não representam toda a operação comercial. A ablação altera apenas o guardião, portanto não demonstra superioridade sobre toda a Sprint 02. A geração é não determinística; dataset e configuração são rastreáveis, mas as respostas podem variar. Recomenda-se três repetições e revisão humana dos casos divergentes.',
            'Custos e limites: o modo completo tem 42 chamadas ao agente e até 32 ao juiz. A bateria econômica reduz para 20 turnos de conversa (alguns bloqueados sem chamada ao modelo) e uma avaliação em lote. Quota, indisponibilidade e rede podem impedir conclusão. Erros são registrados pelo tipo, sem credenciais.',
            'Divisão de responsabilidades confirmada pelo grupo, organizada por disciplina. Turma informada: Ciência da Computação, 1º ano.',
            'Mateus de Oliveira Fernandes Neves - RM 572431: Data Structures and Algorithms.',
            'Angela Sousa Takezawa - RM 570797: Prompt and Artificial Intelligence.',
            'Pedro Soares de Souza - RM 571285: Modelagem Matemática e Computacional.',
            'Paulo Henrique Lira Bilac de Araújo - RM 569496: Computer Organization and Architecture / Computer Science.',
            'Olavo Dadario Vianna Barreto - RM 569272: Pensamento Computacional e Automação com Python / Soluções em Energias Renováveis e Sustentáveis.',
            'John Cutile Titirico - RM 571976: Modelagem Linear para Aprendizado de Máquina.',
            'A chave não é incluída no código nem no relatório. O repositório de referência é https://github.com/woowoo88/SPRINT3_IA. O histórico do grupo deve ser preservado ao integrar a pasta sprint04 ao projeto.'
        ])
    ]
    if resultado:
        secoes[2][1].insert(0, 'Configuração desta execução: modelo do agente ' + resultado['modelo_agente'] +
                           '; juiz ' + resultado['modelo_juiz'] + '; repetições ' + str(resultado['repeticoes']) +
                           '; data UTC ' + resultado['executado_em_utc'] + '. Parâmetros de amostragem: padrões do provedor.')
        if resultado.get('juiz_em_lote'):
            secoes[1][1].append('Execução econômica: oito cenários foram selecionados antes da medição para caber na quota disponível. Agente e juiz usam o mesmo modelo em chamadas separadas. O juiz recebe os 16 registros em um lote, sem nomes de versão. Essa escolha reduz chamadas, mas pode introduzir efeito de ordem e viés do modelo avaliando a própria família. A latência inclui a espera pelo limitador compartilhado.')
        if resultado.get('retomada_em_utc'):
            secoes[1][1].append('Retentativas: apenas chamadas que terminaram com erro técnico foram repetidas. Os turnos já respondidos foram restaurados na memória e as respostas válidas não foram regeneradas. O juiz reavaliou o lote completo. Os erros originais foram preservados em respostas_tentativa_inicial.jsonl e a latência acumula as tentativas; por isso ela não representa apenas tempo de inferência em condições ideais.')
        backup=destino/'respostas_tentativa_inicial.jsonl'
        if backup.exists():
            antigos={(r['id'],r['versao']):r for r in map(json.loads,backup.read_text(encoding='utf-8').splitlines())}
            atuais=list(map(json.loads,(destino/'respostas.jsonl').read_text(encoding='utf-8').splitlines()))
            alterados=[r for r in atuais if antigos[(r['id'],r['versao'])]['status']=='ok' and
                       any(antigos[(r['id'],r['versao'])]['juiz'][k]!=r['juiz'][k] for k in ('correcao','escopo','fidelidade','recusou'))]
            secoes[2][1].append(f'Auditoria do juiz: {len(alterados)} registros com respostas inalteradas receberam notas ou decisões de recusa diferentes na reavaliação. Isso demonstra instabilidade do avaliador; as notas máximas não significam ausência de defeitos. No caso F03 sem guardião, a primeira avaliação apontou ambiguidade sobre processamento de pagamento, mas a segunda aceitou a mesma resposta. Nos casos B02, mudou a interpretação da recusa. Os dois pareceres estão preservados para revisão humana.')
            secoes[2][1].append('Confronto com a avaliação manual: há concordância agregada com os pareceres adequados da Sprint 03, mas não foi comprovado ganho de qualidade. As divergências entre pareceres do próprio juiz recomendam cautela, principalmente em pagamento e ações sem integração. Os cenários de memória recuperaram Solar Park e 12 vagas após a recuperação do erro técnico. Não existem medições históricas equivalentes para afirmar uma redução causal de latência.')
    md = ['# Relatório final - ChargeGrid Intelligence - Sprint 04', f'\nEstado: {estado}\n']
    for titulo, paragrafos in secoes:
        md.append('## ' + titulo)
        md.extend(paragrafos)
        if titulo.startswith('3.'):
            md.extend(['| ' + ' | '.join(tabela[0]) + ' |', '|---|---|---|'])
            md.extend('| ' + ' | '.join(row) + ' |' for row in tabela[1:])
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
            story.extend([Paragraph(escape(paragrafo), styles['BodyText']), Spacer(1, 9)])
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
        canvas.drawString(1.7*cm, 1*cm, f'ChargeGrid - {estado}')
        canvas.drawRightString(A4[0]-1.7*cm, 1*cm, str(doc.page))
    SimpleDocTemplate(str(destino/'relatorio_final.pdf'), pagesize=A4,
                      leftMargin=1.7*cm, rightMargin=1.7*cm, topMargin=1.5*cm,
                      bottomMargin=1.7*cm).build(story, onFirstPage=rodape, onLaterPages=rodape)


if __name__ == '__main__':
    gerar()
