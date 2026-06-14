---
name: projectmem
description: "PROJECTMEM — local-first, event-sourced memory architecture for coding agents. Each agent action becomes an immutable event in a local log. The agent 'remembers' by reconstructing state from events. No external API dependencies."
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, memory, event-sourcing, coding-agents, local-first]
---

# PROJECTMEM — Skill Auto-Gerado

## Fonte
Extraído da Edição #002 do TOP OF THE HOUR — IA
Card: "PROJECTMEM: Camada de Memória Local com Event Sourcing para Agentes de Código"

## O que é
PROJECTMEM é uma arquitetura de memória local-first e event-sourced para coding agents. Cada ação do agente vira um evento imutável em um log local. O agente "lembra" reconstruindo estado a partir dos eventos, sem depender de APIs externas.

## Como implementar no Hermes 2.0
Memória para coding agents é um problema crítico no Hermes. PROJECTMEM oferece um design pattern testado:

1. **Event log local:** Cada tool call, terminal output, e decisão do agente vira um evento imutável
2. **Reconstrução de estado:** O agente reconstrói contexto a partir dos eventos (similar ao Hermes session_search)
3. **Persistência entre sessões:** O log de eventos sobrevive entre execuções do agente

## Estrutura de Eventos
```python
@dataclass
class AgentEvent:
    timestamp: float
    agent_id: str
    action_type: str  # 'tool_call', 'decision', 'observation'
    payload: dict
    parent_event: Optional[str]  # para rastrear causalidade
```

## Comandos
```bash
# Inicializar repositório de eventos PROJECTMEM
projectmem init --path ./agent-memory
projectmem log --agent coding-agent --action tool_call --payload '{"tool":"terminal","cmd":"ls"}'
projectmem replay --agent coding-agent --session latest
```

## Referência
arXiv:2606.XXXXX — PROJECTMEM paper
