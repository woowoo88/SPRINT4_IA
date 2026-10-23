# Sprint 04 - Pipeline de avaliação ChargeGrid

O pipeline mede o desempenho do ChargeGrid Intelligence e compara a versão atual com uma variação sem o guardião de escopo. O código de avaliação está em `sprint04`; a aplicação continua em `chargegrid_intelligence`.

## Execução

Para contas com quota reduzida, o modo econômico usa oito cenários e um juiz em lote, mantendo as cinco categorias do conjunto expandido:

```bash
python -m sprint04.avaliar_economico --modelo gemini-3.5-flash-lite --saida resultados/economico
```

As duas versões e o juiz usam o mesmo modelo em chamadas separadas. Esse modo utiliza até 21 chamadas por bateria antes de retentativas: 20 turnos de conversa e uma avaliação em lote. Regras locais podem reduzir esse total. O limitador permite oito chamadas por minuto, mas a execução também depende da quota diária do projeto.

No [notebook do Colab](https://colab.research.google.com/github/woowoo88/SPRINT3_IA/blob/main/Executar_Sprint04.ipynb), execute as células em ordem. A chave é lida por Colab Secrets ou entrada oculta. Os modelos são definidos antes da avaliação e registrados nos resultados.

Localmente, com Python 3.10 ou superior e chave configurada em `GOOGLE_API_KEY` ou `.env`:

```bash
pip install -r requirements-sprint04.txt
python -m sprint04.avaliar --modelo SEU_MODELO --juiz MODELO_JUIZ --repeticoes 1
python -m unittest sprint04.test_pipeline sprint04.test_economico sprint04.test_retomada -v
```

Para reduzir o efeito de variações nas respostas, considere três repetições. Cada repetição envolve 32 avaliações, até 42 chamadas de conversa e até 32 chamadas ao juiz. As chamadas podem consumir quota ou créditos do provedor.

## Dataset e versões

O `golden_dataset.json` contém 16 cenários: cinco funcionais, dois de memória em três turnos, dois de escopo, cinco de segurança e dois de borda. Cada caso possui gabarito semântico e expectativa de recusa. O gabarito é enviado apenas ao juiz.

São comparadas duas variações da Sprint 03: `sprint03_atual` e `variacao_sem_guardiao`. A segunda desativa o guardião no adaptador de teste. Modelo, prompt e memória são mantidos. Cada cenário usa uma sessão independente e preserva o histórico entre seus turnos.

## Métricas e resultados

O juiz recebe diálogo completo, contexto e gabarito, sem conhecer o nome da versão. Correção, escopo e fidelidade recebem notas de 0 a 4, normalizadas para 0 a 1. A adequação da recusa compara a recusa observada com a esperada. O score final é a média dessas quatro métricas. Também são calculadas taxa de recusa correta, cobertura, correção por categoria e latência por cenário.

Falhas contam como zero no agregado e reduzem a cobertura. Não há vencedor enquanto as duas versões não concluírem todas as avaliações. O pipeline exporta `respostas.jsonl`, `resumo.json`, `notas.csv`, `relatorio_final.md` e `relatorio_final.pdf` em `resultados/<data-hora>/`. Tokens de saída são estimados; não representam consumo faturável.

## Resultados registrados

Os resultados estão em `resultados_reais/execucao_economica/`. Foram avaliados oito cenários por versão com Gemini 3.5 Flash-Lite. Após a retomada de três falhas técnicas, a cobertura chegou a 100% e a nota final foi 1,000 nas duas versões. O relatório analisa o empate e as mudanças de parecer do juiz.

Oito testes automatizados verificam o funcionamento do pipeline sem consumir a API. Os resultados desses testes estão descritos em `VALIDACAO_LOCAL.md`. O arquivo `avaliacao_manual_sprint03.md` contém a avaliação qualitativa anterior, e `proveniencia.json` registra a versão do projeto usada como base.

Para retomar apenas turnos com falha técnica, com a chave configurada no ambiente:

```python
from pathlib import Path
from sprint04.retomar_falhas import retomar
retomar(Path('resultados/sua_execucao'))
```

O procedimento preserva a tentativa inicial, restaura os turnos anteriores e não regenera respostas válidas. Depois, reavalia todo o lote. O histórico das tentativas reais está em `resultados_reais/HISTORICO_EXECUCOES.md`.

Referência técnica: [saída estruturada Gemini no LangChain](https://reference.langchain.com/python/langchain-google-genai/chat_models/ChatGoogleGenerativeAI/with_structured_output).
