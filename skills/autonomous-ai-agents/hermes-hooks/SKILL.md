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

## Hooks Avancados (ECC-inspired)

| Hook | Dispara | Padrão ECC | Uso |
|------|---------|------------|-----|
| `pre:bash:dispatcher` | Antes de bash | `PreToolUse/Bash` | Valida qualidade do comando, tmux, push, GateGuard |
| `pre:write:doc-file-warning` | Antes de Write | `PreToolUse/Write` | Avisa sobre arquivos de documentação não-padrão |
| `pre:edit-write:suggest-compact` | Após Edit/Write | `PreToolUse/Edit|Write` | Sugere compactação manual em intervalos lógicos |
| `pre:observe:continuous-learning` | Qualquer tool | `PreToolUse/*` | Captura observações para aprendizado contínuo (assíncrono, timeout 10s) |
| `pre:governance-capture` | Bash/Write/Edit | `PreToolUse/Bash|Write|Edit|MultiEdit` | Captura segredos, violações de política, pedidos de aprovação (ativa com ECC_GOVERNANCE_CAPTURE=1) |
| `pre:config-protection` | Write/Edit | `PreToolUse/Write|Edit` | Bloqueia alterações em configs de linter/formatter |
| `pre:mcp-health-check` | Qualquer tool | `PreToolUse/*` | Verifica saúde do MCP server antes de chamadas MCP |
| `pre:gateguard-fact-force` | Write/Edit | `PreToolUse/Edit|Write` | Força gate: bloqueia primeira Edit/Write por arquivo e exige investigação |
| `pre:compact` | Antes de compactar contexto | `PreCompact/*` | Salva estado antes de compactação |
| `stop:format-typecheck` | Ao parar | `Stop/*` | Batch formata (Biome/Prettier) + typecheck (tsc) em todos JS/TS |
| `stop:check-console-log` | Ao parar | `Stop/*` | Verifica console.log em arquivos modificados |
| `stop:session-end` | Ao parar | `Stop/*` | Persiste estado da sessão em arquivo de checkpoint |
| `stop:evaluate-session` | Ao parar | `Stop/*` | Avalia sessão e extrai patterns para aprendizado contínuo |
| `stop:cost-tracker` | Ao parar | `Stop/*` | Rastreia tokens e custo por sessão |
| `stop:desktop-notify` | Ao parar | `Stop/*` | Notificação desktop com sumário da resposta |
| `session:end:marker` | Fim de sessão | `SessionEnd/*` | Marcador de lifecycle (não-bloqueante) |

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

## Implementacao no Codigo (engine.py)

Os hooks agora tem uma implementacao real em `watchdog/engine.py`:

```python
from engine import HookManager

# Configurar hooks padrao
HookManager.setup_default()
# → pre-patch: verifica se arquivo existe
# → post-terminal: checa exit code

# Registrar hook customizado
def meu_pre_hook(ctx):
    path = ctx.get("path", "")
    if not os.path.exists(path):
        return {"warning": f"Arquivo nao existe: {path}"}
    return {"status": "ok"}

HookManager.register("pre", "patch", meu_pre_hook)

# Executar hooks
result = HookManager.execute("pre", "patch", {"path": "arquivo.py"})
# → {"executed": 1, "results": [{"status": "ok"}]}
## Hooks Implementados (procedurais)

Estes hooks sao seguidos por mim (Hermes) como procedimento automatico em toda sessao.

| Hook | Procedimento | O que fazer |
|------|-------------|-------------|
| `post-patch` | **Pre-output checklist** | Antes de responder, verificar: build compila? features intactas? APK/artefato existe? nada quebrado? |
| `post-terminal` | **Exit code check** | Verificar `exit=$?`. Se != 0, reportar e tentar alternativa. |
| `pre-commit` | **taste-skill + data-leak-scan** | Carregar `pre-commit-data-leak-scan` skill. Verificar as 10 regras do taste-skill. |
| `on-error` | **Auto-healing** | Se ferramenta falhou 3x, tentar alternativa (outra ferramenta, outro approach). |
| `post-delegate` | **Result consolidation** | Consolidar resultado de sub-agente. NUNCA confiar em auto-relato — verificar side effects. |
| `pre-output` | **Pre-output checklist completo** | Ver arquivo `references/pre-output-checklist.md` |

### Pre-Output Checklist (hook crítico)

O usuário disse: "esse teste tem q ser feito SEMPRE antes do output. pare de me entregar códigos quebrados."

Antes de QUALQUER resposta contendo código, build, ou entrega:
1. **Compila?** `./gradlew assembleDebug` / `go build` / `npm run build` → exit 0
2. **Features existentes continuam funcionando?** Nunca remover funcionalidade consolidada. Se reescreveu algo, compare com o original.
3. **APK/artefato gerado?** `ls -lh output` — existe e tem tamanho esperado
4. **Fluxo completo coberto?** Cada callback/conexão existe? Nenhum parâmetro obrigatório faltando?
5. **Nada quebrado pela edição?** `git diff` ou comparar arquivos modificados com o original
6. **Só então → responda**

Falhou no checklist → CORRIGA antes de responder.

### Exemplo de Fluxo Completo com hooks

```
📝 patch(arquivo.kt, old, new)
  ├─ [pre-patch] Verificar se arquivo existe... ✅
  ├─ [EXEC] patch aplicado ✓
  ├─ [post-patch] Build... ✅
  ├─ [post-patch] Verificar APK... ✅
  └─ [post-patch] Atualizar hermes-progress.md... ✅

🖥️ terminal("adb install app-debug.apk")
  ├─ [pre-terminal] Validar comando... ✅
  ├─ [EXEC] APK instalado ✓
  ├─ [post-terminal] Exit code 0... ✅
  └─ [on-success] Avancar pipeline... ✅
```

### ECC-Inspired Pre-Output Checklist Expandido

Antes de QUALQUER resposta contendo código, build, ou entrega:

1. **Segurança holística (ECC AgentShield)** — Verificar se há:
   - ✅ Credenciais/segredos hardcoded (tokens, senhas, API keys)
   - ✅ caminhos absolutos expostos (/home/user, /Users/nome)
   - ✅ IPs internos, URLs de staging/dev
   - ✅ Dados LGPD-sensiveis (CPF, RG, dados bancários)
   - ✅ Comentários com info sensível
   - ✅ console.log() em produção

2. **GateGuard (ECC)** — Se é a primeira Edit/Write no arquivo:
   - Investigar importadores, schemas de dados, instruções do usuário
   - Não permitir edição cega

3. **Verification loop (ECC)** — Checkpoint:
   - Compila? Features intactas? APK/artefato existe? Nada quebrado?

4. **Cost tracking (ECC)** — Anotar tokens gastos nesta rodada

5. **Session persistence (ECC)** — Salvar checkpoint

6. **Só então → responda**

### Lista de Hooks Autoload

Incluido no autoload para toda sessao:
```
hermes-hooks
```
