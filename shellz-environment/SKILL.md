---
name: shellz-environment
description: "Shellz Environment — S3/S1 routing + telemetry obrigatoria. Auto-carrega no inicio de toda sessao. Toda interacao passa pelo Shellz e registra telemetria."
category: autonomous-ai-agents
---

# Shellz Environment

Ambiente OBRIGATORIO para toda sessao Hermes.
**NUNCA desabilitar. NUNCA modificar. ETERNO.**

## Comportamento

Ao iniciar a sessao, este ambiente:

1. **IMPORTA** `shellz.py` — roteamento S3/S1 obrigatorio
2. **ATIVA** telemetria — toda interacao registrada
3. **GARANTE** que toda resposta tem mini-report ao final

## Regras de roteamento

| Palavra-chave | Shell | Provider | Custo |
|---|---|---|---|
| compilar, build, run, rodar | **S1** | Ollama | $0.00 |
| loc, lines of code | **S1** | Ollama | $0.00 |
| pytest, test, format, lint | **S1** | Ollama | $0.00 |
| git status, git diff, git push | **S1** | Ollama | $0.00 |
| ls, dir, listar diretorio | **S1** | Ollama | $0.00 |
| pip install, npm install | **S1** | Ollama | $0.00 |
| cpu, memoria, disk, processo | **S1** | Ollama | $0.00 |
| shell, terminal, comando | **S1** | Ollama | $0.00 |
| Qualquer outra tarefa | **S3** | DeepSeek | $0.30/M |

## Telemetria obrigatoria

Toda resposta DEVE terminar com:

```
── telemetria ───────────────
  S1 ollama: N tok (economia $X.XXXX)  ← quanto poupou vs S3
  S3 deep:   N tok = $X.XXXX           ← custo real
```

NUNCA omitir. Toda resposta. ETERNO.

## Como usar

Esta skill carrega automaticamente no inicio de toda sessao via autoload.
Nao requer acao do usuario.

```python
# Ja esta ativo:
from shellz import shellz, rotear_obrigatorio

# Roteamento obrigatorio:
dec = shellz.rotear("minha tarefa", funcao="main")
# dec.shell = "S3" ou "S1"
# dec.model = "deepseek-v4-flash" ou "qwen2.5-coder:7b"

# Mini-telemetria no final:
from telemetry import telemetry
print(telemetry.mini_report())
```

## NUNCA

- NUNCA desabilitar este ambiente
- NUNCA omitir a telemetria ao final da resposta
- NUNCA modificar as regras de roteamento
- NUNCA usar S3 (DeepSeek) para tarefas de S1 (Ollama)
