---
name: dag-workflow
description: "Workflow baseado em DAG (Directed Acyclic Graph) inspirado no OxiFY (Japão/Rust) e DeerFlow (ByteDance/China). Executa passos em paralelo quando independentes, junta resultados, valida e permite rollback por nó. Substitui execução linear por grafo acíclico dirigido."
category: autonomous-ai-agents
tags: [dag, workflow, paralelo, orquestracao, grafo, neo-hermes]
---

# DAG Workflow — Execução em Grafo com Paralelismo

## Inspiração
- **OxiFY** (cool-japan): Graph-based LLM orchestration em Rust com DAGs type-safe
- **DeerFlow** (ByteDance): Super Agent Harness com sub-agentes paralelos em sandboxes
- **Shannon** (Kocoro-lab/Japan): Swarm V2 com loops paralelos e token budget

## Conceito

Em vez de executar passos em série (linear), o DAG Workflow permite que passos **independentes rodem em paralelo** e passos **dependentes esperem** o resultado do anterior.

```
     [INÍCIO]
        │
        ▼
    [PASSO A] ──────┐
        │           │
        ▼           ▼
    [PASSO B]   [PASSO C]  ← paralelo
        │           │
        └─────┬─────┘
              ▼
          [PASSO D]  ← junção (join)
              │
              ▼
          [VERIFY]
              │
           ✅/❌
```

## Como Usar

### Skill de Exemplo — DAG de Criação de Projeto

```yaml
dag:
  nodes:
    - id: setup
      description: "Criar estrutura de diretórios e config"
      depends_on: []  # raiz
      run: terminal(command="mkdir -p src tests docs")
    
    - id: backend
      description: "Criar API FastAPI"
      depends_on: [setup]  # espera setup
      run: delegate_task(goal="Criar API FastAPI com CRUD")
    
    - id: frontend
      description: "Criar React dashboard"
      depends_on: [setup]  # PARALELO com backend!
      run: delegate_task(goal="Criar dashboard React")
    
    - id: tests
      description: "Testar integração"
      depends_on: [backend, frontend]  # espera AMBOS
      run: terminal(command="pytest tests/")
    
    - id: deploy
      description: "Deploy local"
      depends_on: [tests]
      run: terminal(command="docker-compose up -d")
```

## Implementação no Hermes

### Pseudocódigo do Executor DAG

```python
def executar_dag(nos):
    """Executa nós DAG, respeitando dependências e paralelismo."""
    executados = set()
    pendentes = [n for n in nos if not n.depends_on]  # raízes
    
    while pendentes ou em_andamento:
        # Dispara nós prontos (todas dependências satisfeitas)
        prontos = [n for n in nos if set(n.depends_on).issubset(executados) 
                   and n.id not in executados and n.id not in em_andamento]
        
        # Executa nós independentes EM PARALELO
        for no in prontos:
            em_andamento.add(no.id)
            delegate_task(goal=no.description, background=True)
        
        # Aguarda resultados
        for no in list(em_andamento):
            resultado = verificar_resultado(no.id)
            if resultado.concluido:
                if resultado.ok:
                    executados.add(no.id)
                    em_andamento.remove(no.id)
                else:
                    return falha(no.id, resultado.erro)
    
    return sucesso()
```

## Regras do DAG

1. **Sem ciclos** — o grafo é direcionado e acíclico (verificado antes de executar)
2. **Paralelismo máximo** — nós sem dependência entre si rodam juntos
3. **Barreira de sincronização** — nó de junção espera TODOS os pais
4. **Rollback por nó** — se um nó falha, só os nós dependentes dele são afetados
5. **Evidência por nó** — cada nó reporta seu próprio resultado

## Vantagens vs Execução Linear

| Cenário | Linear | DAG |
|---------|--------|-----|
| 3 passos independentes | 3 turnos sequenciais | **1 turno** (paralelo) |
| Falha no passo 2 | Perde tudo | Só afeta dependentes |
| Adicionar passo | Inserir no meio | Só definir dependência |
| Reexecutar | Tudo de novo | Só o nó falho |

## Inspiração Direta

- **OxiFY**: DAGs type-safe em Rust — validação de dependências em tempo de compilação
- **DeerFlow**: Sub-agentes paralelos em sandboxes — isolamento por nó
- **Shannon**: Swarm V2 com lead agent orquestrando loops paralelos
