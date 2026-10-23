# Relatório final - ChargeGrid Intelligence - Sprint 04

## 1. Objetivo e golden dataset

O objetivo da Sprint 04 foi medir o desempenho do ChargeGrid Intelligence de forma automatizada, usando a aplicação desenvolvida na Sprint 03.

Foram avaliados 8 cenários (borda: 1; escopo: 1; funcionalidade: 3; memória: 1; segurança: 2). Cada caso reúne as mensagens do usuário, um critério de aceite e a indicação de quando a resposta deve recusar o pedido.

O conjunto expandido contém 16 cenários baseados nos testes anteriores. Para a execução com quota reduzida, foram selecionados oito: disponibilidade de vagas, protocolos, pagamento, memória, escopo, prompt injection, segurança elétrica e transações sem integração. O arquivo golden_dataset_avaliado.json registra os casos utilizados.

O gabarito é enviado somente ao avaliador. Cada caso começa em uma sessão independente, enquanto os turnos de uma mesma conversa compartilham o histórico. No teste de memória, o agente precisa recuperar o nome Solar Park e as 12 vagas informadas, em vez de repetir o padrão de quatro conectores.

A aplicação utiliza dados operacionais simulados. Não há conexão ativa com sensores, meios de pagamento ou carregadores físicos.

## 2. Pipeline, versões e métricas

A avaliação foi implementada em Python, com LangChain e Gemini no papel de juiz (LLM as a judge). A resposta estruturada do avaliador é validada com Pydantic. Essa abordagem permite verificar o sentido da resposta e a adequação das recusas, sem exigir uma redação idêntica ao gabarito.

Foram comparadas duas variações da Sprint 03: a versão atual e a versão com o guardião de escopo desativado no adaptador de teste. As duas usam o mesmo modelo, prompt, memória e conjunto de casos. A comparação avalia o efeito desse componente dentro da arquitetura atual.

O avaliador recebe o contexto, o diálogo completo e o gabarito, sem o nome da versão. Correção, aderência ao escopo e fidelidade ao contexto recebem notas de 0 a 4: 0 indica falha; 1, erro grave; 2, atendimento parcial; 3, resposta correta com pequena omissão; e 4, atendimento completo. A média de cada critério é dividida por quatro para ficar entre 0 e 1.

A adequação da recusa corresponde à proporção de casos em que a decisão de recusar ou responder coincide com o gabarito. A taxa de recusa correta considera apenas os casos em que uma recusa era esperada.

A nota final é a média simples de correção, escopo, fidelidade e adequação da recusa. Falhas técnicas recebem zero no cálculo. A cobertura é a razão entre casos avaliados e casos planejados; a classificação só é emitida quando as duas versões têm cobertura completa.

A latência é medida por cenário e inclui a criação do agente, as respostas e a espera pelo limitador de chamadas, mas exclui o juiz. Os resultados são exportados em CSV, JSON, JSONL e PDF, com data UTC, versões das dependências e hash SHA-256 do dataset. A estimativa de tokens do código original não corresponde ao consumo faturado pela API.

No modo econômico, as 16 respostas das duas versões são avaliadas em um único lote. O agente e o juiz usam o mesmo modelo em chamadas separadas. Isso reduz o número de requisições, mas pode tornar a avaliação sensível à ordem dos registros e ao viés do próprio modelo.

As chamadas com erro técnico foram retomadas a partir do último turno respondido. As respostas válidas foram mantidas e o juiz avaliou novamente o lote completo. A primeira tentativa foi preservada em respostas_tentativa_inicial.jsonl. O tempo das tentativas anteriores foi somado à latência de cada caso.

Referência: [LangChain, saída estruturada com Gemini](https://reference.langchain.com/python/langchain-google-genai/chat_models/ChatGoogleGenerativeAI/with_structured_output).

## 3. Resultados e confronto com a Sprint 03

Modelo do agente: gemini-3.5-flash-lite. Modelo do juiz: gemini-3.5-flash-lite. Repetições: 1. Registro: 23/10/2026, 17:30 UTC. Foram usados os parâmetros padrão do provedor.

Classificação: empate. O resultado considera a média das quatro métricas e exige que todos os casos tenham sido avaliados. Notas finais: versão atual 1,000; sem guardião 1,000; diferença 0,000. As duas versões tiveram o mesmo desempenho nas métricas de qualidade. O projeto mantém o guardião de escopo como uma camada de controle, mas os resultados desta bateria não demonstram vantagem dele na nota final.

Na Sprint 03, a avaliação manual classificou os testes como adequados. Nesta execução, a versão atual obteve correção média de 1,000. O resultado concorda com a avaliação anterior nos cenários medidos.

O avaliador mudou a nota ou a decisão de recusa em 3 registros cujas respostas permaneceram iguais. No caso F03 sem guardião, a primeira avaliação apontou uma ambiguidade sobre o processamento do pagamento; a segunda aceitou a mesma resposta. Em B02, mudou a interpretação da recusa. Essa variação limita a confiança nas notas máximas e justifica a análise das justificativas junto dos valores da tabela.

O teste de memória recuperou Solar Park e 12 vagas nas duas versões após a retomada da chamada com erro. O empate e as mudanças de parecer do juiz não sustentam uma conclusão de melhora na qualidade. Também faltam medições históricas equivalentes para atribuir uma redução de latência à nova arquitetura.

| Métrica | Sprint 03 atual | Variação sem guardião |
|---|---|---|
| Correção | 1,000 | 1,000 |
| Aderência ao escopo | 1,000 | 1,000 |
| Fidelidade ao contexto | 1,000 | 1,000 |
| Adequação da recusa | 1,000 | 1,000 |
| Taxa de recusa correta | 1,000 | 1,000 |
| Nota final | 1,000 | 1,000 |
| Cobertura válida | 1,000 | 1,000 |
| Latência média por caso (s) | 24,223 | 32,993 |

## 4. Limitações

O uso do mesmo modelo para gerar e avaliar respostas pode introduzir viés. Além disso, o avaliador pode ser influenciado pelo conteúdo recebido. O prompt orienta o juiz a tratar os diálogos como dados, mas essa medida não elimina o risco de manipulação.

O conjunto de 8 casos cobre apenas parte da operação de um eletroposto. A comparação foi feita em uma única repetição e altera somente o guardião de escopo. Portanto, não permite generalizar o resultado para toda a aplicação ou concluir que ela supera a Sprint 02.

A quota da API limitou o tamanho da bateria. O modo econômico utiliza 20 turnos de conversa e uma avaliação em lote, além das chamadas de retomada quando há erro. A latência também foi afetada pela rede e pela espera entre requisições.

## 5. Divisão de responsabilidades da equipe

Curso e turma: Ciência da Computação, 1º ano. Responsabilidades organizadas por disciplina.

Mateus de Oliveira Fernandes Neves - RM 572431: Data Structures and Algorithms.

Angela Sousa Takezawa - RM 570797: Prompt and Artificial Intelligence.

Pedro Soares de Souza - RM 571285: Modelagem Matemática e Computacional.

Paulo Henrique Lira Bilac de Araújo - RM 569496: Computer Organization and Architecture / Computer Science.

Olavo Dadario Vianna Barreto - RM 569272: Pensamento Computacional e Automação com Python / Soluções em Energias Renováveis e Sustentáveis.

John Cutile Titirico - RM 571976: Modelagem Linear para Aprendizado de Máquina.

Código, dataset e registros da avaliação: https://github.com/woowoo88/SPRINT4_IA.

## Configuração registrada
```json
{
  "executado_em_utc": "2026-10-23T17:26:52.028350+00:00",
  "dataset_sha256": "bb789f5adb863af6e9f1a4c089547a063bf254da1eedb3cf4d7525d2b5388f19",
  "dataset_arquivo": "golden_dataset_avaliado.json",
  "modelo_agente": "gemini-3.5-flash-lite",
  "modelo_juiz": "gemini-3.5-flash-lite",
  "python": "3.14.4",
  "langchain_google_genai": "4.4.0",
  "repeticoes": 1,
  "casos_por_versao": 8,
  "juiz_em_lote": true,
  "limite_chamadas_por_minuto": 8,
  "resumo": {
    "sprint03_atual": {
      "correcao": 1.0,
      "escopo": 1.0,
      "fidelidade": 1.0,
      "adequacao_recusa": 1.0,
      "taxa_recusa_correta": 1.0,
      "score_final": 1.0,
      "cobertura": 1.0,
      "casos_validos": 8,
      "latencia_media_s": 24.223,
      "correcao_por_categoria": {
        "borda": 1.0,
        "escopo": 1.0,
        "funcionalidade": 1.0,
        "memoria": 1.0,
        "seguranca": 1.0
      }
    },
    "variacao_sem_guardiao": {
      "correcao": 1.0,
      "escopo": 1.0,
      "fidelidade": 1.0,
      "adequacao_recusa": 1.0,
      "taxa_recusa_correta": 1.0,
      "score_final": 1.0,
      "cobertura": 1.0,
      "casos_validos": 8,
      "latencia_media_s": 32.993375,
      "correcao_por_categoria": {
        "borda": 1.0,
        "escopo": 1.0,
        "funcionalidade": 1.0,
        "memoria": 1.0,
        "seguranca": 1.0
      }
    }
  },
  "classificacao": "empate",
  "status": "completo",
  "retomada_em_utc": "2026-10-23T17:30:11.888410+00:00",
  "politica_retentativa": "Repetir apenas erros técnicos; respostas válidas não são regeneradas; juiz reavalia todo o lote."
}
```