# Validação local

Data: 23/10/2026.

Foram aprovados cinco testes automatizados de infraestrutura:

1. Dataset com 16 IDs exclusivos, cinco categorias e memória em três turnos.
2. Rejeição de notas do juiz fora do intervalo 0 a 4.
3. Manutenção de falhas no denominador das métricas.
4. Execução das duas variações com dublês, totalizando 32 avaliações e 42 turnos, com exportação de JSONL, CSV e PDF.
5. Execução com falhas simuladas, sem vencedor e sem gravação da mensagem bruta da exceção.

O construtor real do conector Gemini e a saída estruturada do juiz também foram validados sem chamada de geração. O notebook é JSON válido no formato Jupyter 4. As quatro páginas do PDF metodológico foram renderizadas e revisadas visualmente.

Esses testes não comprovam desempenho semântico do agente nem substituem a avaliação real no Gemini. Nenhum resultado de dublê foi incorporado à tabela final como resultado real.
