---
name: token-budget-control
description: "Controle de orçamento de tokens por agente/sub-agente. Inspirado no Shannon (Kocoro-lab/Japan) Token Budget Control e no roteador-economico do Hermes. Define limite de gasto por tarefa, prioriza modelos baratos e corta quando estoura."
category: autonomous-ai-agents
tags: [economia, tokens, budget, governanca, auditoria, neo-hermes]
---

# Token Budget Control — Orçamento de Tokens por Agente

## Inspiração
- **Shannon** (Kocoro-lab/Japan): Token Budget Control nativo — cada agente tem orçamento, estourou = pausa
- **DeepSeek V4 Flash**: $0.15/1M tokens — modelo mais barato do mercado
- **Hermes `roteador-economico`**: Já temos roteamento inteligente

## Conceito

Cada tarefa tem um **orçamento de tokens** (budget). Se o sub-agente gastar mais que o permitido, ele é pausado e o orçamento é renegociado.

```
[TAREFA] → Orçamento: 10K tokens
  ├── Arquiteto: 2K tokens (20%)
  ├── Revisor: 1K tokens (10%)
  ├── Executor: 5K tokens (50%)
  ├── Auditor: 1K tokens (10%)
  └── Reserva:  1K tokens (10%)
```

## Níveis de Budget

| Nível | Tokens/Tarefa | Modelo | Custo | Uso |
|-------|:------------:|--------|:----:|-----|
| **Econômico** | 5K | DeepSeek V4 Flash | $0.00075 | Tarefas simples, CRUD, leitura |
| **Normal** | 15K | DeepSeek V4 Flash | $0.00225 | Tarefas médias, debugging |
| **Reflexão** | 30K | DeepSeek V4 Flash | $0.00450 | Conselho de IAs, arquitetura |
| **Profundo** | 100K | DeepSeek V4 Pro | $0.05 | Pesquisa, análise complexa |

**Economia Real**: Uma tarefa Normal custa **$0.002** = **R$0.01**. 500 tarefas/mês = **R$5.00**.

## Implementação no Hermes

### Config de Budget (skill)

```yaml
budget:
  nivel: normal              # economico | normal | reflexao | profundo
  max_tokens_por_chamada: 5000
  max_tokens_por_tarefa: 15000
  modelo: deepseek/deepseek-v4-flash
  modelo_pro: deepseek/deepseek-v4-flash  # só se necessário
  alerta_em: 80%             # alerta quando gastou 80%
  cortar_em: 100%            # corta quando estourar
  modo: soft                 # soft=alerta | hard=corta execução
```

### Tracking de Gasto

```python
# Rastrear gasto de tokens por tarefa
import json
from datetime import datetime

HISTORICO = "~/.hermes/token_budget_history.json"

def registrar_gasto(tarefa_id, agente, tokens_input, tokens_output):
    entrada = {
        "tarefa_id": tarefa_id,
        "agente": agente,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "tokens_total": tokens_input + tokens_output,
        "custo": (tokens_input + tokens_output) * 0.00000015,  # $0.15/1M
        "timestamp": datetime.now().isoformat()
    }
    # Salvar no histórico
    with open(HISTORICO, "a") as f:
        f.write(json.dumps(entrada) + "\n")
    return entrada

def verificar_budget(tarefa_id, max_tokens=15000):
    """Verifica se a tarefa já estourou o orçamento."""
    total = 0
    for linha in open(HISTORICO):
        entrada = json.loads(linha)
        if entrada["tarefa_id"] == tarefa_id:
            total += entrada["tokens_total"]
    return {
        "gasto": total,
        "limite": max_tokens,
        "percentual": (total / max_tokens) * 100,
        "estourou": total >= max_tokens
    }
```

## Regras de Budget

1. **DeepSeek V4 Flash é o padrão ABSOLUTO** — $0.15/1M
2. **Cada sub-agente tem seu próprio budget** — não compartilha
3. **Soft alerta** aos 80% — avisa, mas não corta
4. **Hard cutoff** aos 100% — pausa o agente e pede decisão
5. **Reserva de 10%** para cada tarefa — imprevistos
6. **Histórico persistente** — sabe quanto gastou por tarefa/mês

## Tabela de Custo por Tarefa Típica

| Tarefa | Tokens | Custo | Nível |
|--------|:-----:|:----:|-------|
| `ls` / `read_file` | 500 | $0.000075 | Econômico |
| Editar arquivo | 2K | $0.00030 | Econômico |
| CRUD simples | 5K | $0.00075 | Econômico |
| Refatorar módulo | 10K | $0.00150 | Normal |
| Debugging complexo | 15K | $0.00225 | Normal |
| Conselho de IAs (4 agentes) | 20K | $0.00300 | Reflexão |
| Pesquisa + análise | 50K | $0.00750 | Profundo |

**Custo médio por dia (20 tarefas): ~$0.03 → ~R$0.15 → ~R$4,50/mês**

## Como Ativar

```bash
# Carregar a skill
skill_view(name='token-budget-control')

# A skill ajusta automaticamente:
# 1. Define orçamento baseado na tarefa
# 2. Monitora gasto em tempo real
# 3. Alerta/corta quando necessário
# 4. Registra histórico para analytics
```
