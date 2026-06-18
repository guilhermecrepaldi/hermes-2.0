---
name: repos-chineses-japoneses-2026
description: "Pesquisa dos principais repositorios chineses e japoneses de 2026 sobre orquestracao multi-agente, memoria de contexto, skills, governanca de IAs e conselho de agentes. Inclui DeerFlow (ByteDance), OWL (CAMEL-AI), LightAgent, EvoAgentX, Shannon (Kocoro-lab/Japan), OxiFY (Japan) e licoes para o Neo Hermes."
category: autonomous-ai-agents
tags: [china, japan, multi-agent, orquestracao, memoria, skills, governanca, agentes, pesquisa]
---

# Repositórios Chineses e Japoneses — Orquestração, Memória, Skills e Governança (2026)

---

## 1. DeerFlow — ByteDance (China) ⭐ 37K+

**GitHub**: https://github.com/bytedance/deer-flow  
**Descrição**: DeerFlow (Deep Exploration and Efficient Research Flow) é um **super agent harness** open-source que orquestra sub-agentes, memória e sandboxes para fazer praticamente qualquer coisa. Construído sobre LangGraph.

### Arquitetura

```
[Lead Agent] → Decompõe tarefa em sub-tarefas
  ├── [Sub-Agent 1] (Pesquisador) → sandbox Docker isolado
  ├── [Sub-Agent 2] (Codificador) → sandbox Docker isolado
  ├── [Sub-Agent 3] (Analista) → sandbox Docker isolado
  └── [Sub-Agent N] → paralelo, cada um com seu contexto
```

### Diferenciais Chave

| Feature | Descrição | Aplicação no Hermes |
|---------|-----------|-------------------|
| **Super Agent Harness** | Agente líder orquestra, não executa | Hermes já faz com `delegate_task` |
| **Sandbox Docker** | Cada sub-agente em container isolado | Podemos usar `terminal` com Docker |
| **Memória Persistente** | Sub-agentes compartilham estado via memória | Nossa memory + skills |
| **Skills Extensíveis** | Plugins que adicionam capacidades | Já temos skills! |
| **Model-agnostic** | Qualquer LLM com API OpenAI-compatível | Hermes também é |
| **LangGraph Interno** | Graph-based orchestration | Podemos usar DAGs nas skills |

### Lições para o Neo Hermes

1. **Sandbox por sub-agente** — DeerFlow isola cada sub-agente em Docker. Podemos criar skill que spawna sub-agentes em worktrees/containers isolados
2. **Lead Agent não executa, só orquestra** — similar ao nosso `auto-executor` que planeja e delega
3. **Memória compartilhada entre sub-agentes** — nossa memory já faz, mas DeerFlow faz via arquivo compartilhado (podemos usar `MEMORY.md`)

---

## 2. OWL — CAMEL-AI (China) ⭐ 19.9K

**GitHub**: https://github.com/camel-ai/owl  
**Descrição**: Optimized Workforce Learning for General Multi-Agent Assistance. Framework de ponta para colaboração multi-agente que empurra os limites da automação de tarefas.

### Diferenciais

| Feature | Descrição |
|---------|-----------|
| **Workforce Learning** | Agentes aprendem com o trabalho que fazem |
| **General Multi-Agent** | Não é especializado — qualquer tarefa |
| **Role-Playing** | Cada agente tem um papel (pesquisador, codificador, revisor) |
| **Tool Integration** | Ferramentas externas como primeira classe |
| **Comunidade Ativa** | 642 commits, 2.3K forks |

### Lições

1. **Role-playing agents** — cada agente com identidade fixa (similar ao CrewAI). Podemos criar skills com papéis fixos no Hermes
2. **Aprendizado contínuo** — agentes melhoram com o tempo. Nossas skills já fazem isso (curator mantém skills)

---

## 3. LightAgent — wanxingai (China) ⭐ 1.1K

**GitHub**: https://github.com/wanxingai/LightAgent  
**Descrição**: Framework leve de agente IA com **memória, MCP e skills**. Suporta colaboração multi-agente, auto-aprendizado e principais LLMs (OpenAI/DeepSeek/Qwen).

### Diferenciais

| Feature | Descrição |
|---------|-----------|
| **Memória Vetorial** | Vector memory adapter embutido |
| **MCP Nativo** | Protocolo MCP integrado |
| **Skill Manager** | Sistema de gerenciamento de skills |
| **Self-Learning** | Agente aprende com interações passadas |
| **Multi-LLM** | OpenAI, DeepSeek, Qwen — mesma interface |
| **Leve** | Design minimalista, sem dependências pesadas |

### Lições para o Neo Hermes

1. **Vector Memory Adapter** — LightAgent tem adaptador de memória vetorial. Podemos adicionar Mem0 ou similar ao Hermes
2. **Skill Manager** — similar ao nosso sistema de skills, mas com API REST
3. **Self-Learning** — LightAgent tem `self.learn()` que atualiza o comportamento baseado em feedback. Nossa skill `curator` faz algo similar

---

## 4. EvoAgentX — China ⭐ 3.1K

**GitHub**: https://github.com/EvoAgentX/EvoAgentX  
**Descrição**: 🚀 EvoAgentX: Building a Self-Evolving Ecosystem of AI Agents. O agente **monta automaticamente workflows multi-agente** a partir de uma descrição em linguagem natural.

### Diferenciais

| Feature | Descrição |
|---------|-----------|
| **Auto-Workflow Assembly** | Descreva o objetivo → ele monta o workflow multi-agente |
| **Prompt Templates** | Templates de prompt evoluem com uso |
| **Ecosystem** | Agentes compartilham conhecimento entre si |
| **Ferramentas Integradas** | Crawler, pesquisa, MCP |

### Lições

1. **Auto-assembly** — descrever objetivo e o sistema monta os agentes necessários. Nosso `auto-executor` já faz PLAN → EXECUTE → VERIFY
2. **Prompt Templates evolutivos** — templates melhoram com o uso. Podemos versionar prompts nas skills
3. **Ecossistema evolutivo** — skills que se auto-melhoram com o tempo

---

## 5. Shannon — Kocoro-lab (Japão) ⭐ (crescendo)

**GitHub**: https://github.com/Kocoro-lab/Shannon  
**Descrição**: Framework de **orquestração multi-agente orientado a produção**. Foco japonês em confiabilidade, governança e depuração.

### Diferenciais

| Feature | Descrição |
|---------|-----------|
| **Swarm V2** | Lead-orchestrated multi-agent system com loops paralelos |
| **Token Budget Control** | Controle de orçamento de tokens por agente |
| **Human Approval Workflows** | Fluxos de aprovação humana embutidos |
| **Time-Travel Debugging** | Depuração com viagem no tempo (replay de estados) |
| **Channels System** | Webhooks Slack e LINE |
| **Multi-strategy Orchestration** | Várias estratégias de orquestração |

### Lições para o Neo Hermes

1. **Token Budget Control** — controlar quantos tokens cada agente/sub-agente pode gastar. Podemos implementar via `roteador-economico`
2. **Human Approval Workflows** — Hermes já tem `clarify` para aprovação
3. **Time-Travel Debugging** — Hermes tem `/rollback` para checkpoints
4. **Swarm V2** — sub-agentes liderados por um orquestrador central, com loops paralelos

### Filosofia Japonesa Aplicada

O Shannon é construído com **foco em produção**: confiabilidade > velocidade, governança > autonomia cega, depuração > tentativa e erro. Isso é valioso para o Neo Hermes: precisamos de **governança de agentes** (quanto cada um pode gastar, o que cada um pode fazer, trilha de auditoria).

---

## 6. OxiFY — cool-japan (Japão) ⭐

**GitHub**: https://github.com/cool-japan/oxify  
**Descrição**: Plataforma de **orquestração de workflow LLM baseada em grafos**, construída em Rust. Usa DAGs (Directed Acyclic Graphs) para compor aplicações de IA complexas.

### Diferenciais

| Feature | Descrição |
|---------|-----------|
| **Graph-Based Workflows** | DAGs visuais para workflows de LLM |
| **Type-Safe** | Garantias em tempo de compilação (Rust) |
| **Multi-Provider** | OpenAI, Anthropic, modelos locais |
| **Event-Driven** | Arquitetura orientada a eventos |
| **Rust Performance** | Execução rápida e segura |

### Lições

1. **Workflows como DAGs** — nossas skills são lineares. Podemos implementar DAGs (passos paralelos que se juntam)
2. **Type-Safe** — validação de tipos nas skills (entrada/saída esperada)
3. **Event-Driven** — hooks pre/post tool call (já temos hooks via `auto-healing`)

---

## 7. Awesome AI Agents 2026 — Zijian-Ni (China) ⭐

**GitHub**: https://github.com/Zijian-Ni/awesome-ai-agents-2026  
**Descrição**: A lista definitiva de modelos, frameworks, ferramentas, protocolos e recursos de agentes para 2026. Curadoria chinesa.

### Destaques

| Categoria | Projetos |
|-----------|----------|
| **Memória** | agent-memory, Mem0 (graph variant), Letta, Zep |
| **Multi-Agent** | AutoGen, MetaGPT, CAMEL, CrewAI, OpenAI Swarm |
| **Protocolos** | MCP (Anthropic), A2A (Google), ACP (xAI) |
| **Coding Agents** | Claude Code, Codex, DeerFlow, OpenClaw |
| **Governança** | Veritas OS (Japan), agent-governance, Guardrails |

---

## 8. Tabela Comparativa — O Que Levar para o Neo Hermes

| Projeto | Origem | Estrelas | Melhor Feature | Aplicação no Hermes |
|---------|--------|:-------:|----------------|-------------------|
| **DeerFlow** | 🇨🇳 ByteDance | 37K+ | Super Agent Harness + Sandbox | delegate_task com Docker |
| **OWL** | 🇨🇳 CAMEL-AI | 19.9K | Workforce Learning | Role-playing agents |
| **LightAgent** | 🇨🇳 wanxingai | 1.1K | Vector Memory + Self-Learning | Mem0 integration |
| **EvoAgentX** | 🇨🇳 | 3.1K | Auto-workflow assembly | Auto-executor melhorado |
| **Shannon** | 🇯🇵 Kocoro | crescendo | Token Budget + Governance | Roteador-economico + auditoria |
| **OxiFY** | 🇯🇵 cool-japan | — | Graph-based DAG workflows | Skills como DAGs |
| **Veritas OS** | 🇯🇵 | — | AI Agent Governance Runtime | Permissões + audit trail |

---

## 9. Roadmap de Implementação no Neo Hermes

### Fase 1 — Imediata (já temos similar)

| Feature | Já temos | Melhoria |
|---------|---------|----------|
| Super Agent Harness | `auto-executor` + `delegate_task` | Adicionar sandbox Docker |
| Role-playing agents | Skills com papéis | Criar roles fixos (dev, reviewer, tester) |
| Memory persistente | `memory` + `skills` | Adicionar Mem0 para memória vetorial |
| Token Budget Control | `roteador-economico` | Limite por agente/sub-agente |

### Fase 2 — Curto Prazo

| Feature | Como implementar |
|---------|-----------------|
| **Skills como DAGs** | Skills com passos paralelos (inspirado em OxiFY + DeerFlow) |
| **Auto-workflow assembly** | EvoAgentX-style: descrever objetivo → montar workflow |
| **Governança de agentes** | Shannon-style: budget, permissões, audit trail |
| **Self-learning** | LightAgent-style: agente aprende com feedback |

### Fase 3 — Visão

| Feature | Inspiração |
|---------|-----------|
| **Conselho de IAs** | Múltiplos agentes deliberam antes de agir (Shannon Swarm) |
| **Time-travel debugging** | Shannon + Hermes `/rollback` |
| **Agent Marketplace** | Skills público + importação entre frameworks |
| **Graph-based orchestration** | OxiFY DAGs para workflows complexos |
