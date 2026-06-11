---
name: mempalace
description: "Open-source memory system for AI agents with vector store, hierarchical summarization, and intelligent caching — top benchmarks for agentic memory"
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, memory, agents, vector-store, context]
---

# MemPalace — Memory System for AI Agents

## Fonte
Extraído da Edição #002 do TOP OF THE HOUR — IA
Card: "MemPalace: Sistema de Memória Open-Source com Melhores Benchmarks para Agentes de IA" (arc-002-13)

## O que é
MemPalace é um sistema de memória open-source para agentes de IA que oferece:
- **Persistência de longo prazo** — agentes mantêm contexto entre sessões sem estourar a janela de contexto
- **Recuperação semântica** — busca por similaridade em memórias passadas
- **Sumarização hierárquica** — compressão inteligente do histórico
- **Cache inteligente** — reutilização de resultados frequentes

Resultados superiores em benchmarks de memória agêntica.

## Como implementar no Hermes 2.0

### Instalação
```bash
git clone https://github.com/MemPalace/mempalace.git
cd mempalace
pip install -r requirements.txt
pip install -e .
```

### Uso básico
```python
from mempalace import MemPalace

# Inicializa o sistema de memória
memory = MemPalace(
    storage_path="./agent_memory",
    vector_dim=768,  # dimensão do embedding
    summarization="hierarchical"
)

# Salva memória de uma interação
memory.store(
    session_id="session_123",
    content="Resolvemos o bug do KV Cache com a técnica ReasonAlloc",
    metadata={"type": "debug", "severity": "high"}
)

# Recupera memórias relevantes
results = memory.retrieve(
    query="problemas de cache",
    limit=5
)
for r in results:
    print(f"[{r['timestamp']}] {r['content']} (score: {r['score']})")
```

### Hierarchical summarization
```python
# MemPalace automaticamente sumariza memórias antigas
# em níveis hierárquicos de abstração
summary = memory.summarize(session_id="session_123")
# Retorna: Resumo de alto nível das interações anteriores
```

## Comandos
```bash
mempalace --help
mempalace init --path ./memory_store
mempalace query "qual técnica de compressão usamos?"
mempalace stats  # estatísticas do armazenamento
```

## Integração com Hermes
- Substitui ou complementa o sistema de memória atual do Hermes
- Resolve o gargalo de janela de contexto para agentes de longa duração
- Vector store nativo permite busca semântica eficiente
- Hierarchical summarization mantém apenas o essencial

## Referência
https://github.com/MemPalace/mempalace
