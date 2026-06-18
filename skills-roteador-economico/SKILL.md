---
name: roteador-economico
description: "Seleciona o modelo mais barato que ainda resolve a tarefa. DeepSeek V4 Flash para 95% das tarefas. Só sobe para reasoning caro quando estritamente necessário. Economia de 99x vs Claude Opus."
category: software-development
tags: [economia, roteamento, deepseek, custo, provider]
---

# Roteador Econômico — Máximo Resultado, Mínimo Custo

## Modelo Atual
- **Provider**: DeepSeek
- **Modelo**: `deepseek/deepseek-v4-flash`
- **Custo**: ~$0.15/1M tokens
- **Contexto**: 128K tokens

## Custo Comparativo

| Modelo | Custo/1M tokens input | Custo/1M tokens output | Custo Relativo |
|--------|:-------------------:|:--------------------:|:------------:|
| DeepSeek V4 Flash | $0.15 | $0.15 | **1x** ✅ |
| DeepSeek V4 Pro | $0.45 | $1.20 | 3-8x |
| Claude Sonnet 4.6 | $3.00 | $15.00 | 20-100x |
| Claude Opus 4.8 | $15.00 | $75.00 | 100-500x |
| GPT-5 | $30.00 | $60.00 | 200-400x |
| GPT-5.5 | $50.00 | $150.00 | 330-1000x |

## Matriz de Decisão

### Fique no DeepSeek V4 Flash (95% dos casos)
- ✅ Leitura de arquivos (`read_file`, `grep`)
- ✅ Edição de código simples (CRUD, boilerplate, CSS)
- ✅ Refatoração moderada (renomear, extrair função)
- ✅ Testes (unitários, integração)
- ✅ Comandos de terminal (instalar, configurar, build)
- ✅ Pesquisa web e extração
- ✅ Debugging comum (erro de sintaxe, import, lógica simples)
- ✅ Git (commit, branch, merge simples)
- ✅ Scripts Python/JS/Shell
- ✅ Documentação (README, comentários, relatórios)
- ✅ Arquitetura e planejamento de projetos
- ✅ CRUD completo (API, frontend, banco)

### Suba para DeepSeek V4 Pro ou equivalente (5% dos casos)
- ⚠️ Matemática complexa, algoritmos avançados
- ⚠️ Código muito intrincado (1K+ linhas num arquivo)
- ⚠️ Debugging de race condition, deadlock, memory leak
- ⚠️ Otimização de performance (query plans, profiling)
- ⚠️ System design de larga escala

### NUNCA suba para Claude/GPT (a menos que explicitamente pedido)
- ❌ DeepSeek cobre TUDO que precisamos
- ❌ A diferença de qualidade não justifica 100x+ o custo
- ❌ Se uma tarefa falhar, tente `auto-healing` antes de trocar de modelo

## Configuração no config.yaml

```yaml
model:
  default: deepseek/deepseek-v4-flash
  provider: deepseek
  context_length: 128000

delegation:
  model: deepseek/deepseek-v4-flash
  provider: deepseek
  max_iterations: 50
  reasoning_effort: low  # não precisa de reasoning pesado em subagentes

# Auxiliares econômicos
auxiliary:
  vision:
    provider: openrouter
    model: qwen/qwen-vl-plus  # $0.15/1M — barato para visão
  compression:
    provider: deepseek
    model: deepseek/deepseek-v4-flash
```

## Economia Estimada

| Cenário | Por mês |
|---------|--------|
| 1000 chamadas/dia, média 500 tokens/call | ~$2.25/mês |
| 2000 chamadas/dia, média 1000 tokens/call | ~$9.00/mês |
| Uso intenso (5000 chamadas/dia, 2000 tokens/call) | ~$45.00/mês |

**vs Claude Opus para o mesmo volume:** $9.000/mês

## Regras de Ouro
1. **DeepSeek V4 Flash é o padrão ABSOLUTO**
2. Só cogite outro modelo se a tarefa falhar 3x no DeepSeek
3. Quando falhar, tente `auto-healing` antes de trocar de modelo
4. Prefira 3 chamadas DeepSeek a 1 chamada Claude
