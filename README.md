# ChargeGrid Intelligence

Projeto do EV Challenge GoodWe/FIAP para apoiar a operação comercial de eletropostos. O chatbot usa LangChain e Gemini para responder dúvidas sobre vagas, conectores, sessões de recarga, demanda, tarifas, pagamento, OCPP e MODBUS.

Os dados de operação são simulados. O projeto não está conectado a carregadores, sensores ou serviços de pagamento.

## Sprint 04: avaliação do chatbot

A Sprint 04 acrescenta um pipeline de avaliação com gabaritos, notas por critério e comparação entre duas versões: a aplicação atual e uma variação com o guardião de escopo desativado.

O conjunto expandido tem 16 cenários. A execução registrada utilizou oito deles por versão, cobrindo funcionalidade, memória, escopo, segurança e casos de borda. O modelo utilizado foi o Gemini 3.5 Flash-Lite.

| Métrica | Versão atual | Sem guardião |
|---|---:|---:|
| Nota final | 1,000 | 1,000 |
| Cobertura final | 100% | 100% |
| Latência média por cenário | 24,223 s | 32,993 s |

Houve empate na nota final. A latência inclui espera entre chamadas e tentativas após falhas técnicas. O juiz também mudou três pareceres sobre respostas inalteradas, uma limitação discutida no relatório.

- [Relatório final em PDF](sprint04/resultados_reais/execucao_economica/relatorio_final.pdf)
- [Dataset, respostas, notas e configuração da execução](sprint04/resultados_reais/execucao_economica/)
- [Metodologia e comandos da avaliação](sprint04/README.md)
- [Identificação dos integrantes](entregaveis/identificacao_integrantes.txt)

## Executar no Google Colab

[Abrir o notebook da Sprint 04](https://colab.research.google.com/github/woowoo88/SPRINT3_IA/blob/main/Executar_Sprint04.ipynb)

Execute as células na ordem. O notebook clona o repositório, instala as dependências e lê a chave por Colab Secrets ou entrada oculta. O modo econômico avalia oito cenários por versão; o modo completo usa os 16 cenários. Ao final, o notebook oferece o download dos resultados e do relatório.

Para conversar com o agente após a instalação e a configuração da chave, execute outra célula:

```python
%run chat_colab.py
```

A conversa mantém a mesma sessão entre perguntas. Digite `sair` para encerrar.

## Executar localmente

Requer Python 3.10 ou superior. Configure um ambiente virtual e instale as dependências da avaliação:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements-sprint04.txt
```

Crie um arquivo `.env`, usando `.env.example` como referência:

```env
GOOGLE_API_KEY=sua-chave
GEMINI_MODEL=gemini-3.5-flash-lite
```

O `.env` está no `.gitignore`. A chave não deve ser incluída no código nem nos arquivos de resultados.

Para conversar:

```bash
python chat_colab.py
```

Para executar a avaliação econômica:

```bash
python -m sprint04.avaliar_economico --modelo gemini-3.5-flash-lite --saida resultados/economico
```

Para rodar os testes de infraestrutura, que não consomem a API:

```bash
python -m unittest sprint04.test_pipeline sprint04.test_economico sprint04.test_retomada -v
```

As chamadas ao Gemini dependem da quota e dos modelos disponíveis no projeto do Google.

## Organização

- `chargegrid_intelligence/`: agente conversacional, memória, contexto e regras de segurança.
- `chat_colab.py`: entrada para a conversa contínua.
- `sprint04/`: dataset, avaliação, retomada de falhas e geração do relatório.
- `sprint04/resultados_reais/`: registros das execuções e resultados finais.
- `entregaveis/`: documentação da Sprint 03 e identificação dos integrantes.

O `ChargeGridAgent` monta o contexto e o histórico da sessão antes de consultar o Gemini. O `ScopeGuardAgent` aplica regras locais de escopo e segurança; ele não realiza uma segunda chamada a um modelo de linguagem.
