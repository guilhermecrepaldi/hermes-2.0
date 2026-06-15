# 🏆 Kimi Code CLI — Análise Comparativa vs Hermes Watchdog
**Data**: 2026-06-13 | **Repo**: MoonshotAI/kimi-code v0.15.0 | **Nosso**: Hermes Watchdog v3.1

---

## 📊 Sumário Executivo

| Dimensão | Kimi Code | Hermes Watchdog | Quem Ganha |
|----------|-----------|-----------------|------------|
| **Arquitetura** | Monorepo TypeScript (9 packages) | Python monolith | Kimi |
| **CLI** | Commander (flags + subcomandos) | argparse manual + subprocess | Kimi |
| **TUI** | pi-tui (reativo, temas custom) | Nenhum (só terminal) | **Kimi** |
| **Sub-agentes** | 3 built-in (coder/explore/plan) | delegate_task + skill_manage | **Kimi** |
| **Permissões** | Permission system + YOLO/auto | Nenhum (tudo liberado) | **Kimi** |
| **Hooks lifecycle** | Sim (pré-tool, pós-resposta) | Nenhum | **Kimi** |
| **Skills** | .agents/skills/<name>/SKILL.md | skill_manage + ~/.hermes/skills/ | **Kimi (mais integrado)** |
| **AGENTS.md** | Hierárquico (raiz + subdiretórios) | Nenhum | **Kimi** |
| **Session control** | Resume, fork, export, compress | Nenhum | **Kimi** |
| **Background tasks** | agent-task, process-task, persist | terminal(background=true) | **Kimi** |
| **Quota/Economia** | Nenhum específico | **Shellz + workbench** | **NÓS** ✅ |
| **Roteador S1/S2/S3** | Nenhum | **workbench + intelligence-router** | **NÓS** ✅ |
| **Watchdog 24/7** | Nenhum | **watchdog_hermes.py** | **NÓS** ✅ |
| **Setup versionado** | Nenhum | **setup_hermes.sh + skill** | **NÓS** ✅ |

---

## 🔴 O QUE O KIMI TEM DE SUPERIOR (Implementar AGORA)

### 1. Sistema de Permissões (PRIORIDADE MÁXIMA 🚨)

Kimi Code tem `-y/--yolo` (aprova tudo), `--auto` (auto permission mode) e `--plan` (só planeja, não executa).

**O que implementar:**
```
hermes-workbench --yolo           # Modo turbo (sem aprovações)
hermes-workbench --auto           # Auto permission mode
hermes-workbench --plan           # Modo planejamento (sem execução)
hermes-workbench --session <id>   # Resumir sessão anterior
```

**Arquivo**: `permissoes.py` em `D:/projetos/hermes-watchdog/`

### 2. Controle de Sessão (PRIORIDADE ALTA 🔥)

Kimi salva sessões em `$KIMI_CODE_HOME/sessions/` e permite:
- Resume (`-S` ou `-r`)
- Fork (`/fork`)
- Export (`kimi export`) como ZIP ou Markdown
- Context compression automática + manual (`/compress`)
- Título customizado (`/title`)

**O que implementar:**
```python
# Em hermes_workbench.py - novos comandos
session save    <nome>       # Salva contexto atual
session resume <nome>        # Restaura sessão
session list                  # Lista sessões salvas
session export <nome>        # Exporta como markdown
session fork <nome>          # Fork a partir de checkpoint
```

**Arquivo**: `session_manager.py` em `D:/projetos/hermes-watchdog/`

### 3. Hooks de Lifecycle (PRIORIDADE ALTA 🔥)

Kimi executa scripts nos pontos de vida do agente sem editar JSON.

**Modelo do Kimi** (arquivo TOML de config):
```toml
[hooks.before_tool_call]
command = "node scripts/validate.mjs"

[hooks.after_response]
command = "bash scripts/notify.sh"
```

**O que implementar:**
```python
# hooks_config.json
{
  "before_tool_call": "python validate.py",
  "after_tool_response": "python notify.py",
  "before_command": "python check_permission.py",
  "on_error": "python log_error.py"
}
```

**Arquivo**: `hooks_config.json` + `hook_runner.py`

### 4. Sub-agentes com Contexto Isolado (MELHORAR O QUE TEMOS)

Kimi tem 3 sub-agentes **fixos** com toolsets restritos:
- `coder` — leitura+escrita+execução (tudo liberado)
- `explore` — **readonly** (só busca, leitura — não escreve nem executa)
- `plan` — **nenhum comando shell** (só planejamento textual)

**O que implementar no hermes_workbench.py:**
```
hermes-workbench sub coder   "implemente X"    # Agente com toolsets totais
hermes-workbench sub explore "mapeie Y"        # Read-only
hermes-workbench sub plan    "arquitete Z"     # Só texto
```

### 5. AGENTS.md Hierárquico (IMPLEMENTAÇÃO RÁPIDA ✅)

Kimi usa AGENTS.md na raiz **e** em subdiretórios como prompt injetado.

**O que implementar:**
Criar `.hermes/AGENTS.md` com:
- Mapa do projeto (diretórios e responsabilidades)
- Hard constraints (regras do sistema)
- Workflow requirements
- Onde colocar novos recursos

E `docs/AGENTS.md` para regras específicas de documentação.

### 6. Plugins + Marketplace (MÉDIO PRAZO)

Kimi tem ecossistema de plugins com:
- Plugin marketplace (`/plugin`)
- Instalação de skills de GitHub
- Trust level por plugin

---

## 🟢 O QUE NÓS TEMMOS QUE O KIMI NÃO TEM (NOSSA VANTAGEM)

| Feature Nossa | Por que é superior |
|---------------|-------------------|
| **Shellz S1/S2/S3** | Kimi não tem fallback local+cloud — se API cair, ele para. Nós temos Ollama local + DeepSeek + Claude |
| **Watchdog 24/7** | Kimi não reinicia serviços. Nosso watchdog_hermes.py monitora e revive Hermes + Ollama |
| **Quota inteligente** | Kimi não tem gerenciamento de tokens — consome até acabar |
| **Setup versionado** | setup_hermes.sh garante que nada se perde |
| **Relatório de economia** | Shellz reporta economia vs cloud puro |
| **Windows-first** | Kimi trata Windows como cidadão de segunda classe |
| **Zero janelas** | VBS + pythonw — tudo invisível |
| **DeepSeek foco** | Agora 100% DeepSeek (conforme instrução) |

---

## 🎯 PLANO DE AÇÃO PRIORIZADO

### Fase 1 — HOJE (implementar agora)
1. ✅ Sistema de setup versionado (setup_hermes.sh + skill)
2. ✅ Roteador DeepSeek (hermes_workbench.py)
3. ⬜ **Permissões**: flags --yolo, --auto, --plan
4. ⬜ **AGENTS.md** na raiz do projeto

### Fase 2 — PRÓXIMA SESSÃO
5. ⬜ **Session Manager**: save/resume/list/export
6. ⬜ **Hooks**: hooks_config.json + hook_runner.py

### Fase 3 — FUTURO
7. ⬜ **Sub-agentes fixos**: coder, explore, plan
8. ⬜ **Plugin marketplace**
9. ⬜ **TUI** (interface visual interativa)

---

## 📋 Checklist de Melhorias Imediatas

- [ ] 1. Flag `--yolo` no hermes_workbench.py (aprova tudo)
- [ ] 2. Flag `--auto` (auto permission com regras)
- [ ] 3. Flag `--plan` (só planeja, sem tools de escrita)
- [ ] 4. Comando `session` (save/resume/list/export)
- [ ] 5. AGENTS.md na raiz com mapa do projeto
- [ ] 6. `hooks_config.json` com runner
- [ ] 7. Sub-agentes fixos via `hermes-workbench sub`
