---
name: rdma-mac-cluster
description: "RDMA over Thunderbolt — Apple macOS 26.2 habilita RDMA sobre Thunderbolt para conectar 2-4 Macs via USB-C formando clusters de IA de alto desempenho para inferência e fine-tuning locais"
category: mlops
tags: [auto-gerado, innovation-scanner, apple, rdma, cluster, mac]
---

# RDMA over Thunderbolt — Mac AI Cluster — Skill Auto-Gerado

## Fonte
Extraído da Edição #005 do TOP OF THE HOUR — IA
Card: "Apple macOS 26.2 Habilita RDMA sobre Thunderbolt: Clusters de IA de Alto Desempenho Conectando Macs Via Cabo USB-C"

## O que é
O macOS 26.2 habilita **RDMA** (Remote Direct Memory Access) sobre **Thunderbolt**, permitindo conectar 2 a 4 Macs via cabo USB-C/Thunderbolt para formar **clusters de IA de alto desempenho**. Com RDMA, a memória de um Mac pode ser acessada diretamente por outro sem passar pelo overhead da pilha de rede tradicional, resultando em latência de microssegundos e throughput de dezenas de Gbps.

Ideal para:
- **Inferência distribuída** — dividir modelos grandes entre múltiplos Macs
- **Fine-tuning local** — paralelizar batches em vários dispositivos Apple Silicon
- **Pré-processamento de dados** — distribuir workloads de ETL/EDA

## Como implementar no Hermes 2.0

### 1. Verificar compatibilidade
```bash
# macOS 26.2+ necessário
sw_vers
# Thunderbolt 4 ou 5
system_profiler SPThunderboltDataType | grep "Speed:"
```

### 2. Configurar cluster RDMA
```bash
# Em cada Mac, habilitar RDMA over Thunderbolt
sudo sysctl net.inet.tcp.rdma_enable=1

# Verificar peers detectados
rdma link show
```

### 3. Distribuir inferência com PyTorch
```python
import torch.distributed as dist

# Configurar backend RDMA
dist.init_process_group(
    backend="nccl",  # ou "gloo" com RDMA
    init_method="rdma://192.168.1.100:29500",
    world_size=4,
    rank=0
)

# Dividir modelo entre os Macs
model = LargeModel()
model = torch.nn.parallel.DistributedDataParallel(model)
```

## Comandos
```bash
# Verificar links RDMA
rdma link show
rdma stat show

# Testar latência entre Macs
rdma ping 192.168.1.101

# Benchmark de throughput
rdma bandwidth -t 30 -s 1048576 192.168.1.101
```

## Hardware Necessário
- 2-4 Macs com Apple Silicon (M3/M4 Ultra recomendado)
- Cabo Thunderbolt 4/5 (até 40-80 Gbps)
- macOS 26.2 ou superior

## Referência
- Apple Developer: https://developer.apple.com/macos
- RDMA spec: https://www.rdmaconsortium.org
- Fonte: Apple macOS 26.2 Release Notes
