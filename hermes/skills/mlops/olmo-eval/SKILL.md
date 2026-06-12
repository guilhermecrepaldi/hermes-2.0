---
name: olmo-eval
description: "Allen AI olmo-eval — open-source evaluation workbench integrated into the development cycle. Define custom evaluation suites in YAML and run benchmarks automatically during training to detect regression and catastrophic forgetting."
category: mlops
tags: [auto-gerado, innovation-scanner, evaluation, allen-ai, open-source, benchmarking]
---

# olmo-eval — Workbench de Avaliação para Ciclo de Desenvolvimento

## Fonte
Extraído da Edição #003 do TOP OF THE HOUR — IA (12 JUN 2026)
Card: "olmo-eval — Allen AI lança workbench de avaliação open-source para o ciclo de desenvolvimento"

## O que é
olmo-eval é um workbench de avaliação open-source do Allen Institute for AI (AI2) integrado ao ciclo de desenvolvimento de modelos. Permite definir suites de avaliação customizadas em YAML e executá-las automaticamente durante o treinamento — cada checkpoint é avaliado contra benchmarks, detectando regressão (catastrophic forgetting) antes de prosseguir.

## Como implementar no Hermes 2.0
Pode ser usado como ferramenta de validação contínua para modelos que o Hermes gerencia localmente:

1. **Definir evaluation suite** em YAML com os benchmarks relevantes
2. **Integrar ao loop de treinamento** — cada checkpoint é avaliado automaticamente
3. **Detectar regressão** — se métricas caírem abaixo do threshold, o treinamento é pausado
4. **Gerar relatórios** de performance comparativa entre checkpoints

## Comandos
```bash
# Clonar
git clone https://github.com/allenai/olmo-eval
cd olmo-eval

# Instalar
pip install -e .

# Executar evaluation suite
olmo-eval run --config configs/my_eval.yaml --model /path/to/checkpoint
```

## Referência
https://huggingface.co/blog/olmo-eval
