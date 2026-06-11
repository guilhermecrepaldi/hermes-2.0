---
name: agent-reach
description: "CLI for AI agents to read and search Twitter, Reddit, YouTube, and GitHub without API fees — web scraping-based social media access"
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, web-scraping, social-media, research, cli]
---

# Agent-Reach — Social Media CLI for AI Agents

## Fonte
Extraído da Edição #002 do TOP OF THE HOUR — IA
Card: "Agent-Reach: CLI sem API Fees para Ler e Buscar Twitter, Reddit, YouTube e GitHub" (app-002-03)

## O que é
Agent-Reach (26.3k estrelas no GitHub) é uma CLI que dá a agentes de IA acesso visual à internet — lê e busca conteúdo em múltiplas plataformas sociais através de uma única interface, **sem custos de API**:

- Twitter/X
- Reddit
- YouTube
- GitHub
- Bilibili
- XiaoHongShu (小红书)

Usa web scraping inteligente em vez de APIs pagas, eliminando a complexidade de integração com múltiplos provedores.

## Como implementar no Hermes 2.0

### Instalação
```bash
git clone https://github.com/Panniantong/Agent-Reach.git
cd Agent-Reach
pip install -r requirements.txt
pip install -e .
```

### Uso como CLI
```bash
# Buscar tópicos no Twitter
agent-reach search twitter "AI agents" --limit 10

# Buscar trending no Reddit
agent-reach search reddit "machine learning" --sort hot

# Buscar vídeos no YouTube
agent-reach search youtube "Blackwell Ultra" --limit 5

# Buscar repositórios no GitHub
agent-reach search github "llm compression" --sort stars
```

### Uso como biblioteca Python
```python
from agent_reach import AgentReach

ar = AgentReach()
results = ar.search_all(["Twitter", "Reddit", "GitHub"], 
                         query="hermes agent",
                         limit=5)
for platform, posts in results.items():
    for post in posts:
        print(f"[{platform}] {post['title']}: {post['url']}")
```

## Comandos
```bash
agent-reach --help
agent-reach search <platform> <query> [--limit N] [--sort relevance|hot|new]
agent-reach trending twitter
```

## Integração com Hermes
- Use como ferramenta de pesquisa para agentes de investigação e notícias
- Substitui múltiplas APIs pagas (Twitter API, Reddit API, YouTube API)
- Saída estruturada (JSON) facilita parsing por agentes
- Ideal para skills de pesquisa de mercado e monitoramento

## Referência
https://github.com/Panniantong/Agent-Reach
