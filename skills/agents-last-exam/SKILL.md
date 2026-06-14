---
name: agents-last-exam
description: "Agents' Last Exam — UC Berkeley benchmark for evaluating real-world agent capabilities. Tests programming, scientific research, web navigation, and tool use. More relevant than traditional Q&A benchmarks for evaluating agentic capabilities."
category: mlops
tags: [auto-gerado, innovation-scanner, benchmark, evaluation, agents, uc-berkeley]
---

# Agents' Last Exam — Skill Auto-Gerado

## Fonte
Extraído da Edição #001 do TOP OF THE HOUR — IA
Card: "Agents' Last Exam: UC Berkeley Cria Benchmark Definitivo para Capacidades de Agentes de IA"

## O que é
O Agents' Last Exam é um benchmark da UC Berkeley que testa agentes de IA em tarefas do mundo real: programação, pesquisa científica, navegação web, uso de ferramentas. Proposto como substituto para benchmarks tradicionais de Q&A que não refletem capacidades agênticas reais.

## Como implementar no Hermes 2.0
Use o Agents' Last Exam para benchmark do sistema Hermes:

1. **Avaliação periódica:** Execute o benchmark após cada atualização do Hermes para medir regressão
2. **Comparação de providers:** Compare performance de diferentes modelos/providers nas tarefas agenticas
3. **Integração com CI/CD:** Adicione ao pipeline de deploy do Hermes

## Comandos
```bash
# Clonar e executar o benchmark
git clone https://github.com/ucberkeley/agents-last-exam
cd agents-last-exam
pip install -r requirements.txt

# Executar com Hermes
python run_benchmark.py --agent hermes --model deepseek-v4
python run_benchmark.py --agent hermes --model gpt-4o
python run_benchmark.py --report  # gera relatório comparativo
```

## Referência
https://github.com/ucberkeley/agents-last-exam
