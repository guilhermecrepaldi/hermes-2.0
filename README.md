# Hermes 2.0 — Orquestrador Multi-Shell Autônomo

> Sistema integrado de orquestração de agentes de IA com Workbench Mode, watchdog 24/7, pipeline multi-shell e deploy contínuo.
> **Construído em cima do [Hermes Agent](https://hermes-agent.nousresearch.com) da Nous Research.**

---

## ⚡ WORKBENCH MODE — A Raiz do Hermes

**Workbench Mode não é uma skill, não é uma config, não é opcional. É a raiz do programa.** Toda chamada no Hermes segue este fluxo:

```
🧠 S3 (deepseek-pro)       → Decide O QUÊ fazer, analisa prós/contras, define escopo
🗂️ S2 (deepseek-v4-flash)   → Arquieta COMO fazer, define componentes, interfaces, fluxo
⚙️ S1 (Ollama local)        → EXECUTA: gera código, escreve testes, implementa
🛠️ S0 (Python local)        → Testa, valida, verifica build
```

| Shell | Modelo | Papel | Custo | 
|-------|--------|-------|-------|
| 🧠 **S3** | deepseek-pro ☁️ | Decisão, planejamento, escopo | Pago (leve) |
| 🗂️ **S2** | deepseek-v4-flash ☁️ | Arquitetura, design, interfaces | Pago (mínimo) |
| ⚙️ **S1** | Ollama qwen2.5-coder:7b 🖥️ | **Execução, código, testes** | **GRÁTIS** |
| 🛠️ **S0** | Python local 🖥️ | Validação, testes, build | Grátis |

> **S1 é sempre local.** Regra absoluta. Economia reportada em toda resposta.
> Pular qualquer fase = proibido.

---

## 📊 Economia de Tokens

O Hermes 2.0 reporta em TODA resposta o quanto o S1 local economizou:

```
🧠 S3: deepseek-pro ☁️     | ~1.200 tokens  | $0.00048
🗂️ S2: deepseek-v4-flash ☁️ | ~800 tokens    | $0.00024
⚙️ S1: qwen2.5-coder:7b 🖥️  | ~9.500 tokens  | $0,00 🆓
🛠️ S0: python local 🖥️     | Testes          | $0,00 🆓
─────────────────────────────────────────────────────────────
💰 S1 economizou: $0.00285 (83%) vs fazer TUDO sem as atualizações (só cloud)
```

**Por que a economia é tão alta?**
- S1 local (Ollama) = $0 por token — **grátis**
- Modelos cloud = $0.00015~0.003 por token — **pago**
- 70-90% das tasks podem ser executadas no S1 local
- A economia acumulada escala linearmente com o uso

---

## 🏗️ Arquitetura

```
┌───────────────────────────────────────────────────────────────┐
│                        HERMES 2.0                             │
│                  (um único sistema integrado)                  │
└───────────────────────────────────────────────────────────────┘
         │                 │                │           
┌────────┴────────┐ ┌──────┴──────┐ ┌───────┴────────┐
│   WORKBENCH    │ │  WATCHDOG   │ │  CRON JOBS    │
│   ──────────   │ │  ────────   │ │  ──────────    │
│ S3→S2→S1→S0   │ │  VBS loop   │ │ 04:00 Backup   │
│ PROTOCOLO SEND│ │  pythonw     │ │                │
│ Token Tracker │ │  zero janela │ │                │
│ F1→F5         │ │  anti-travam │ │                │
└───────────────┘ └──────────────┘ └────────────────┘
```

### Pipeline Completo (F1 a F5)

```
F1 🧠 S3→ DECISION_PACKAGE:  O quê, por quê, alternativas, riscos
       ↓
F2 🗂️ S2→ ARCHITECTURE.md:  Componentes, interfaces, fluxo de dados
       ↓
F3 ⚙️ S1→ EXECUTION:         Código, testes, scripts (Ollama local)
       ↓
F4 🔄 S3→ REVIEW:            Quality Gate — aprova ou loop F2→F3 (máx 3)
       ↓
F5 📊 REPORT:                delivery-report + economia S1 + git commit
```

---

## 🧠 Gestão de Memória

A memória do Hermes 2.0 é **persistente entre sessões** e organizada em camadas:

| Camada | O que armazena | Exemplo |
|--------|---------------|---------|
| 🧠 **Memória persistente** | Fatos duráveis, preferências, regras | "WORKBENCH MODE É A RAIZ" |
| 📘 **Skills** | Procedimentos reutilizáveis | codebase-pack, code-audit-engine |
| 📊 **Token Tracker** | Histórico de tokens/custo | `token_history.jsonl` |
| 📝 **Session memory** | Contexto da sessão atual | tool calls, decisões |

**Regras de memória:**
- Fatos que serão úteis em futuras sessões → **memória persistente**
- Workflows e procedimentos → **skills** (SKILL.md)
- Custos e métricas → **token_tracker.py**
- Estado temporário de tarefa → **session_search** (não salvar em memória)

---

## 📡 PROTOCOLO SEND (Multi-IA Handoff)

Protocolo de comunicação entre shells com autoridades ponderadas:

```json
{
  "shell3": {
    "ias": [
      {"provider": "openai", "model": "gpt-4o-mini", "authority": 10},
      {"provider": "gemini", "model": "gemini-2.5-flash", "authority": 8}
    ],
    "strategy": "sequencial"
  },
  "shell2": {
    "ias": [
      {"provider": "mecanico", "authority": 10},
      {"provider": "openai", "model": "gpt-4o-mini", "authority": 5}
    ],
    "strategy": "sequencial"
  },
  "shell1": {
    "ias": [
      {"provider": "ollama", "model": "qwen2.5-coder:7b", "authority": 10},
      {"provider": "ollama", "model": "qwen2.5-coder:7b", "authority": 10}
    ],
    "strategy": "paralelo",
    "workers": 10
  }
}
```

**Estratégias de handoff:**
- **sequencial**: Tenta IA de maior autoridade, se falhar vai para a próxima
- **paralelo**: Executa múltiplas IAs simultaneamente, pega o melhor resultado
- **consenso**: Múltiplas IAs votam, só aceita se maioria concordar
- **fallback**: Tenta principal, cai para reserva se timeout/erro

---

## 🔧 Componentes do Sistema

### 🛡️ Watchdog 24/7

Monitoramento contínuo sem abrir janelas (VBS + pythonw):

| Arquivo | Função |
|---------|--------|
| `watchdog_invisible.vbs` | Launcher VBS — loop que executa sem janela cmd |
| `watchdog_hermes.py` | Monitor: timeout 25min, loop detection, zumbi |
| `shellz_tray.py` | Ícone na bandeja do Windows (verde/laranja/cinza) |

**Proteções:**
- ⏱️ Log parado >25min → kill + recovery
- 🔄 5x mesma tool call → kill (loop detection)
- 💀 CPU 0% por 5min → kill (processo zumbi)
- 🔌 Pausa GPU via `.shellz_paused` → watchdog respeita

### 📦 Skills do Hermes

| Skill | Categoria | Função |
|-------|-----------|--------|
| `workbench-mode` | 🏭 **RAIZ** | Operating model padrão (S3→S2→S1) |
| `delivery-report` | 📊 Report | Relatório pós-entrega padronizado |
| `code-audit-engine` | 🔬 Auditoria | 5 técnicas (radon, flake8, mutmut, pydeps, wily) |
| `codebase-pack` | 📦 Util | Empacota repo em 1 XML/MD para LLM |
| `repo-explainer` | 🔍 Pesquisa | Explica qualquer repo em profundidade |
| `codebase-rag` | 🧠 RAG | RAG local sobre código com embeddings |
| `exercise-variator` | 📐 Educação | Gera variações paramétricas de exercícios |
| `software-architecture-review` | 🏗️ Arquitetura | Revisão arquitetural de codebases |

### ⏰ Cron Jobs

| Job | Schedule | Função |
|-----|----------|--------|
| Backup completo | 04:00 | Backup do projeto + config + skills + cron + memória |

---

## 🖥️ Shells Locais (Ollama)

O Hermes 2.0 usa Ollama como IA local para execução (S1). Modelos disponíveis:

| Modelo | Tamanho | Ideal para |
|--------|---------|------------|
| **qwen2.5-coder:7b** | 4.7GB | ✅ Geração de código, testes, scripts |
| **deepseek-coder-v2:lite** | 8.9GB | Código complexo, refatoração |
| **llama3.1:8b** | 4.9GB | Análise, planejamento |
| **deepseek-coder:6.7b** | 3.8GB | Código leve |
| **gemma3** | 3.3GB | Alternativa rápida |
| **llama3.2:3b** | 2.0GB | Tarefas simples |

**Shell 1 (S1) é sempre Ollama local. Grátis. Sempre que possível.**

---

## 🔄 Ciclo de Vida de uma Tarefa

Toda solicitação ao Hermes 2.0 segue automaticamente:

```
1. 🧠 S3: DECISION_PACKAGE
   → "O quê, por quê, alternativas, riscos, arquivos afetados"

2. 🗂️ S2: ARCHITECTURE.md  
   → "Componentes, interfaces, fluxo de dados, skills necessárias"

3. ⚙️ S1: EXECUÇÃO (Ollama local)
   → Código, testes, scripts — tudo local, grátis

4. 🔄 S3: REVIEW (Quality Gate)
   → Código correto? Testes passam? Aprova ou loop F2→F3 (máx 3)

5. 📊 F5: RELATÓRIO
   → delivery-report + economia S1 + git commit
```

---

## 📁 Estrutura do Projeto

```
D:\projetos\
├── hermes-2.0\              ← Este repositório (docs, config, scripts)
├── hermes-watchdog\         ← Watchdog + Shellz Tray + VBS guardian
├── workbench-ai.manager\    ← Orquestrador multi-shell (PROTOCOLO SEND)
├── LOVE CLASS\              ← Projeto SPRINT (app Android de matemática)

~/.hermes/
├── skills\                  ← Skills do Hermes (30+)
├── config.yaml              ← Config principal
├── .env                     ← API keys e secrets

~/.hermes-watchdog\           ← Logs do watchdog
```

---

## 🚀 Como Usar

```bash
# Iniciar watchdog (fundo, zero janelas)
wscript.exe D:\projetos\hermes-watchdog\watchdog_invisible.vbs

# Verificar status do watchdog
cat ~/hermes-watchdog/watchdog_state.json

# Verificar Ollama (S1 local)
ollama list

# Ver economia acumulada
python D:\projetos\workbench-ai.manager\src\workbench\monitoring\token_tracker.py

# Status completo do Hermes
hermes status
```

---

## 🛡️ Princípios

1. **Workbench Mode é a raiz** — S3→S2→S1 em toda call. Não é skill, não é opcional.
2. **S1 é sempre local** — Ollama executa código. Grátis. Reportar economia.
3. **Conhecimento persiste** — memória, skills, token_tracker. Nada morre na sessão.
4. **Tudo integrado** — watchdog, cron, skills são UM sistema.
5. **Economia de tokens** — ~70-90% das tasks vão para S1 local. Economia reportada sempre.
6. **Zero janelas** — processos background usam pythonw + VBS. Sem cmd.exe.
7. **Auto-recuperação** — watchdog detecta travamento e recupera automaticamente.

---

## Tecnologias

- **Hermes Agent** (Nous Research) — plataforma base de agente autônomo
- **DeepSeek** — modelo de raciocínio (S3 cloud)
- **Ollama** — IA local (S1 execução, 7+ modelos)
- **Python** — scripts de automação, token tracking
- **Batch/VBS** — watchdog zero-janela

---

## GitHub

Projeto aberto para contribuição e estudo.
Repositório: [github.com/guilhermecrepaldi/hermes-2.0](https://github.com/guilhermecrepaldi/hermes-2.0)

---

**Hermes 2.0** — Um único sistema. Multi-shell. Auto-recuperável. Econômico.
