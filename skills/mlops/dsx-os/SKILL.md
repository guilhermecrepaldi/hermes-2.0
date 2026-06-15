---
name: dsx-os
description: "DSX OS — sistema operacional modular open-source para AI Factories (fábricas de dados de IA) com workload scheduler MaxLP, lançado por Hugging Face e Sentient Foundation"
category: mlops
tags: [auto-gerado, innovation-scanner, ai-factory, huggingface, open-source]
---

# DSX OS — Skill Auto-Gerado

## Fonte
Extraído da Edição #005 do TOP OF THE HOUR — IA
Card: "Hugging Face e Sentient Lançam DSX OS Open-Source: Sistema Operacional Modular para AI Factories com Eficiência Energética"

## O que é
DSX OS é um sistema operacional modular open-source para operação de **AI Factories** (fábricas de dados de IA), desenvolvido pela Hugging Face em parceria com a Sentient Foundation. Inclui o **DSX MaxLP** (Maximized Linear Programming) workload scheduler para orquestração eficiente de workloads de treinamento e inferência em larga escala, com foco em eficiência energética e utilização de GPU.

## Como implementar no Hermes 2.0

### 1. Explorar o repositório
```bash
git clone https://github.com/huggingface/dsx-os
cd dsx-os
```

### 2. Verificar dependências
```bash
# Requer Python 3.11+ e drivers NVIDIA
python -c "import torch; print(torch.cuda.is_available())"
```

### 3. Integrar com o pipeline do Hermes
O DSX OS pode ser usado como backend de orquestração de workloads para:
- Agendamento de inferência em lote
- Gerenciamento de filas de requests
- Otimização energética de GPUs

```python
# Exemplo conceitual de integração
from dsx_os import WorkloadScheduler

scheduler = WorkloadScheduler(
    max_gpus=4,
    policy="maxlp"  # MaxLP scheduling
)
```

## Comandos
```bash
# Clone o repositório
git clone https://github.com/huggingface/dsx-os

# Documentação
# https://huggingface.co/blog/dsx-os
```

## Referência
- Hugging Face Blog: https://huggingface.co/blog
- Sentient Foundation: https://sentient.foundation
- Fonte: Hugging Face e Sentient Foundation
