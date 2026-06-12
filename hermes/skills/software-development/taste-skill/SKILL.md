---
name: taste-skill
description: "taste-skill — open-source skill for coding agents that adds style quality to AI outputs, eliminating generic text patterns. Uses few-shot prompting for authentic, non-robotic text generation."
category: software-development
tags: [auto-gerado, innovation-scanner, coding-agents, style, quality, open-source]
---

# taste-skill — Skill Auto-Gerado

## Fonte
Extraído da Edição #002 do TOP OF THE HOUR — IA (app-002-04)
Card: "last30days-skill and taste-skill: Ferramentas para Agentes de IA Mais Inteligentes e com Estilo"

## O que é
taste-skill (41.3k estrelas) é uma skill open-source para coding agents que adiciona "bom gosto" às saídas de IA, eliminando texto genérico e padrões robóticos. Usa few-shot prompting (exemplos no prompt) para produzir outputs mais autênticos, resolvendo o problema de "slop" (texto genérico de IA).

A skill irmã last30days-skill (39.6k estrelas) pesquisa qualquer tópico nos últimos 30 dias em Reddit, X, YouTube, HN e Polymarket.

## Como implementar no Hermes 2.0

```bash
git clone https://github.com/Leonxlnx/taste-skill
cd taste-skill
```

Incluir nos prompts do Hermes:
```
[Aplique taste-skill: prefira linguagem natural e específica. Evite frases como "em constante evolução", "transformador", "revolucionário". Seja direto e técnico.]
```

## Comandos
```bash
# last30days-skill: pesquisa tendências recentes
python last30days.py --topic "fine-tuning LLMs"

# taste-skill: aplicar estilo em texto
python taste.py --input "texto_genérico.md" --style "técnico,direto"
```

## Referência
- https://github.com/Leonxlnx/taste-skill
- https://github.com/Leonxlnx/last30days-skill
- Fonte: GitHub Trending
