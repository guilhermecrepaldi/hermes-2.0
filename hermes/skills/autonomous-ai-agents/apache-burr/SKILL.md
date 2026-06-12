---
name: apache-burr
description: "Apache Burr — open-source framework for building reliable, auditable AI agents with built-in traceability. Each agent step is recorded in an immutable execution graph."
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, agents, framework, observability]
---

# Apache Burr — Skill Auto-Gerado

## Fonte
Extraído da Edição #001 do TOP OF THE HOUR — IA
Card: "Apache Burr: Framework Open-Source para Agentes de IA Confiáveis e Auditáveis"

## O que é
Apache Burr é um framework open-source da Apache Software Foundation para construir agentes de IA confiáveis com rastreabilidade embutida. Cada passo do agente é registrado em um grafo de execução imutável, permitindo auditoria completa — ideal para aplicações enterprise em finanças, saúde e jurídico.

Alternativa a LangChain e CrewAI com foco em confiabilidade e observabilidade.

## Como implementar no Hermes 2.0
Instalação via pip:

```bash
pip install burr
```

Uso básico:
```python
from burr.core import Agent, Step, Execution

# Define um agente auditável
agent = Agent(
    name="hermes-agent",
    steps=[
        Step("plan", action="planejar"),
        Step("execute", action="executar"),
        Step("verify", action="verificar")
    ]
)

# Executa com rastreabilidade total
execution = agent.run(input="tarefa")
print(execution.graph)  # Grafo imutável de execução
```

## Comandos
```bash
# Instalar
pip install burr

# Ver exemplos
python -m burr.examples.simple_agent
```

## Referência
- https://burr.apache.org/
- https://github.com/apache/burr
- Fonte: Hacker News
