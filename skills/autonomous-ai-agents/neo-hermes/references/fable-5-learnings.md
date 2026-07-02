# Fable 5 — Lições da Arquitetura do Claude Code (Leak Mar/2026)

**Fonte**: https://github.com/asgeirtj/system_prompts_leaks (43.3K⭐)
**Contexto**: 512K linhas de TypeScript expostas via npm source map

## Principais Descobertas

### 1. Agent Loop = ~20 linhas de `while True`
Todo o poder está no **harness**, não no loop. O loop só orquestra.

### 2. Complexidade no Harness
Permissões, contexto, memória, tools — tudo no harness. Skills são só ações que o harness dispara.

### 3. Segurança nas Tool Descriptions
Regras de segurança embedadas na descrição de cada tool. Sem policy externa.

### 4. Modelo Barato para Decisões
Haiku (leve/barato) roda safety checks antes de ações caras.
**Nossa versão**: `classificar_tarefa_local()` com Ollama antes de rotear pra nuvem.

### 5. Context Engineering > Prompt Engineering
Estrutura do contexto (hermes-progress.md) é o diferencial, não o prompt.

### 6. KV Cache Compartilhado
Sub-agentes compartilham cache → 40-60% economia de tokens.
**Nossa versão**: `delegate_task` com `background=True`.

### 7. 44 Features Escondidas
Features atrás de compile-time flags.

## Implementação no Hermes 2.0

| Fable 5 | Hermes 2.0 | Arquivo |
|---------|-----------|---------|
| Agent loop | `HermesLoop.run()` | `hermes_loop.py` |
| Harness | `HermesHarness` | `watchdog/core.py` |
| Segurança embedada | `Action.required_permissions` | `watchdog/core.py` |
| Haiku para decisões | `classificar_tarefa_local()` | `watchdog/core.py` |
| Context Engineering | `Context` dataclass + `hermes-progress.md` | `watchdog/core.py` + raiz |
| Memória leve | `recent_actions[10]` + persistente | `watchdog/core.py` |
