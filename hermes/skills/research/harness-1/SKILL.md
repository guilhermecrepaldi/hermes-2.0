---
name: harness-1
description: "Harness-1 — open-source search agent that surpasses GPT-5.4 in research benchmarks with dynamic source discovery and multi-agent collaboration"
category: research
tags: [auto-gerado, innovation-scanner, search, research, rag, agents]
---

# Harness-1 — Skill Auto-Gerado

## Fonte
Extraído da Edição #001 do TOP OF THE HOUR — IA
Card: "Harness-1: Agente de Busca Open-Source Supera GPT-5.4 em Benchmarks de Pesquisa"

## O que é
Harness-1 é um agente de busca open-source que supera o GPT-5.4 em benchmarks de pesquisa. Em vez de depender de uma base fixa de conhecimento, ele descobre dinamicamente novos ambientes de busca e usa múltiplos agentes especializados que colaboram para encontrar e sintetizar informação. Uma evolução importante sobre RAG estático tradicional.

## Como implementar no Hermes 2.0
Clone e execute o agente:

```bash
git clone https://github.com/[org]/harness-1
cd harness-1
pip install -r requirements.txt

# Executar busca
python run.py --query "últimos avanços em RL para LLMs"
```

## Comandos
```bash
# Busca com descoberta dinâmica de fontes
python run.py --query "sua pergunta" --sources "arxiv,github,paperswithcode"

# Modo agente multi-colaborativo
python run.py --query "pesquisa" --multi-agent
```

## Referência
- https://github.com/[org]/harness-1
- Fonte: VentureBeat
