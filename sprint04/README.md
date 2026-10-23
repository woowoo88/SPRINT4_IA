# Sprint 04 - Pipeline de avaliação ChargeGrid

Esta sprint acrescenta avaliação sistemática ao código existente. O agente conversacional permanece no pacote `chargegrid_intelligence`; o pipeline fica em `sprint04`.

## Execução

Abra o notebook [Executar_Sprint04.ipynb no Colab](https://colab.research.google.com/github/woowoo88/SPRINT3_IA/blob/main/Executar_Sprint04.ipynb) e execute as células em ordem. A chave é lida por Colab Secrets ou entrada oculta. Informe IDs de modelo disponíveis em sua conta; nenhum modelo é substituído silenciosamente.

Localmente, com Python 3.10 ou superior e chave configurada em `GOOGLE_API_KEY` ou `.env`:

```bash
pip install -r requirements-sprint04.txt
python -m sprint04.avaliar --modelo SEU_MODELO --juiz MODELO_JUIZ --repeticoes 1
python -m unittest sprint04.test_pipeline -v
```

Para reduzir o efeito de variações nas respostas, considere três repetições. Cada repetição envolve 32 avaliações, até 42 chamadas de conversa e até 32 chamadas ao juiz. As chamadas podem consumir quota ou créditos do provedor.

## Dataset e versões

O `golden_dataset.json` contém 16 cenários: cinco funcionais, dois de memória em três turnos, dois de escopo, cinco de segurança e dois de borda. Cada caso possui gabarito semântico e expectativa de recusa. O gabarito é enviado apenas ao juiz.

São comparadas duas variações da mesma aplicação: `sprint03_atual` e `variacao_sem_guardiao`. A segunda desativa o guardião apenas no adaptador de avaliação; modelo, prompt e memória permanecem iguais. Não se trata de uma execução histórica da Sprint 02. Cada cenário tem uma sessão isolada, preservando a sequência de turnos interna.

## Métricas e resultados

O juiz recebe diálogo completo, contexto e gabarito, sem conhecer o nome da versão. Correção, escopo e fidelidade recebem notas de 0 a 4, normalizadas para 0 a 1. A adequação da recusa compara a recusa observada com a esperada. O score final é a média dessas quatro métricas. Também são calculadas taxa de recusa correta, cobertura, correção por categoria e latência por cenário.

Falhas contam como zero no agregado e reduzem a cobertura. Não há vencedor enquanto as duas versões não concluírem todas as avaliações. O pipeline exporta `respostas.jsonl`, `resumo.json`, `notas.csv`, `relatorio_final.md` e `relatorio_final.pdf` em `resultados/<data-hora>/`. Tokens de saída são estimados; não representam consumo faturável.

## Evidências e pendências

Os cinco testes de infraestrutura foram aprovados, conforme `VALIDACAO_LOCAL.md`. Os dublês são exclusivos dos testes e não fornecem notas reais do agente. Não havia chave Gemini neste ambiente, portanto o relatório em `relatorio_metodologico/` está marcado como pendente de execução real.

`avaliacao_manual_sprint03.md` preserva o registro qualitativo anterior para confronto, sem tratá-lo como comprovação quantitativa. `proveniencia.json` identifica a base copiada. Após a execução real, revise as justificativas do juiz e entregue o PDF consolidado junto do link deste repositório e do arquivo de identificação dos integrantes. Confirme nome completo do Jhon, código da turma e divisão efetiva das tarefas desta sprint.

Referência técnica: [saída estruturada Gemini no LangChain](https://reference.langchain.com/python/langchain-google-genai/chat_models/ChatGoogleGenerativeAI/with_structured_output).
