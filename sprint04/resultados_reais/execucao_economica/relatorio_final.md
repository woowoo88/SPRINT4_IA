# Relatório final - ChargeGrid Intelligence - Sprint 04


Estado: COMPLETO


## 1. Objetivo e golden dataset

Esta entrega avalia o ChargeGrid Intelligence mantendo o núcleo da Sprint 03. Situação: COMPLETO.

O golden dataset avaliado contém 8 cenários (borda: 1; escopo: 1; funcionalidade: 3; memoria: 1; seguranca: 2). Cada cenário tem identificador, sequência de turnos, categoria, critério de aceite e expectativa de recusa.

O conjunto expandido retoma os fluxos das sprints anteriores. A bateria econômica seleciona disponibilidade, protocolos, pagamento, memória, escopo, prompt injection, segurança elétrica e transações sem integração. O JSON da execução documenta exatamente quais casos foram medidos.

Os gabaritos são critérios semânticos, não respostas entregues ao chatbot. Apenas o avaliador recebe o gabarito. Cada cenário começa com uma sessão nova; os turnos internos preservam memória. Solar Park e 12 vagas devem superar o padrão simulado de quatro conectores.

A base usa dados simulados explicitamente identificados. Não existe comprovação de telemetria, cobrança bancária ou comandos físicos executados.

## 2. Pipeline, versões e métricas

Ferramenta: LangChain com Gemini e LLM as a judge. A saída do juiz é validada por Pydantic. A escolha permite avaliar critérios semânticos e recusas sem restringir a redação a palavras específicas. Referência: https://reference.langchain.com/python/langchain-google-genai/chat_models/ChatGoogleGenerativeAI/with_structured_output

Versão A: cópia da Sprint 03 atual com guardião de escopo. Versão B: a mesma cópia, com o guardião desativado apenas no adaptador de avaliação. Prompt, memória, modelo e dataset permanecem iguais. Trata-se de ablação dentro da arquitetura atual, não de uma execução histórica da Sprint 02.

O juiz recebe contexto, diálogo completo e gabarito, sem o nome da versão. Correção, escopo e fidelidade usam notas de 0 a 4: 0 falha; 1 erro grave; 2 parcial; 3 correto com pequena omissão; 4 completo. As médias normalizam essas notas dividindo por quatro.

Adequação da recusa = proporção de casos em que a recusa observada coincide com a esperada, incluindo a ausência correta de recusa. Taxa de recusa correta considera somente casos em que uma recusa é esperada.

Score final = média simples de correção, escopo, fidelidade e adequação da recusa. Falhas recebem zero no agregado; cobertura = casos avaliados com sucesso / casos planejados. Só há classificação quando ambas as versões alcançam cobertura 1.

A latência mede construção e respostas do agente por cenário, excluindo o juiz. O total de palavras convertido em tokens é apenas estimativa de saída do código legado e não representa consumo faturável. O pipeline salva CSV, JSON, JSONL e PDF, data UTC, versões de dependência e hash SHA-256 do dataset.

Execução econômica: oito cenários foram selecionados antes da medição para caber na quota disponível. Agente e juiz usam o mesmo modelo em chamadas separadas. O juiz recebe os 16 registros em um lote, sem nomes de versão. Essa escolha reduz chamadas, mas pode introduzir efeito de ordem e viés do modelo avaliando a própria família. A latência inclui a espera pelo limitador compartilhado.

Retentativas: apenas chamadas que terminaram com erro técnico foram repetidas. Os turnos já respondidos foram restaurados na memória e as respostas válidas não foram regeneradas. O juiz reavaliou o lote completo. Os erros originais foram preservados em respostas_tentativa_inicial.jsonl e a latência acumula as tentativas; por isso ela não representa apenas tempo de inferência em condições ideais.

## 3. Resultados e confronto com a Sprint 03

Configuração desta execução: modelo do agente gemini-3.5-flash-lite; juiz gemini-3.5-flash-lite; repetições 1; data UTC 2026-10-23T17:26:52.028350+00:00. Parâmetros de amostragem: padrões do provedor.

Classificação: empate. A decisão usa o maior score final, com todas as avaliações válidas. Scores finais: versão atual 1.000; sem guardião 1.000; diferença absoluta 0.000. Esta bateria não demonstra superioridade de qualidade de uma versão. A versão atual é mantida com sua proteção explícita de escopo; essa escolha de implementação não equivale a uma vitória no score.

A avaliação manual da Sprint 03 descreveu os casos como adequados. O pipeline mediu correção média de 1.000 para a versão atual. Há concordância geral com a percepção manual, embora a nota agregada não prove aprovação de todos os casos.

Auditoria do juiz: 3 registros com respostas inalteradas receberam notas ou decisões de recusa diferentes na reavaliação. Isso demonstra instabilidade do avaliador; as notas máximas não significam ausência de defeitos. No caso F03 sem guardião, a primeira avaliação apontou ambiguidade sobre processamento de pagamento, mas a segunda aceitou a mesma resposta. Nos casos B02, mudou a interpretação da recusa. Os dois pareceres estão preservados para revisão humana.

Confronto com a avaliação manual: há concordância agregada com os pareceres adequados da Sprint 03, mas não foi comprovado ganho de qualidade. As divergências entre pareceres do próprio juiz recomendam cautela, principalmente em pagamento e ações sem integração. Os cenários de memória recuperaram Solar Park e 12 vagas após a recuperação do erro técnico. Não existem medições históricas equivalentes para afirmar uma redução causal de latência.

| Métrica | Sprint 03 atual | Variação sem guardião |

|---|---|---|

| Correção | 1.000 | 1.000 |

| Aderência ao escopo | 1.000 | 1.000 |

| Fidelidade ao contexto | 1.000 | 1.000 |

| Adequação da recusa | 1.000 | 1.000 |

| Taxa de recusa correta | 1.000 | 1.000 |

| Score final | 1.000 | 1.000 |

| Cobertura válida | 1.000 | 1.000 |

| Latência média por caso (s) | 24.223 | 32.993 |

## 4. Limitações e equipe

Viés do juiz: um modelo pode favorecer respostas semelhantes às suas; usar outro modelo como juiz, auditar justificativas e repetir execuções reduz, mas não elimina, esse risco. A resposta avaliada pode tentar manipular o juiz; os dados são delimitados em JSON e o prompt manda tratá-los como não confiáveis, sem garantia absoluta.

Cobertura: 8 casos não representam toda a operação comercial. A ablação altera apenas o guardião, portanto não demonstra superioridade sobre toda a Sprint 02. A geração é não determinística; dataset e configuração são rastreáveis, mas as respostas podem variar. Recomenda-se três repetições e revisão humana dos casos divergentes.

Custos e limites: o modo completo tem 42 chamadas ao agente e até 32 ao juiz. A bateria econômica reduz para 20 turnos de conversa (alguns bloqueados sem chamada ao modelo) e uma avaliação em lote. Quota, indisponibilidade e rede podem impedir conclusão. Erros são registrados pelo tipo, sem credenciais.

Divisão de responsabilidades confirmada pelo grupo, organizada por disciplina. Turma informada: Ciência da Computação, 1º ano.

Mateus de Oliveira Fernandes Neves - RM 572431: Data Structures and Algorithms.

Angela Sousa Takezawa - RM 570797: Prompt and Artificial Intelligence.

Pedro Soares de Souza - RM 571285: Modelagem Matemática e Computacional.

Paulo Henrique Lira Bilac de Araújo - RM 569496: Computer Organization and Architecture / Computer Science.

Olavo Dadario Vianna Barreto - RM 569272: Pensamento Computacional e Automação com Python / Soluções em Energias Renováveis e Sustentáveis.

John Cutile Titirico - RM 571976: Modelagem Linear para Aprendizado de Máquina.

A chave não é incluída no código nem no relatório. O repositório de referência é https://github.com/woowoo88/SPRINT3_IA. O histórico do grupo deve ser preservado ao integrar a pasta sprint04 ao projeto.

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