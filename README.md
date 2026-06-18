# hermes-2.0

**Hermes 2.0 — Sistema de Orquestração Multi-Shell com Watchdog 24/7, Journal AI Automatizado e Pipeline de Agentes Autônomos.**

Sistema completo de automação inteligente usando agentes de IA, watchdog de processos, orquestração multi-shell e pipeline automatizado de research em IA.

## 🎯 Funcionalidades

### 🤖 Agentes Autônomos
- **S1 Router** — roteamento inteligente de tarefas
- **S3 Headroom** — compressão inteligente de contexto
- **Hermes Doctor** — diagnóstico de saúde do sistema
- **Hermes Queen** — orquestração de agentes em cascata

### 🔄 Watchdog 24/7
- Monitoramento contínuo de processos
- Auto-recuperação em caso de falha
- Logs e notificações em tempo real
- Tray system invisível para Windows

### 🗞️ Journal AI Automatizado
- Escaneamento diário de notícias de IA
- Fontes: TechCrunch, Hacker News, arXiv, Reddit
- Resumo inteligente com DeepSeek
- Entrega em markdown estruturado

### ⚡ Shellz — Orquestração Multi-Shell
- 3 shells colaborativas
- QA integrado
- Tray guardian com auto-recuperação

## 🔧 Stack

| Componente | Tecnologia |
|------------|-----------|
| Python | 3.11+ |
| IA | DeepSeek API, Ollama |
| Shell | PowerShell, Batch, Bash |
| Monitoramento | Watchdog + Logging |
| Automação | Cron jobs + Hooks |

## 📁 Estrutura

```
├── hermes_workbench.py        # CLI principal
├── hermes_queen.py            # Orquestrador de agentes
├── hermes_doctor.py           # Diagnóstico
├── s1_router.py               # Roteador de tarefas
├── s3_headroom.py             # Compressão de contexto
├── watchdog_hermes.ps1        # Watchdog principal
├── shellz_menu.bat            # Menu Shellz
├── hooks/                     # Hooks de validação
├── docs/                      # Documentação
└── logs/                      # Logs do sistema
```

## 🚀 Quick Start

```bash
python hermes_workbench.py    # Iniciar workbench
python hermes_queen.py        # Orquestrador
./watchdog_hermes.ps1         # Watchdog
```

---

> Projeto em evolução contínua. Inspirado em arquiteturas de coding agents (Claude Code, Codex, Grok Build).
