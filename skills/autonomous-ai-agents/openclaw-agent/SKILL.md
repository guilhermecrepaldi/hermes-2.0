---
name: openclaw-agent
description: "OpenClaw — plataforma de agentes de código aberto com suporte a múltiplos providers (Anthropic Claude, OpenAI, DeepSeek) para automação programática de CI/CD e scripts"
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, openclaw, multi-provider, agent-cli]
---

# OpenClaw — Skill Auto-Gerado

## Fonte
Extraído da Edição #006 do TOP OF THE HOUR — IA
Card: "Anthropic Reinstaura OpenClaw e Uso de Agentes de Terceiros no Claude — Com Ressalvas de Metering"

## O que é
OpenClaw é uma plataforma de agentes de código aberto que funciona com **múltiplos provedores de LLM**:
- **Anthropic Claude** (via Agent SDK)
- **OpenAI** (GPT models)
- **DeepSeek** (DeepSeek models)

Permite automação programática de pipelines CI/CD, execução de scripts autônomos e integração com GitHub Actions. Após a Anthropic reverter sua decisão de bloquear agentes de terceiros, OpenClaw agora opera sob o novo sistema de crédito Agent SDK, mas ganhou independência ao suportar múltiplos backends.

## Como implementar no Hermes 2.0

### 1. Instalação
```bash
# Via pip
pip install openclaw

# Ou via npm
npm install -g openclaw
```

### 2. Configurar providers
```bash
# Configurar chaves de API
openclaw config set anthropic.api_key $ANTHROPIC_API_KEY
openclaw config set openai.api_key $OPENAI_API_KEY
openclaw config set deepseek.api_key $DEEPSEEK_API_KEY

# Provider padrão
openclaw config set default_provider deepseek
```

### 3. Usar em scripts e CI/CD
```bash
# Executar comando via agente
openclaw run "Refatore este arquivo: main.py" --model deepseek

# Em GitHub Actions
openclaw run "Revise este PR" --github-token ${{ secrets.GITHUB_TOKEN }}
```

### 4. Integrar com Python
```python
from openclaw import Agent

agent = Agent(
    provider="deepseek",  # ou "anthropic", "openai"
    model="deepseek-v4"
)

result = agent.run("Analise o código neste diretório e sugira melhorias")
print(result)
```

## Comandos
```bash
# CLI
openclaw --help
openclaw run "<prompt>" [--model <model>]
openclaw config [set|get|list]
openclaw providers   # lista providers configurados

# Modo interativo
openclaw
```

## Comparação com Hermes Tools
O OpenClaw complementa mas NÃO substitui o sistema de agentes nativo do Hermes:
- **Hermes Agent**: orquestração interna, skills, memória, ferramentas
- **OpenClaw**: executor de agentes multi-provider para tarefas externas

Use OpenClaw quando precisar delegar tarefas a um modelo específico não configurado como provider primário do Hermes.

## Referência
- GitHub: https://github.com/openclaw/openclaw
- Documentação: https://openclaw.dev
- Fonte: VentureBeat / Anthropic Blog
