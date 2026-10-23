# Entrega Sprint 03 - ChargeGrid Intelligence

Documentação da Sprint 03, mantida como registro da evolução do projeto. A avaliação e o relatório final da Sprint 04 estão em `sprint04/resultados_reais/execucao_economica/`.

## Repositório

https://github.com/woowoo88/SPRINT3_IA

## Projeto

ChargeGrid Intelligence é uma aplicação acadêmica de agentes de IA para o EV Challenge GoodWe/FIAP. A solução apoia o gerenciamento comercial de recarga veicular, com respostas sobre vagas, conectores, sessões de recarga, demanda, cobrança dinâmica, pagamento, OCPP, MODBUS e relatórios operacionais.

## Arquivos da entrega

- `guia_execucao.md`: instruções para executar o agente no Google Colab e localmente.
- `relatorio_modelos.md`: comparação entre modelos/configurações avaliadas.
- `casos_de_teste.md`: testes funcionais, testes de memória e testes de segurança.
- `relatorio_evolucao.md`: versão em Markdown do relatório de evolução.
- `relatorio_evolucao.pdf`: relatório de evolução em PDF, com até 5 páginas.
- `identificacao_integrantes.txt`: identificação dos integrantes do grupo.

## Agentes implementados

- `ChargeGridAgent`: agente principal de conversa. Ele usa LangChain, envia o contexto interno ao modelo Gemini, mantém memória por sessão e retorna a resposta final ao usuário.
- `ScopeGuardAgent`: agente guardião de escopo. Ele avalia a pergunta antes da chamada ao modelo e bloqueia temas que não pertencem ao contexto ChargeGrid.

## Tecnologias

- Python
- LangChain
- Google Gemini
- Google Colab
- GitHub

## Segurança

As credenciais não aparecem no código-fonte. A chave do Gemini deve ser informada apenas no ambiente de execução, por variável de ambiente ou pelo campo seguro do Colab.
