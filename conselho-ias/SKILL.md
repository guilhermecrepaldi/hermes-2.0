---
name: conselho-ias
description: "Conselho de IAs — múltiplos agentes especializados deliberam antes de agir. Inspirado no Shannon Swarm V2 (Japão) e OWL Workforce Learning (China). Cada agente tem um papel (Arquiteto, Revisor, Executor, Auditor) e vota antes da execução. Aumenta assertividade do output por consenso."
category: autonomous-ai-agents
tags: [conselho, deliberacao, multi-agente, governanca, votacao, neo-hermes]
---

# Conselho de IAs — Deliberação Multi-Agente Antes da Ação

## Inspiração
- **Shannon** (Kocoro-lab/Japan): Swarm V2 — lead-orchestrated multi-agent com loops paralelos, token budget, approval workflows
- **OWL** (CAMEL-AI/China): Workforce Learning — agentes com papéis fixos que colaboram
- **DeerFlow** (ByteDance/China): Super Agent Harness com sub-agentes especializados

## Conceito

> **4 agentes especializados analisam a mesma tarefa → cada um dá seu parecer → conselho vota → só executa se aprovado.**

Isso elimina decisões precipitadas, aumenta a assertividade e simula um time real de desenvolvimento.

```
         ┌──────────┐
         │  TAREFA   │
         └────┬─────┘
              │
      ┌───────┼───────┐
      ▼       ▼       ▼
  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
  │ ARQ  │ │ REV  │ │ EXEC │ │ AUD  │
  │ iteto│ │ isor │ │ utor │ │ itor │
  └──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
     │        │        │        │
     └────────┴────┬───┴────────┘
                   ▼
            ┌──────────┐
            │ CONSELHO │
            │  (VOTA)  │
            └────┬─────┘
               ✅/❌
                 │
                 ▼
           [EXECUTA ou AJUSTA]
```

## Papéis do Conselho

### 1. Arquiteto (Chief Architect)
**Responsabilidade**: Planejar a abordagem, escolher ferramentas, validar viabilidade.
- Cria o plano de execução
- Define stack e dependências
- Identifica riscos
- **Input**: `auto-executor` (PLAN)
- **Frase**: "Sugiro a seguinte arquitetura..."

### 2. Revisor (Code Reviewer)
**Responsabilidade**: Revisar o plano por qualidade, segurança e boas práticas.
- Verifica se o plano segue boas práticas
- Identifica vulnerabilidades potenciais
- Sugere melhorias
- **Input**: `arquitetura-code-review-loops`
- **Frase**: "O plano está sólido, mas sugiro..."

### 3. Executor (Implementer)
**Responsabilidade**: Executar o plano aprovado, reportar resultados.
- Executa cada passo
- Coleta evidências (exit codes, paths, logs)
- Reporta resultados
- **Input**: `auto-executor` (EXECUTE + VERIFY)
- **Frase**: "Executando conforme plano..."

### 4. Auditor (Quality Auditor)
**Responsabilidade**: Verificar o resultado final, métricas, conformidade.
- Confere se o entregável atende aos requisitos
- Verifica métricas (cobertura, performance, segurança)
- Valida se pode ir para produção
- **Input**: `cybersec-code-review` + `output-coeso`
- **Frase**: "Auditoria concluída. Resultado: ✅/❌"

## Fluxo de Deliberação

```
Fase 1 — ANÁLISE INDIVIDUAL
  Arquiteto: analisa e planeja (não executa!)
  Revisor: revisa o plano do Arquiteto
  -> Se Revisor rejeita: Arquiteto ajusta (loop)

Fase 2 — EXECUÇÃO
  Executor: executa o plano aprovado
  Auditor: acompanha a execução em tempo real

Fase 3 — VERIFICAÇÃO
  Auditor: verifica resultado final
  Revisor: revisa código gerado
  -> Se ambos aprovam: ✅ ENTREGUE
  -> Se não: loop de correção

Fase 4 — REPORT
  Conselho: relatório consolidado com parecer de cada membro
```

## Uso no Hermes

```python
# Fluxo do Conselho
from hermes_tools import delegate_task

def conselho_deliberar(tarefa):
    # Fase 1: Análise paralela
    tarefa_contexto = f"Tarefa: {tarefa}\nContexto: {contexto_atual()}"
    
    plano = delegate_task(
        goal="Atue como Arquiteto. Crie um plano detalhado para: " + tarefa,
        context=tarefa_contexto,
        toolsets=["terminal", "file", "web"]
    )
    
    revisao = delegate_task(
        goal="Atue como Revisor. Revise criticamente este plano e sugira melhorias: " + plano.summary,
        context=tarefa_contexto,
        toolsets=["web"]
    )
    
    # Se revisor aprovou, executa
    if revisao.summary.startswith("✅") or "aprovado" in revisao.summary.lower():
        resultado = delegate_task(
            goal="Atue como Executor. Execute o plano aprovado: " + plano.summary,
            context=tarefa_contexto,
            toolsets=["terminal", "file"]
        )
        
        auditoria = delegate_task(
            goal="Atue como Auditor. Verifique este resultado contra os requisitos: " + resultado.summary,
            context=tarefa_contexto + "\nRequisitos: " + tarefa,
            toolsets=["terminal"]
        )
        
        if auditoria.summary.startswith("✅"):
            return "✅ Conselho aprovou. " + resultado.summary
        else:
            return "⚠️ Auditoria apontou problemas. " + auditoria.summary
    else:
        return "🔄 Conselho pediu ajustes. " + revisao.summary
```

## Vantagens

| Aspecto | Sem Conselho | Com Conselho (Neo Hermes) |
|---------|-------------|--------------------------|
| Planejamento | Executa direto | Arquiteto + Revisor deliberam |
| Qualidade | Revisão depois | Revisão ANTES de executar |
| Segurança | Só no final | Auditoria contínua |
| Assertividade | Tenta-erro-tenta | Consenso antes da ação |
| Custo | Pode refazer várias vezes | Mais caro por tarefa, MAIS BARATO no total |

## Quando Usar vs Quando Não

### Use o Conselho para:
- 🔴 Tarefas complexas (3+ passos)
- 🔴 Código que vai para produção
- 🔴 Mudanças em infraestrutura
- 🔴 Decisões de arquitetura
- 🔴 Tarefas com risco alto

### Não use o Conselho para:
- ✅ Leitura de arquivos
- ✅ Comandos simples (1 passo)
- ✅ Pesquisa rápida
- ✅ Tarefas já padronizadas em skill
