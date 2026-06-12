---
name: diffusiongemma
description: "DiffusionGemma — Google DeepMind's diffusion-based language model that generates text 4× faster than autoregressive transformers. Parallel text generation for low-latency applications."
category: mlops
tags: [auto-gerado, innovation-scanner, diffusion, llm, google, deepmind]
---

# DiffusionGemma — Skill Auto-Gerado

## Fonte
Extraído da Edição #001 do TOP OF THE HOUR — IA
Card: "DiffusionGemma: Geração de Texto 4x Mais Rápida com Modelos de Difusão Acelerados pela NVIDIA"

## O que é
DiffusionGemma é uma família de modelos de linguagem do Google DeepMind baseados em difusão, que geram texto 4× mais rápido que transformers autorregressivos equivalentes. Enquanto modelos como GPT-4 e Claude geram texto token por token (sequencial), DiffusionGemma gera o texto completo em paralelo — como o Stable Diffusion faz com imagens. NVIDIA acelerou para GPUs RTX via programa RTX AI Garage.

## Como implementar no Hermes 2.0

```bash
# Instalar dependências
pip install transformers torch accelerate

# Carregar o modelo
from transformers import AutoModelForDiffusion, AutoTokenizer

model = AutoModelForDiffusion.from_pretrained("google/diffusion-gemma-2b")
tokenizer = AutoTokenizer.from_pretrained("google/diffusion-gemma-2b")

# Geração paralela (4x mais rápida)
prompt = "Explique o que é um transformer em uma frase:"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, num_inference_steps=4)
text = tokenizer.decode(outputs[0])
```

## Comandos
```bash
# Executar via RTX AI Garage (NVIDIA)
# Testar demo online em huggingface.co/google/diffusion-gemma
pip install git+https://github.com/google/diffusion-gemma
```

## Referência
- https://blog.google/technology/ai/google-deepmind-gemma-diffusion/
- https://huggingface.co/google
- https://blogs.nvidia.com/blog/rtx-ai-garage-local-gemma-diffusion/
- Fonte: Google AI Blog
