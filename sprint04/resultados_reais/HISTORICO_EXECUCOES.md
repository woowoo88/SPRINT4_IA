# Histórico das execuções reais

As tentativas abaixo utilizaram a credencial fornecida no ambiente de execução, sem incluí-la nos arquivos.

1. `execucao_01`: agente Gemini 3.6 Flash e juiz Gemini 3.7 Flash. A tentativa foi interrompida após falha do avaliador; a chamada direta ao 3.7 Flash também excedeu o tempo limite. Não foi emitida classificação.
2. `execucao_final`: agente e juiz Gemini 3.6 Flash, em chamadas separadas. Houve respostas válidas e erros `GoogleRateLimitError`; a execução foi interrompida para diagnosticar a quota. Não foi emitida classificação.
3. `execucao_controlada`: mesma configuração, com limitador compartilhado de oito chamadas por minuto. O provedor confirmou HTTP 429 por limite diário gratuito de 20 chamadas ao Gemini 3.6 Flash, não apenas frequência por minuto. A tentativa foi interrompida; as falhas não foram tratadas como respostas corretas.
4. `execucao_economica`: Gemini 3.5 Flash-Lite nas duas versões e no juiz em chamada separada. O conjunto de oito casos foi selecionado antes desta execução, cobrindo as cinco categorias. A primeira passagem apresentou três erros de API na versão sem guardião. Somente os turnos com erro foram retomados, restaurando os turnos prévios sem novas chamadas e sem regenerar respostas válidas. O juiz reavaliou todo o lote. A cobertura final é de 100%, com empate no score de 1,000 em ambas as versões. Foram observadas mudanças de parecer em três registros com respostas inalteradas, documentadas como limitação do avaliador. A primeira passagem permanece em `respostas_tentativa_inicial.jsonl`.

As tentativas anteriores estão preservadas para rastreabilidade. A tabela da entrega usa exclusivamente a bateria econômica, sem misturar notas, modelos ou respostas das tentativas interrompidas. Os dados operacionais do ChargeGrid continuam simulados; as chamadas e avaliações do Gemini são reais.
