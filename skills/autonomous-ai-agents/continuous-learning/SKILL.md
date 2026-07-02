---
name: continuous-learning
description: "Sistema de aprendizado contínuo: extrai padrões de sessões anteriores e os transforma em skills/insights reutilizáveis. Inspirado no ECC Continuous Learning + Session Evaluation hooks."
category: autonomous-ai-agents
tags: [learning, patterns, skills, evolution, memory, ecc-inspired]
---

# Continuous Learning — Aprendizado Contínuo

## Trigger
- Ao final de tarefas complexas (5+ tool calls)
- Após resolver bugs recorrentes
- Quando descobre um padrão útil
- Usuário diz "aprenda isso", "guarde isso", "nunca mais erre isso"

## Mecanismo

### 1. Extração de Padrões (Stop:evaluate-session hook)

Ao final de cada sessão ou após tarefa complexa, extrair:

```
- Erro comum corrigido: {descrição}
- Solução aplicada: {passos}
- Pode virar skill? Sim/Não
- Pode virar memory? Sim/Não
- Padrão de código identificado: {descrição}
- Workflow repetitivo: {descrição}
```

### 2. Gatilhos para Criação de Skills

Criar skill (com confirmacao do usuario) quando:

| Gatilho | Ação |
|---------|------|
| Mesmo erro resolvido 2+ vezes | Criar auto-healing rule |
| Workflow manual repetido 3+ vezes | Criar skill de automação |
| Padrão de código descoberto | Criar reference/snippet |
| Config recorrente | Criar template/config |
| Correção que usuario pediu explicitamente | skill_manage create/patch |

### 3. Gatilhos para Memory

Guardar em memoria (sem perguntar) quando:

| Situação | Ação |
|----------|------|
| Preferência do usuário declarada | memory add |
| Correção de comportamento do agente | memory add |
| Caminho/env/config importante | memory add |
| Workflow que funcionou bem | Oferta de skill ao final |

### 4. Pattern Extraction Template

markdown
## Continuous Learning - Extração

### Sessão: {breve descricao}
### Padrões Identificados:

1. **{Pattern name}**
   - Contexto: {quando ocorre}
   - Solução: {o que fazer}
   - Reutilizável: {sim/nao}
   - Ação: {criar skill / memory / nada}

### Lições Aprendidas
- {licao 1}
- {licao 2}

### Sugestão
- {skill/memory a criar}
