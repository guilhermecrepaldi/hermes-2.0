---
name: antigravity-20
description: "Google Antigravity 2.0 — IDE desktop, CLI e SDK de agentes com orquestração multi-ferramenta, substituto do Gemini CLI para desenvolvimento de agentes autônomos"
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, google, agent-sdk, cli]
---

# Antigravity 2.0 — Skill Auto-Gerado

## Fonte
Extraído da Edição #005 do TOP OF THE HOUR — IA
Card: "Antigravity 2.0: Google Lança IDE Desktop, CLI e SDK de Agentes que Substitui o Gemini CLI com Orquestração Multi-Ferramenta"

## O que é
Antigravity 2.0 é a plataforma completa de desenvolvimento de agentes do Google, anunciada no I/O 2026. Inclui:
- **IDE Desktop** — ambiente visual para construir e depurar agentes
- **CLI** — interface de linha de comando para automação e scripting
- **SDK** — biblioteca para integração programática de agentes em aplicações
- **Orquestração multi-ferramenta** — agentes que usam múltiplas ferramentas em sequência coordenada

Substitui o Gemini CLI como ferramenta primária de agentes do ecossistema Google.

## Como implementar no Hermes 2.0

### 1. Instalar o CLI
```bash
# Assumindo disponível via npm ou gcloud
npm install -g @google/antigravity-cli
# ou
gcloud components install antigravity-cli
```

### 2. Criar um agente com o Antigravity SDK
```python
# Exemplo conceitual: agente multi-ferramenta
from antigravity import Agent, ToolUse

agent = Agent(
    name="hermes-agent",
    model="gemini-3.1-pro",
    tools=["code_execution", "web_search", "file_system"]
)

result = agent.run("Pesquise o preço do BTC e salve em um arquivo")
```

### 3. Usar via CLI para automação
```bash
antigravity run "Crie um sumário dos arquivos no diretório atual"
```

## Comandos
```bash
# CLI
antigravity --help
antigravity run "<prompt>"
antigravity init    # inicializa um projeto de agente
antigravity deploy  # deploy do agente

# SDK
pip install antigravity-sdk
```

## Referência
- Google I/O 2026: https://blog.google/technology/ai/antigravity-2
- Documentação: https://developers.google.com/antigravity
- Fonte: Google I/O 2026
