---
name: openenv
description: "OpenEnv — open-source environment for Agentic Reinforcement Learning. Standardized environments for training agents that browse the web, use APIs, and execute code via RL."
category: data-science
tags: [auto-gerado, innovation-scanner, reinforcement-learning, agents, training, rl]
---

# OpenEnv — Skill Auto-Gerado

## Fonte
Extraído da Edição #002 do TOP OF THE HOUR — IA (arc-002-08)
Card: "OpenEnv: Ambiente Open-Source para Aprendizado por Reforço de Agentes com Apoio da Comunidade"

## O que é
OpenEnv é um ambiente open-source para RL Agêntico (aprendizado por reforço aplicado a agentes de IA). Oferece ambientes padronizados para treinar agentes que navegam na web, usam APIs e executam código. Recebeu apoio significativo da comunidade, estabelecendo-se como referência para treinar agentes com RL em ambientes padronizados.

## Como implementar no Hermes 2.0

```bash
git clone https://github.com/[org]/openenv
cd openenv
pip install -e .
```

Uso básico:
```python
import openenv

# Ambiente de navegação web
env = openenv.make("WebNav-v0")
obs = env.reset()
for step in range(100):
    action = agent.act(obs)  # seu policy
    obs, reward, done, info = env.step(action)
    if done: break
```

## Comandos
```bash
# Listar ambientes disponíveis
python -m openenv.list

# Treinar agente em ambiente web
python train.py --env WebNav-v0 --algorithm ppo
```

## Referência
- https://huggingface.co/blog/openenv-agentic-rl
- Fonte: HuggingFace Blog
