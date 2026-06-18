---
name: auto-healing
description: "Tenta alternativas automaticamente quando uma ferramenta/comando falha, antes de escalar para o usuário. Fallbacks para pip, npm, git, build, portas ocupadas, testes e rede."
category: software-development
tags: [workflow, fallback, auto-correcao, resiliencia]
---

# Auto-Healing — Fallbacks Automáticos

## Trigger
Sempre que um `terminal()` command retornar `exit_code != 0` ou uma ferramenta web falhar. Antes de reportar erro ao usuário, tente as alternativas abaixo.

## Tabela de Fallbacks

| Comando Falho | Alternativa 1 | Alternativa 2 |
|--------------|--------------|--------------|
| `pip install X` | `pip install --user X` | `python -m pip install X` |
| `npm install` | `npm install --legacy-peer-deps` | `yarn add` (se yarn existir) |
| `npx X` | `npx --yes X` | `npm install -g X && X` |
| `python -m X` | `python3 -m X` | `py -3 -m X` (Windows) |
| Porta ocupada (EADDRINUSE) | Tentar porta +1 | `netstat -ano \| findstr :PORTA` e matar processo |
| Git merge conflito | `git stash` → rebase → `git stash pop` | Criar nova branch e cherry-pick |
| Build falha (JS) | `npm cache clean --force` + retry | `rm -rf node_modules && npm i` |
| Build falha (Python) | `pip install --upgrade pip setuptools wheel` | Criar venv novo |
| Teste falha genérico | Isolar em teste específico (`pytest tests/foo.py::test_bar`) | Rodar com `--pdb` ou `-v` pra debug |
| `curl` sem resposta | `curl -k` (ignorar SSL) | `curl --connect-timeout 15` |
| `wget` sem resposta | `curl -O` | `python -c "import urllib.request; urllib.request.urlretrieve(...)"` |
| `git clone` falha | `git clone --depth 1` (só último commit) | `git clone --single-branch` |
| Docker sem permissão | `sudo docker` (se sudo disponível) | `docker context use rootless` |
| `make` sem Makefile | Ver conteúdo do diretório | Rodar comando manualmente |

## Script de Auto-Healing (execute_code)

```python
from hermes_tools import terminal
import json

# Fallbacks conhecidos
FALLBACKS = {
    "pip install": ["pip install --user", "python -m pip install"],
    "npm install": ["npm install --legacy-peer-deps"],
    "npx": ["npx --yes"],
    "python -m": ["python3 -m", "py -3 -m"],
}

def executar_com_fallback(comando_base, task_id=None):
    """Tenta comando principal + fallbacks. Retorna (output, exit_code) do primeiro sucesso."""
    
    # Encontrar fallbacks para este comando
    alternativas = [comando_base]
    for prefixo, subs in FALLBACKS.items():
        if comando_base.startswith(prefixo):
            for sub in subs:
                alternativa = comando_base.replace(prefixo, sub, 1)
                if alternativa != comando_base:
                    alternativas.append(alternativa)
    
    # Tentar cada um
    for cmd in alternativas:
        resultado = terminal(command=cmd, task_id=task_id)
        if resultado.exit_code == 0:
            return resultado
        print(f"⚠️ Fallback tentado: {cmd} → exit {resultado.exit_code}")
    
    # Todos falharam
    return resultado
```

## Estratégia de Uso

```
1. Comando falha (exit_code != 0)
2. Verificar na tabela de fallbacks
3. Tentar alternativa 1
4. Se falhar: tentar alternativa 2
5. Se NENHUMA funcionar:
   - Analisar a causa (output do erro)
   - Reportar erro real ao usuário com diagnóstico
   - Sugerir ação manual se aplicável
6. Se alguma funcionar:
   - Seguir em frente sem incomodar o usuário
```

## Observações
- Fallbacks são SILENCIOSOS — não pare de trabalhar, só registre qual fallback funcionou
- Só reporte ao usuário se TODAS as alternativas falharem
- Para tarefas críticas (deploy, migration), informe o fallback usado
