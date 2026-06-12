---
name: cohere-coding-agent
description: "Cohere Coding Agent — open-source 30B coding agent optimized to run on a single H100 GPU with INT4 quantization. Democratizes access to frontier coding AI."
category: software-development
tags: [auto-gerado, innovation-scanner, coding-agent, cohere, open-source]
---

# Cohere Coding Agent — Skill Auto-Gerado

## Fonte
Extraído da Edição #001 do TOP OF THE HOUR — IA
Card: "Cohere Abre o Código de Agente de Programação de 30B que Roda em uma Única H100"

## O que é
A Cohere open-sourçou um agente de programação de 30B parâmetros especializado em codificação, otimizado para rodar em uma única GPU H100 com quantização INT4. Democratiza o acesso a agentes de codificação de ponta — qualquer desenvolvedor pode rodar localmente sem depender de APIs externas.

## Como implementar no Hermes 2.0
O agente pode ser baixado do HuggingFace e executado localmente via llama.cpp ou vLLM:

```bash
# Baixar o modelo
huggingface-cli download CohereForAI/coding-agent-30b

# Executar com llama.cpp (após converter para GGUF)
./llama-cli -m coding-agent-30b.Q4_K_M.gguf -p "def fibonacci(n):"
```

Via Python:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "CohereForAI/coding-agent-30b",
    load_in_4bit=True,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("CohereForAI/coding-agent-30b")
```

## Comandos
```bash
# Download via HuggingFace
huggingface-cli download CohereForAI/coding-agent-30b

# Ou via Ollama (se disponível)
ollama pull cohere-coding-agent
```

## Referência
- https://huggingface.co/CohereForAI
- https://venturebeat.com/category/ai/
- Fonte: VentureBeat
