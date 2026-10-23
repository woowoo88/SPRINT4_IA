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

O construtor real do conector Gemini e a saída estruturada do juiz também foram validados sem chamada de geração. O notebook é JSON válido no formato Jupyter 4. As quatro páginas do PDF metodológico foram renderizadas e revisadas visualmente.

Esses testes não substituem a avaliação semântica real, concluída em `resultados_reais/execucao_economica/`. Nenhum resultado de dublê foi incorporado à tabela final como resultado real. A execução utilizou Gemini 3.5 Flash-Lite, oito cenários por versão e uma retomada de três falhas técnicas. A cobertura final foi de 100%, com empate no score de 1,000.
