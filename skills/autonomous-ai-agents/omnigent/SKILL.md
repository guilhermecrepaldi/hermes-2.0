---
name: omnigent
description: "Databricks Omnigent — meta-harness open-source para orquestração, composição e governança de múltiplos agentes de código (Claude Code, Codex, OpenCode, Gemini CLI) em um único pipeline"
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, hermes-2.0, agent-orchestration, databricks]
---

# Omnigent — Meta-Harness para Orquestração de Agentes de Código

## Fonte
Extraído da Edição #005 do TOP OF THE HOUR — IA
Card: "Databricks Libera Omnigent como Open-Source — Meta-Harness que Orquestra Agentes entre Claude Code e Outros CLI"

## O que é
Omnigent é uma meta-ferramenta open-source da Databricks que compõe, governa e compartilha agentes de IA através de diferentes CLIs de agentes de código (Claude Code, Codex, OpenCode, Gemini CLI). Ele permite definir agentes especializados como "resources" em um arquivo de configuração YAML que colaboram automaticamente em pipelines com auditoria e governança embutidas.

## Como implementar no Hermes 2.0
1. Clone o repositório: `git clone https://github.com/omnigent-ai/omnigent.git`
2. Instale dependências: `cd omnigent && pip install -e .`
3. Configure agents em um arquivo `omnigent.yaml`:
   ```yaml
   agents:
     reviewer:
       cli: claude-code
       role: "code review"
     tester:
       cli: opencode
       role: "run tests and report"
     deployer:
       cli: codex
       role: "deploy to staging"
   ```
4. Execute: `omnigent run --pipeline review-test-deploy`

## Comandos
```bash
# Instalação
pip install omnigent
# ou
git clone https://github.com/omnigent-ai/omnigent.git && cd omnigent && pip install -e .

# Executar pipeline definido em omnigent.yaml
omnigent run --pipeline <nome>

# Listar agentes disponíveis
omnigent list

# Compartilhar agente com time
omnigent share --agent <nome>
```

## Integração com Hermes
O Hermes pode usar Omnigent como um delegator inteligente: em vez de chamar um agente específico, o Hermes define uma pipeline Omnigent que orquestra múltiplos agentes de código para tarefas complexas (ex: code review → tests → deploy).

## Referência
- Repositório: https://github.com/omnigent-ai/omnigent
- Blog Databricks: https://www.databricks.com/blog/introducing-omnigent-meta-harness-combine-control-and-share-your-agents
