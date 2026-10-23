# Validação local

Data: 23/10/2026.

Foram aprovados oito testes automatizados de infraestrutura:

1. Dataset com 16 IDs exclusivos, cinco categorias e memória em três turnos.
2. Rejeição de notas do juiz fora do intervalo 0 a 4.
3. Manutenção de falhas no denominador das métricas.
4. Execução das duas variações com dublês, totalizando 32 avaliações e 42 turnos, com exportação de JSONL, CSV e PDF.
5. Execução com falhas simuladas, sem vencedor e sem gravação da mensagem bruta da exceção.
6. Avaliação econômica com oito cenários e julgamento em lote de ambas as versões.
7. Rejeição de lote do juiz com identificadores ausentes.
8. Retomada exclusiva do turno com erro, preservando histórico e a tentativa original.

Os testes usam respostas simuladas para verificar o encadeamento do pipeline, os cálculos e o tratamento de falhas. As notas do relatório vêm de uma execução separada com Gemini, registrada em `resultados_reais/execucao_economica/`.

Essa execução utilizou Gemini 3.5 Flash-Lite em oito cenários por versão. Três falhas técnicas foram retomadas. A cobertura final foi de 100%, com empate na nota de 1,000.
