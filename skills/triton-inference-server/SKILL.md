---
name: triton-inference-server
description: "NVIDIA Triton Inference Server — production-grade inference serving that improves throughput by 2-5x without changing hardware. Supports multiple frameworks, dynamic batching, and model ensembles. Essential for cost-effective LLM deployment."
category: mlops
tags: [auto-gerado, innovation-scanner, inference-server, nvidia, throughput, cost-optimization]
---

# Triton Inference Server — Skill Auto-Gerado

## Fonte
Extraído da Edição #003 do TOP OF THE HOUR — IA
Card: "Repensando TCO de IA — custo por token, não custo por GPU, é a métrica que importa"

## O que é
NVIDIA Triton Inference Server é um servidor de inferência de produção que melhora throughput em 2-5x sem trocar de hardware, usando:
- **Dynamic batching** — agrupa requests em lotes para maximizar utilização GPU
- **Model ensembles** — pipeline de múltiplos modelos sem latência de rede entre etapas
- **Concurrent model execution** — múltiplos modelos na mesma GPU
- **Framework agnostic** — TensorRT, ONNX, PyTorch, TensorFlow

## Como implementar no Hermes 2.0
Se Hermes usa inferência local via llama.cpp ou vLLM, Triton pode ser uma alternativa para produção:

1. **Substituir backend de inferência:** Configurar Hermes para usar Triton em vez de API direta
2. **Multi-model serving:** Um único Triton servindo múltiplos modelos (chat, code, embedding) na mesma GPU
3. **Custo-por-token otimizado:** Medir TCO real (custo da instância/hora) / (tokens processados/hora)

## Comandos
```bash
# Iniciar Triton com modelo
docker run --gpus all -p 8000:8000 -p 8001:8001 \
  nvcr.io/nvidia/tritonserver:24.12-py3 \
  tritonserver --model-repository=/models

# Configurar Hermes para usar Triton
hermes config set provider.triton.url http://localhost:8000
hermes config set provider.triton.model hermes-llm

# Verificar métricas de throughput
curl localhost:8000/metrics | grep triton_inference_request_duration_us
```

## Referência
https://developer.nvidia.com/triton-inference-server
https://github.com/triton-inference-server/server
