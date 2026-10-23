# Sprint 04 - Pipeline de avaliação ChargeGrid

Esta sprint acrescenta avaliação sistemática ao código existente. O agente conversacional permanece no pacote `chargegrid_intelligence`; o pipeline fica em `sprint04`.

## Execução

Para contas com quota reduzida, o modo econômico usa oito cenários e um juiz em lote, mantendo as cinco categorias do conjunto expandido:

```bash
python -m sprint04.avaliar_economico --modelo gemini-3.5-flash-lite --saida resultados/economico
```

O mesmo modelo é utilizado em ambas as versões e em uma chamada separada de avaliação. Esse modo usa até 18 chamadas ao modelo por bateria. Ele não contorna limites diários: se a quota do projeto acabar, é preciso aguardar a renovação ou ajustar o plano no provedor. O controle de ritmo do modo completo limita as chamadas a oito por minuto por padrão.

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

Os oito testes de infraestrutura foram aprovados. Os dublês são exclusivos dos testes e não fornecem notas reais do agente. A avaliação real está concluída em `resultados_reais/execucao_economica/`: oito cenários por versão, Gemini 3.5 Flash-Lite, cobertura final de 100% e empate no score (1,000). Consulte o PDF, os diálogos e as justificativas; o relatório registra a instabilidade do juiz e as retentativas técnicas. O documento em `relatorio_metodologico/` é uma versão histórica anterior à execução.

`avaliacao_manual_sprint03.md` preserva o registro qualitativo anterior para confronto, sem tratá-lo como comprovação quantitativa. `proveniencia.json` identifica a base. O relatório final inclui John Cutile Titirico (RM 571976) e a divisão por matérias confirmada pelo grupo. A turma foi informada como Ciência da Computação, 1º ano. A chave não integra o código ou os arquivos de entrega.

Para retomar apenas turnos com falha técnica, com a chave configurada no ambiente:

```python
from pathlib import Path
from sprint04.retomar_falhas import retomar
retomar(Path('resultados/sua_execucao'))
```

O procedimento preserva a tentativa inicial, restaura os turnos anteriores e não regenera respostas válidas. Depois, reavalia todo o lote. O histórico das tentativas reais está em `resultados_reais/HISTORICO_EXECUCOES.md`.

Referência técnica: [saída estruturada Gemini no LangChain](https://reference.langchain.com/python/langchain-google-genai/chat_models/ChatGoogleGenerativeAI/with_structured_output).
