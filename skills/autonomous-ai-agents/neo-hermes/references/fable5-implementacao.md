# Implementacao Fable 5 no Hermes 2.0

## Estrutura Completa (Jun/2026)

```
hermes-2.0/
├── hermes_loop.py                 # Agent Loop (~15 linhas de logica)
├── hermes-progress.md             # Session continuity (auto-gerenciado)
├── finalizer-loop.sh              # Watchdog a cada 2 minutos
├── watchdog/
│   ├── core.py                    # HermesHarness + Action + Context
│   ├── engine.py                  # Checkpoint, Hooks, Cache, Worktree
│   ├── finalizer.py               # check_pending() + fix_pending()
│   ├── s1_router.py               # Router com dataclass + type hints
│   ├── config.py                  # Config centralizada
│   ├── logger.py                  # Logging estruturado
│   └── monitor.py                 # Monitor de processos
├── tests/
│   ├── test_core.py               # 6 testes
│   ├── test_engine.py             # 10 testes
│   ├── test_economy.py            # 4 testes
│   ├── test_router.py             # 6 testes
│   └── test_workbench.py          # 2 testes
├── pyproject.toml                 # ruff + pytest + mypy
├── .github/workflows/ci.yml       # GitHub Actions
├── THIRD_PARTY_NOTICES.md         # OSS atribuicao
└── SPEC_ARQUITETURA_HERMES.md     # Mapa arquitetural Fable 5
```

## Componentes Fable 5 Implementados

### 1. Agent Loop (hermes_loop.py)
```python
while True:
    user_input = get_input()
    harness.update_context(user_input)
    salvar_progresso("INPUT", user_input[:40])
    ctx = carregar_progresso()
    harness.context.hermes_progress = str(ctx.get("feito", []))
    action = harness.choose_action(user_input)
    result = harness.execute_action(action, user_input)
    harness.update_progress(result)
    salvar_progresso(action.name, result.summary[:80])
    if len(harness.context.recent_actions) % 5 == 0:
        CheckpointManager.save()
```

### 2. Harness (core.py)
- HermesHarness: permissoes, contexto, memoria, tools
- Action com security_policy embedada (R11)
- Roteamento: Ollama primeiro ($0), cloud fallback
- Tool descriptions com SECURITY prefix

### 3. Engine (engine.py)
- Context Engineering: carregar/salvar progresso
- Checkpointing: save/list/auto_compact (10 max)
- Hooks: pre/post com setup_default
- KV Cache: TTL + compactacao
- Subagent worktrees: git worktree add/remove
- Initializer + Coding Agent: setup → plan → execute

### 4. Finalizer (finalizer.py)
- check_pending(): varre testes, git, TODOs, CI, SPEC
- fix_pending(): commit, push, pytest
- ignora hermes-progress.md (muda sempre)
- max 10 tentativas no loop

## Metricas

| Item | Valor |
|---|---|
| Testes | 28/28 passando |
| CI | Verde |
| Loop central | ~15 linhas |
| Loops hooks | pre-patch + post-terminal |
| Subagents | via git worktrees |
| Checkpoints | auto a cada 5 acoes |
| Finalizer | 2min loop watchdog |
| Security embed | 7 actions + 6 tools |
