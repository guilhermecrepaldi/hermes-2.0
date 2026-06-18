---
name: auto-assembly-workflow
description: "Auto-Assembly Workflow — descreva o objetivo em linguagem natural e o sistema monta automaticamente o workflow multi-agente ideal. Inspirado no EvoAgentX (China) que 'monta workflows sozinho' e no DeerFlow Super Agent Harness."
category: autonomous-ai-agents
tags: [auto-assembly, workflow, evoagentx, deerflow, autonomo, neo-hermes]
---

# Auto-Assembly Workflow — Monte o Workflow Automaticamente

## Inspiração
- **EvoAgentX** (China, 3.1K⭐): "Descreva o objetivo → ele monta automaticamente o workflow multi-agente"
- **DeerFlow** (ByteDance, 37K⭐): "Super Agent Harness que orquestra sub-agentes, memória e sandboxes"
- **Shannon** (Kocoro-lab/Japan): "Multi-strategy orchestration — escolhe a estratégia certa pra cada tarefa"

## Conceito

> Você descreve o objetivo em linguagem natural. O sistema **analisa a tarefa**, **monta o workflow ideal** (escolhendo skills, papéis, DAG) e **executa**.

```
"Quero criar uma API FastAPI com testes e deploy"

  │
  ▼

[Auto-Assembly Analyzer]
  ├── Identifica: projeto novo, precisa de CRUD, testes, deploy
  ├── Skills necessárias: auto-executor, dag-workflow, conselho-ias
  ├── Papéis: Arquiteto + Executor + Revisor
  ├── DAG: setup → (backend || frontend) → tests → deploy
  └── Budget: 15K tokens (normal)

  │
  ▼

[Conselho de IAs] aprova o workflow
  │
  ▼

[DAG Workflow] executa os passos
  │
  ▼

[Token Budget] monitora gastos
  │
  ▼

[Resultado] API criada, testada, no ar
```

## Como Funciona

### Fase 1 — Análise da Tarefa

O Auto-Assembly analisa a tarefa e classifica:

| Tipo de Tarefa | Skills Necessárias | Papéis | DAG | Budget |
|---------------|-------------------|--------|-----|--------|
| **CRUD simples** | auto-executor | Executor | Linear | Econômico |
| **Projeto novo** | auto-executor + conselho-ias | Arquiteto + Executor + Revisor | DAG | Normal |
| **Refatoração** | auto-executor + auto-healing + conselho-ias | Arquiteto + Revisor + Executor + Auditor | DAG | Reflexão |
| **Pesquisa** | conselho-ias + web | Arquiteto + Revisor | Paralelo | Profundo |
| **Bug fix** | auto-executor + auto-healing | Executor + Revisor | Linear | Econômico |
| **Deploy** | auto-executor | Executor + Auditor | Linear | Normal |
| **Conselho complexo** | conselho-ias + dag-workflow | Todos 4 | DAG + Votação | Profundo |

### Fase 2 — Montagem

```python
def montar_workflow(tarefa):
    """Analisa a tarefa e monta o workflow ideal."""
    tipo = classificar_tarefa(tarefa)
    
    workflow = {
        "skills": tipo["skills"],
        "papeis": tipo["papeis"],
        "dag": tipo["dag"],
        "budget": tipo["budget"],
        "modelo": "deepseek/deepseek-v4-flash"
    }
    
    # Apresenta o plano pro usuário
    print(f"📋 Workflow montado para: {tarefa[:60]}...")
    print(f"   Skills: {', '.join(workflow['skills'])}")
    print(f"   Papéis: {', '.join(workflow['papeis'])}")
    print(f"   Budget: {workflow['budget']}")
    print(f"   Modelo: {workflow['modelo']}")
    
    return workflow
```

### Fase 3 — Execução

```python
def executar_workflow(workflow, tarefa):
    skills = [skill_view(name=s) for s in workflow["skills"]]
    
    if "conselho-ias" in workflow["skills"]:
        # Passa pelo conselho primeiro
        return conselho_deliberar(tarefa)
    
    if "dag-workflow" in workflow["skills"]:
        # Executa como DAG paralelo
        return dag_executar(tarefa)
    
    # Fallback: auto-executor linear
    return auto_executor_executar(tarefa)
```

## Tabela de Classificação

| Palavra-chave na Tarefa | Tipo | Ação |
|------------------------|------|------|
| "criar", "novo", "iniciar" | Projeto novo | Conselho + DAG |
| "refatorar", "migrar", "otimizar" | Refatoração | Conselho + DAG + Auditor |
| "corrigir", "bug", "erro", "fix" | Bug fix | Auto-healing + Revisor |
| "pesquisar", "investigar", "analisar" | Pesquisa | Web + Conselho |
| "deploy", "publicar", "subir" | Deploy | Executor + Auditor |
| "testar", "teste" | Testes | Executor + DAG paralelo |
| "CRUD", "API", "rota" | CRUD | Auto-executor |
| "arquitetura", "projetar", "desenhar" | Design | Conselho (só Arquiteto + Revisor) |

## Como Usar

```bash
skill_view(name='auto-assembly-workflow')

# A partir de agora, descreva tarefas naturalmente:
# "Quero criar uma API de usuários com FastAPI, testar e fazer deploy"
# O Auto-Assembly monta tudo sozinho
```

## Exemplo Real

```
👤 USUÁRIO: "Cria um sistema de login com JWT"

🤖 AUTO-ASSEMBLY:
   Análise: Projeto novo + CRUD + testes
   Workflow montado:
   ┌────────────────────────────────────┐
   │ Skills: auto-executor, conselho-ias│
   │ Papéis: Arquiteto, Executor, Revisor│
   │ DAG: plan → (backend || frontend)  │
   │ Budget: Normal (15K tokens)        │
   │ Custo estimado: $0.002             │
   └────────────────────────────────────┘
   ✅ Workflow aprovado. Executando...
   
   1/4 🏗️ ARQUITETO: Planejando estrutura...
   2/4 ✅ CONSELHO: Aprovado
   3/4 ⚡ EXECUTOR: Criando backend...
   4/4 🔍 REVISOR: Código revisado e aprovado
   
   📦 RESULTADO: Sistema JWT criado em /src
```
