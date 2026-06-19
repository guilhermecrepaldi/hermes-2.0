---
name: hermes-hooks
description: "Sistema de hooks pre/post tool call para o Hermes. Inspirado nos Hooks do Claude Code (Set/2025) e no programmatic tool calling da Claude API. Dispara acoes automaticamente antes ou depois de ferramentas especificas. Ex: rodar testes apos editar codigo, lint antes de commit."
category: autonomous-ai-agents
tags: [hooks, automacao, pre-post, tool-call, claude-code, programmatic-tool-calling]
---

# Hermes Hooks — Pre/Post Tool Automation

## Inspiracao
- **Claude Code Hooks** (Set/2025): hooks pre/post que disparam automaticamente em eventos como `pre-tool-call`, `post-tool-call`, `pre-commit`, `post-test`
- **Programmatic Tool Calling** (Claude API, Jan/2026): agente escreve codigo que chama ferramentas programaticamente
- **Effective Harnesses** (Anthropic, Nov/2025): initializer + coding agent com artefatos de sessao

## Conceito

Hooks sao acoes automaticas que disparam em eventos especificos do ciclo de vida de uma ferramenta.

```
[Tool Call] → pre-hook → [EXECUCAO] → post-hook → resultado
                  │                        │
                  ▼                        ▼
            Valida antes            Valida depois
            (lint, check)           (testes, report)
```

## Hooks Disponiveis

| Hook | Dispara | Uso |
|------|---------|-----|
| `pre-patch` | Antes de editar arquivo | Lint, backup, check se arquivo existe |
| `post-patch` | Depois de editar | Rodar syntax check, atualizar hermes-progress |
| `pre-terminal` | Antes de comando shell | Validar comando, logar |
| `post-terminal` | Depois do comando | Checar exit code, logar resultado |
| `pre-git-commit` | Antes de commit | Rodar lint, check taste-skill |
| `post-git-commit` | Depois do commit | Atualizar changelog, notificar |
| `pre-delegate` | Antes de spawnar sub-agente | Verificar budget, logar inicio |
| `post-delegate` | Depois do sub-agente voltar | Consolidar resultado, logar gasto |
| `on-error` | Quando tool retorna erro | Auto-healing, logar erro |
| `on-success` | Quando tool conclui com sucesso | Avancar pipeline, logar |

## Config (skills/hermes-hooks/hooks.yaml)

```yaml
hooks:
  pre-patch:
    - action: "verificar_arquivo_existe"
      on_fail: "alert"     # skip | alert | block
  post-patch:
    - action: "rodar_syntax_check"
      on_fail: "block"
    - action: "atualizar_progress"
      on_fail: "skip"
  post-terminal:
    - action: "checar_exit_code"
      on_fail: "block"
  pre-git-commit:
    - action: "rodar_lint"
      on_fail: "block"
  on-error:
    - action: "auto_healing"
      on_fail: "report"
```

## Implementacao no Hermes

Os hooks sao seguidos por mim (Hermes) como procedimento automatico. Nao preciso de codigo extra — so da skill.

### Exemplo de Fluxo com Hooks

```
📝 patch(arquivo.py, old, new)
  ├─ [pre-patch] Verificar se arquivo existe... ✅
  ├─ [EXEC] patch aplicado ✓
  ├─ [post-patch] Syntax check... ✅
  └─ [post-patch] Atualizar hermes-progress.md... ✅

🖥️ terminal("pytest")
  ├─ [pre-terminal] Validar comando... ✅
  ├─ [EXEC] pytest rodou ✓
  ├─ [post-terminal] Exit code 0... ✅
  └─ [on-success] Avancar pipeline... ✅
```

### Lista de Hooks Autoload

Incluido no autoload para toda sessao:
```
hermes-hooks
```
