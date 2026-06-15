---
name: nemotron-3-ultra
description: "NVIDIA Nemotron 3 Ultra — modelo aberto 550B (55B ativos) com arquitetura híbrida Mamba-Attention, 1M tokens de contexto, otimizado para agentes multipasso e raciocínio agêntico de longa duração."
category: mlops
tags: [auto-gerado, innovation-scanner, nvidia, nemotron, mamba, moe, gguf, agentic]
---

# NVIDIA Nemotron 3 Ultra — Skill Auto-Gerado

## Fonte
Extraído da Edição #006 do TOP OF THE HOUR — IA
Card: "NVIDIA Lança Nemotron 3 Ultra: 550B Parâmetros, 55B Ativos — Modelo Aberto para Agentes de Longa Duração"

## O que é
O NVIDIA Nemotron 3 Ultra é o modelo mais capaz da família Nemotron:
- **550B parâmetros totais**, 55B ativos por token via MoE (Mixture-of-Experts)
- **Arquitetura híbrida Mamba-Attention**: combina state-space models (eficientes em sequências longas) com atenção tradicional (precisa em raciocínio)
- **1 milhão de tokens de contexto** — ideal para agentes multipasso
- **Otimizado para agentes** que planejam, chamam ferramentas e mantêm contexto por centenas de iterações
- **Open weights, dados e receita de treinamento** disponíveis no HuggingFace

**Diferença do Nemotron 3.5 ASR:** O Nemotron 3.5 ASR é um modelo de reconhecimento de fala fine-tunable. O Nemotron 3 Ultra é um modelo geral de raciocínio e agentes — não relacionado a ASR.

## Como implementar no Hermes 2.0

### 1. Inferência com llama.cpp (GGUF quantizado)
O modelo está disponível em GGUF via unsloth, permitindo execução em hardware acessível:

```bash
# Download do GGUF quantizado
huggingface-cli download unsloth/NVIDIA-Nemotron-3-Ultra-550B-A55B-GGUF \
  --include "Q4_K_M/*" --local-dir ./models/nemotron-3-ultra

# Inferência com llama.cpp
llama-cli \
  -m ./models/nemotron-3-ultra/nemotron-3-ultra-q4_k_m.gguf \
  -p "Explique como um agente de IA pode planejar uma tarefa complexa em 5 passos" \
  -n 1024 \
  --ctx-size 32768
```

### 2. Como provider no Hermes (via OpenRouter)
O modelo está disponível via OpenRouter com suporte a 1M tokens de contexto:

```yaml
# config.yaml (provider DeepSeek ou OpenRouter)
providers:
  - name: openrouter
    models:
      - name: nvidia/nemotron-3-ultra
        max_tokens: 32768
```

### 3. Uso com HuggingFace transformers
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "nvidia/Nemotron-3-Ultra-550B-A55B",
    device_map="auto",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained("nvidia/Nemotron-3-Ultra-550B-A55B")

prompt = "Plan the steps to implement a multi-agent system"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=512)
print(tokenizer.decode(outputs[0]))
```

### 4. Para agentes multipasso (caso de uso principal)
```python
# O modelo é otimizado para sessões longas de agente:
# - Mantém contexto por centenas de iterações de tool calls
# - Suporta planejamento hierárquico
# - Eficiente em sequências longas graças ao Mamba-Attention híbrido
```

## Características Técnicas
| Parâmetro | Valor |
|-----------|-------|
| Parâmetros totais | 550B |
| Parâmetros ativos | 55B (por token) |
| Arquitetura | MoE + Mamba-Attention híbrida |
| Contexto máximo | 1.048.576 tokens |
| Intelligence Index | 48 |
| Licença | Open (pesos, dados, receita abertos) |

## Comandos
```bash
# Verificar modelo no HuggingFace
huggingface-cli info nvidia/Nemotron-3-Ultra-550B-A55B

# Download de checkpoint GGUF
huggingface-cli download unsloth/NVIDIA-Nemotron-3-Ultra-550B-A55B-GGUF

# Teste rápido
python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
m = AutoModelForCausalLM.from_pretrained('nvidia/Nemotron-3-Ultra-550B-A55B', trust_remote_code=True)
t = AutoTokenizer.from_pretrained('nvidia/Nemotron-3-Ultra-550B-A55B')
print('Model loaded successfully')
"
```

## Referência
- Technical Report: https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf
- HuggingFace (GGUF): https://huggingface.co/unsloth/NVIDIA-Nemotron-3-Ultra-550B-A55B-GGUF
- OpenRouter: https://openrouter.ai/nvidia
- Fonte original: NVIDIA Research / HuggingFace
