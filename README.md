# 🤖 NEO HERMES

**Multi-Shell Autonomous AI Orchestration System** — Watchdog 24/7, agent pipelines, context compression, smart routing.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek%20V4%20Flash-red)
![Ollama](https://img.shields.io/badge/Local-Ollama-green)
![Headroom](https://img.shields.io/badge/Context-Headroom.ai-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **Orquestrador inteligente que roda agentes de IA (cloud + local), watchdog de auto-recuperação, roteamento econômico de tarefas e pipeline automatizado de research.**  
> ⚡ Economia de até **66×** em custo de tokens vs concorrência.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                    NEO HERMES                        │
├─────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │   S1     │  │   S3     │  │   Hermes Queen    │   │
│  │  Router  │  │ Headroom │  │   (Orchestrator)  │   │
│  │(Ollama)  │  │(DeepSeek)│  │   (Cascading)    │   │
│  │  $0/task │  │$0.015/M  │  │                  │   │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘   │
│       │              │                │              │
│  ┌────▼──────────────▼────────────────▼──────────┐   │
│  │           Watchdog Guardian 24/7              │   │
│  │     (auto-recuperação + telemetria)          │   │
│  └───────────────────────────────────────────────┘   │
│  ┌───────────────────────────────────────────────┐   │
│  │         Cron Jobs / Hooks Pipeline            │   │
│  │  Jornal AI | Research | Monitoração           │   │
│  └───────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 Funcionalidades

### 🤖 Agentes Autônomos
| Componente | Função | Motor | Custo |
|-----------|--------|-------|-------|
| **S1 Router** | Tarefas simples (validação, ajustes, verificação) | Ollama qwen2.5-coder | **Grátis** |
| **S3 Headroom** | Tarefas complexas (orquestração, análise) | DeepSeek V4 Flash | ~$0.015/1M tokens |
| **Hermes Queen** | Orquestrador em cascata de sub-agentes | DeepSeek V4 Flash | ~$0.015/1M tokens |
| **Hermes Doctor** | Diagnóstico de saúde do sistema | Ollama | **Grátis** |

### 🔄 Watchdog 24/7
- Monitoramento contínuo de processos
- Auto-recuperação em caso de falha
- Logs e notificações em tempo real
- Tray guardian invisível (Windows)

### ⚡ Shellz — Roteamento Inteligente
- **3 shells colaborativas** com roteamento automático
- **ECC** (Economic Checkpoint Control) — otimização de custo por tarefa
- **QA integrado** — validação automática antes de entrega

### 🗞️ Jornal AI Automatizado
- Escaneamento diário de IA e tech
- Fontes: TechCrunch, HN, arXiv, Reddit
- Resumo inteligente com DeepSeek
- Entrega em markdown estruturado

### 📊 Telemetria Obrigatória
- Footer de custo em toda resposta
- Comparativo: Régua US$ 1/1M × DeepSeek × Ollama
- Transparência total de gasto por operação

---

## 🔧 Stack

| Componente | Tecnologia |
|-----------|-----------|
| **Core** | Python 3.11+ |
| **LLM Cloud** | DeepSeek V4 Flash (via Headroom :8787) |
| **LLM Local** | Ollama (qwen2.5-coder) |
| **Context Compression** | Headroom.ai (cache + compressão) |
| **Shell** | Python, Bash, Batch |
| **Monitoramento** | Watchdog + Logging estruturado |
| **Cron** | Agendamento interno + Hooks |
| **Documentação** | Skills (SKILL.md), Memory persistente |

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/guilhermecrepaldi/neo-hermes.git
cd neo-hermes

# 2. Instalar
pip install -r requirements.txt

# 3. Configurar Headroom (recomendado)
#   Editar: /watchdog/headroom_config.yaml

# 4. Iniciar
python hermes_queen.py            # Orquestrador principal
python watchdog/headroom.py       # Proxy Headroom (cache/localhost:8787)
```

### Comandos Rápidos

```bash
python hermes_queen.py          # Iniciar orquestrador
python watchdog/s1_executor.py  # Executor de tarefas S1
python hermes_doctor.py         # Diagnóstico do sistema
```

---

## 📁 Estrutura do Projeto

```
neo-hermes/
├── hermes_queen.py            # Orquestrador principal de agentes
├── hermes_doctor.py           # Diagnóstico de saúde
├── hermes_workbench.py        # CLI principal
├── watchdog/
│   ├── s1_executor.py         # Executor de tarefas simples (Ollama)
│   ├── s3_headroom.py         # Executor de tarefas complexas (DeepSeek)
│   ├── shellz.py              # Roteador Shellz
│   ├── headroom.py            # Proxy headroom.ai
│   ├── headroom_config.yaml   # Config do headroom
│   └── telemetria.py          # Telemetria de custos
├── skills/                    # Skills do sistema (SKILL.md)
├── hooks/                     # Hooks de validação
├── docs/                      # Documentação
└── logs/                      # Logs do sistema
```

---

## 📊 Economia de Tokens

| Motor | Custo 1M tokens | vs Régua (US$ 1) |
|-------|----------------|------------------|
| Ollama qwen2.5-coder | **Grátis** | Infinito |
| DeepSeek V4 Flash (direto) | $0,15 | 6× mais barato |
| DeepSeek via Headroom (cache) | ~$0,015 | **66× mais barato** |
| **Régua base** | **$1,00** | — |

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja nossos [issues](https://github.com/guilhermecrepaldi/neo-hermes/issues) para começar.

---

## 📫 Contato

**Guilherme Crepaldi** — [silvagui8@gmail.com](mailto:silvagui8@gmail.com)  
🔗 [LinkedIn](https://linkedin.com/in/guilherme-crepaldi-778b3b237) · [Portfolio](https://crepaldi.online) · [GitHub](https://github.com/guilhermecrepaldi)

---

> ⚡ *"Autonomous systems that deliver. Agents that learn. Code that runs 24/7."*
