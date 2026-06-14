---
name: flash-routing
description: "Apple Flash-Routing — inference optimization that runs 20B models entirely on-device by reading parameters directly from flash storage, bypassing DRAM"
category: mlops
tags: [auto-gerado, innovation-scanner, apple, inference, optimization]
---

# Flash-Routing — Skill Auto-Gerado

## Fonte
Extraído da Edição #001 do TOP OF THE HOUR — IA
Card: "Apple Leva 20B Parâmetros para o Dispositivo Sem Tocar na DRAM com Flash-Routing"

## O que é
Flash-Routing é uma técnica de inferência desenvolvida pela Apple que permite executar modelos de IA de até 20 bilhões de parâmetros diretamente em dispositivos móveis **sem jamais carregar os parâmetros completos na DRAM**. Em vez disso, o modelo lê os parâmetros diretamente do armazenamento flash (NAND) conforme necessário, roteando apenas os parâmetros das camadas ativas a cada passo de inferência.

O principal obstáculo para IA on-device sempre foi o tamanho limitado da RAM em dispositivos móveis (tipicamente 6-12GB). Flash-Routing contorna isso transformando o gargalo de largura de banda do flash em um recurso explorável através de roteamento esparso e previsão de acesso.

A técnica é particularmente relevante para:
- Modelos de linguagem grandes (LLMs) rodando localmente
- Agentes de IA que precisam de inferência sem latência de rede
- Dispositivos Apple Silicon com Neural Engine e memória unificada
- Privacidade de dados (inferência nunca sai do dispositivo)

## Como implementar no Hermes 2.0

### 1. Conhecimento para configuração de inferência local
Quando configurar modelos para inferência local via llama.cpp ou outro backend, considere:

- Modelos > 7B normalmente exigem quantização (Q4/Q5) para caber na RAM do dispositivo
- Técnicas como Flash-Routing podem ser exploradas via memory-mapped I/O em sistemas de arquivo
- O conceito de carregar parâmetros sob demanda é similar ao swap de camadas em inferência distribuída

### 2. Inspiração para caching
O princípio do Flash-Routing — carregar apenas os parâmetros necessários — pode ser adaptado para o sistema de skills do Hermes: skills grandes podem ser carregadas sob demanda do disco, usando lazy-loading conforme necessário.

### 3. Uso com Apple Silicon
Se o Hermes estiver rodando em hardware Apple (Mac), o CoreML SDK já tem suporte a flash-routing:
```bash
coremltools.convert(model, 
    compute_precision=coremltools.precision.FLOAT16,
    memory_mode="flash_routing"
)
```

## Comandos
```bash
# Verificar se CoreML SDK suporta flash-routing (macOS only)
xcrun coremlcompiler available-memory-modes

# Monitorar uso de memória flash vs DRAM durante inferência
sudo fs_usage -w -f filesys | grep "mlmodel"
```

## Técnica relacionada
Flash-Routing se relaciona com Memory-Mapped Models e Layer-wise Loading. É o complemento em hardware do que técnicas de quantização fazem em software.

## Referência
- Edição #001, TOP OF THE HOUR — IA
- Apple WWDC CoreML session (2026)
- [`coremltools` documentation](https://coremltools.readme.io/)