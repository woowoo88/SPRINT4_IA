# Guia de Execução - ChargeGrid Intelligence

## Execução no Google Colab

Abra um notebook novo no Google Colab e execute as células abaixo.

### 1. Instalação

```python
%cd /content
!rm -rf SPRINT4_IA
%pip uninstall -y chargegrid-intelligence

!git clone https://github.com/woowoo88/SPRINT4_IA.git
%cd SPRINT4_IA

%pip install -q -r requirements.txt
```

### 2. Configuração da chave Gemini

```python
import os
from getpass import getpass

os.environ.pop("GEMINI_API_KEY", None)
os.environ["GOOGLE_API_KEY"] = getpass("Cole sua chave Gemini: ")
os.environ["GEMINI_MODEL"] = "gemini-3.6-flash"
```

A chave deve ser colada apenas quando o Colab solicitar. Ela não deve ser enviada ao GitHub nem escrita diretamente no código.

### 3. Execução em modo conversa contínua

```python
!python chat_colab.py
```

Depois disso, o usuário pode fazer várias perguntas na mesma sessão:

```text
Usuário: Quantas vagas temos disponíveis?
ChargeGrid: ...

Usuário: Quais conectores estão livres?
ChargeGrid: ...

Usuário: Como funciona o pagamento?
ChargeGrid: ...
```

Para encerrar a conversa, digite:

```text
sair
```

## Execução local

Crie um arquivo `.env` com base no `.env.example`:

```env
GOOGLE_API_KEY=sua-chave-aqui
GEMINI_MODEL=gemini-3.6-flash
```

Depois execute:

```bash
pip install -r requirements.txt
python chat_colab.py
```

## Observações

- O agente usa dados simulados para o protótipo acadêmico.
- O contexto do ChargeGrid é enviado automaticamente ao modelo.
- A resposta final não exibe chaves, variáveis de ambiente, caminhos locais ou detalhes internos.
- O `ScopeGuardAgent` bloqueia perguntas que não pertencem ao contexto ChargeGrid.
