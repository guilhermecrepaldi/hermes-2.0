# 🏛️ HERMES NEO — Arquitetura Completa (v4.0)
**Inspirado em**: Ruflo (Queen Agent), Kimi Code (AGENTS.md + skills), DiffusionGemma (paralelismo), Qwen3-VL (visão local)

---

## 👑 Queen Agent — Cérebro do Sistema

```
Usuário → [REQUEST] 
                │
          ┌─────▼──────┐
          │  👑 QUEEN  │  ← Decide, delega, coordena
          │  AGENT     │
          └─────┬──────┘
                │
     ┌──────────┼──────────┐
     │          │          │
┌────▼───┐ ┌───▼────┐ ┌───▼────┐
│ 🏗️ S3  │ │ 🔍 S2  │ │ 💻 S1  │  ← Workers paralelos
│ Decisão│ │ Pesquisa│ │ Código │
└────┬───┘ └───┬────┘ └───┬────┘
     │          │          │
     └──────────┼──────────┘
                │
          ┌─────▼──────┐
          │  👁️ S3 QA  │  ← Quality Gate (consenso)
          └─────┬──────┘
                │
          ┌─────▼──────┐
          │  📊 REPORT │  ← Economia + relatório
          └─────┬──────┘
                │
           [RESPONSE]
```

## 🧠 SONA — Roteador Inteligente (substitui keyword match)

Usa **Qwen3-VL** para classificar tarefas em <1s:

```python
SONA_TIERS = {
    "S1": {"modelo": "ollama/qwen2.5-coder:7b", "custo": 0, "tipo": "codigo, comando, arquivo"},
    "S2": {"modelo": "deepseek-v4-flash", "custo": 0.15, "tipo": "pesquisa, analise, revisao"},
    "S3": {"modelo": "deepseek-pro", "custo": 0.50, "tipo": "decisao, estrategia, arquitetura"},
}
```

## 🔗 Hooks Lifecycle — 5 Pontos de Gatilho

```python
HOOKS = {
    "before_task":    "hooks/validate.py",     # Valida antes de executar
    "after_task":     "hooks/notify.py",        # Notifica após
    "before_command": "hooks/check_perms.py",   # Permissão
    "on_error":       "hooks/log_error.py",     # Log de erro
    "on_complete":    "hooks/report.py",        # Relatório final
}
```

## 💾 Pattern Memory — Memória Vetorial

```python
pattern_memory = {
    "problema": "erro SQL injection no login",
    "solucao": "usar parameterized queries",
    "modelo": "deepseek-v4-flash",
    "custo": 0.003,
    "timestamp": "2026-06-13",
    "tags": ["seguranca", "sql", "backend"]
}
```

## 📊 Comparativo de Economia

| Feature | Antes (v3.1) | Depois (v4.0 Neo) |
|---------|--------------|-------------------|
| **Roteamento** | Keyword match | Qwen3-VL (SONA) |
| **Orquestração** | Sequencial (F1→F2→F3) | Paralelo (Queen+Workers) |
| **Velocidade** | 4 etapas sequenciais | Workers paralelos (3x) |
| **Economia** | ~41% | ~75% (target) |
| **Memória** | Manual (skill) | Automática (vetorial) |
| **Hooks** | Nenhum | 5 hooks lifecycle |
| **Doctor** | setup_hermes.sh --verify | hermes doctor (completo) |
| **Tolerância** | Fallback chain | Consenso Queen (3x peso) |

## 📁 Estrutura de Arquivos

```
D:/projetos/hermes-watchdog/
├── hermes_workbench.py     ← CLI principal (comandos)
├── hermes_queen.py         ← Queen Agent (orquestradora)
├── hermes_sona.py          ← SONA router (Qwen3-VL)
├── hermes_doctor.py        ← Health check completo
├── hermes_hooks.py         ← Lifecycle hooks
├── hermes_memory.py        ← Pattern memory (vetorial)
├── hooks/
│   ├── validate.py
│   ├── notify.py
│   ├── check_perms.py
│   ├── log_error.py
│   └── report.py
├── patterns/               ← Pattern memory storage
├── quota_config.json
├── setup_hermes.sh
└── video_analyzer.py
```

## 🧪 Plano de Testes

1. `python hermes_queen.py "criar rota de login"` → Queen delega para S3+S2+S1 em paralelo
2. `python hermes_sona.py "refatorar função de pagamento"` → Classifica como S2 (código médio)
3. `python hermes_doctor.py` → Verifica Python, FFmpeg, Ollama, GPU, disco, git
4. `python hermes_memory.py search "sql injection"` → Retorna pattern salvo
5. `hermes hooks run before_task --task "deploy"` → Executa hook de validação
