# Relatório final - ChargeGrid Intelligence - Sprint 04


Estado: PENDENTE DE EXECUÇÃO REAL


## 1. Objetivo e golden dataset

Esta entrega avalia o ChargeGrid Intelligence mantendo o núcleo da Sprint 03. Situação: PENDENTE DE EXECUÇÃO REAL.

O golden dataset contém 16 cenários: cinco funcionais, dois de memória, dois de escopo, cinco de segurança e dois de borda. Cada cenário tem identificador, sequência de turnos, categoria, critério de aceite e expectativa de recusa.

Os fluxos funcionais retomam disponibilidade, protocolos, pagamento, relatório e demanda das sprints anteriores. Foram adicionados cálculos, memória, mudança de assunto, instruções maliciosas e pedidos transacionais sem integração.

Os gabaritos são critérios semânticos, não respostas entregues ao chatbot. Apenas o avaliador recebe o gabarito. Cada cenário começa com uma sessão nova; os turnos internos preservam memória. Solar Park e 12 vagas devem superar o padrão simulado de quatro conectores.

A base usa dados simulados explicitamente identificados. Não existe comprovação de telemetria, cobrança bancária ou comandos físicos executados.

## 2. Pipeline, versões e métricas

Ferramenta: LangChain com Gemini e LLM as a judge. A saída do juiz é validada por Pydantic. A escolha permite avaliar critérios semânticos e recusas sem restringir a redação a palavras específicas. Referência: https://reference.langchain.com/python/langchain-google-genai/chat_models/ChatGoogleGenerativeAI/with_structured_output

Versão A: cópia da Sprint 03 atual com guardião de escopo. Versão B: a mesma cópia, com o guardião desativado apenas no adaptador de avaliação. Prompt, memória, modelo e dataset permanecem iguais. Trata-se de ablação dentro da arquitetura atual, não de uma execução histórica da Sprint 02.

O juiz recebe contexto, diálogo completo e gabarito, sem o nome da versão. Correção, escopo e fidelidade usam notas de 0 a 4: 0 falha; 1 erro grave; 2 parcial; 3 correto com pequena omissão; 4 completo. As médias normalizam essas notas dividindo por quatro.

Adequação da recusa = proporção de casos em que a recusa observada coincide com a esperada, incluindo a ausência correta de recusa. Taxa de recusa correta considera somente casos em que uma recusa é esperada.

Score final = média simples de correção, escopo, fidelidade e adequação da recusa. Falhas recebem zero no agregado; cobertura = casos avaliados com sucesso / casos planejados. Só há classificação quando ambas as versões alcançam cobertura 1.

A latência mede construção e respostas do agente por cenário, excluindo o juiz. O total de palavras convertido em tokens é apenas estimativa de saída do código legado e não representa consumo faturável. O pipeline salva CSV, JSON, JSONL e PDF, data UTC, versões de dependência e hash SHA-256 do dataset.

## 3. Resultados e confronto com a Sprint 03

Classificação inconclusiva. Não há duas execuções completas que sustentem a escolha de uma versão vencedora.

O registro manual anterior classifica os casos como adequados, mas não contém logs completos, tempos ou notas numéricas. Ainda não é possível confirmar concordância com o pipeline. Não foram atribuídas notas retrospectivas à Sprint 03.

| Métrica | Sprint 03 atual | Variação sem guardião |

|---|---|---|

| Correção | Não medido | Não medido |

| Aderência ao escopo | Não medido | Não medido |

| Fidelidade ao contexto | Não medido | Não medido |

| Adequação da recusa | Não medido | Não medido |

| Taxa de recusa correta | Não medido | Não medido |

| Score final | Não medido | Não medido |

| Cobertura válida | Não medido | Não medido |

| Latência média por caso (s) | Não medido | Não medido |

## 4. Limitações e equipe

Viés do juiz: um modelo pode favorecer respostas semelhantes às suas; usar outro modelo como juiz, auditar justificativas e repetir execuções reduz, mas não elimina, esse risco. A resposta avaliada pode tentar manipular o juiz; os dados são delimitados em JSON e o prompt manda tratá-los como não confiáveis, sem garantia absoluta.

Cobertura: 16 casos não representam toda a operação comercial. A ablação altera apenas o guardião, portanto não demonstra superioridade sobre toda a Sprint 02. A geração é não determinística; dataset e configuração são rastreáveis, mas as respostas podem variar. Recomenda-se três repetições e revisão humana dos casos divergentes.

Custos e limites: uma execução envolve 42 chamadas ao agente e até 32 ao juiz, com repetições adicionais multiplicando esses valores. Alguns casos bloqueados não chegam ao modelo. Quota, indisponibilidade e rede podem impedir conclusão. Erros são registrados pelo tipo, sem credenciais.

O material anterior informa nomes, RMs e matérias por integrante, mas não comprova divisão individual das tarefas da Sprint 04. Para preservar a integridade, as atribuições abaixo permanecem a confirmar pelo grupo.

Mateus de Oliveira Fernandes Neves - RM 572431; Angela Sousa Takezawa - RM 570797; Pedro Soares de Souza - RM 571285; Paulo Henrique Lira Bilac de Araújo - RM 569496; Olavo Dadario Vianna Barreto - RM 569272; Jhon - RM 571976. Nome completo do Jhon, código da turma e tarefas efetivamente realizadas na Sprint 04 devem ser confirmados.

A chave não é incluída no código nem no relatório. O repositório de referência é https://github.com/woowoo88/SPRINT3_IA. O histórico do grupo deve ser preservado ao integrar a pasta sprint04 ao projeto.