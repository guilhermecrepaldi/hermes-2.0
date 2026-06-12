---
name: mimo-code
description: "Xiaomi MiMo Code — open-source coding agent harness with persistent memory that beats Claude Code on 200+ step tasks. Solves degradation in long coding sessions by maintaining state between stages."
category: software-development
tags: [auto-gerado, innovation-scanner, coding-agent, xiaomi, open-source, memory]
---

# MiMo Code — Agente de Codificação com Memória Persistente

## Fonte
Extraído da Edição #003 do TOP OF THE HOUR — IA (12 JUN 2026)
Card: "Xiaomi MiMo Code — agente de codificação open-source supera Claude Code em >200 etapas"

## O que é
MiMo Code é um harness agêntico open-source da Xiaomi para codificação. Seu diferencial é um sistema de memória persistente que mantém estado entre etapas, resolvendo o problema de degradação em tarefas longas de código (200+ etapas). Supera o Claude Code em cenários multi-arquivo e tarefas complexas.

## Como implementar no Hermes 2.0
Pode ser usado como backend de coding agent alternativo:

1. **Configurar como motor de codificação** para tarefas de automação de código
2. **Aproveitar memória persistente** para projetos com mais de 50 arquivos
3. **Integrar com o sistema de skills** do Hermes para tarefas de refatoração

## Comandos
```bash
# Clonar
git clone https://github.com/xiaomi/mimo-code
cd mimo-code

# Instalar dependências
pip install -r requirements.txt

# Executar tarefa de codificação
python run.py --task "refactor module X" --memory-persist
```

## Referência
https://venturebeat.com/ai/xiaomi-mimo-code-beats-claude-code/
