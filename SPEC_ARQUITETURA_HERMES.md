# SPEC_ARQUITETURA_HERMES.md
# Arquitetura Agentica do Hermes 2.0 vs Fable 5 (Claude Code)
# Objetivo: Aproximar nossa arquitetura ao padrão Fable 5 mantendo nossa identidade

## Estado Atual (20-Jun-2026)

### ✅ Ja implementado (passo a passo com Fable 5)

| Componente | Status | Arquivo | Detalhe |
|---|---|---|---|
| **Loop central < 20 linhas** | ✅ | `hermes_loop.py` | `while True` + handle + exit |
| **Harness com permissoes** | ✅ | `core.py` | `HermesHarness` com validate |
| **Roteamento economico IA local** | ✅ | `core.py` | Ollama primeiro, fallback cloud |
| **Context Engineering** | ✅ | `engine.py` | `carregar_progresso()` integrado ao loop |
| **Agent Loop + harness** | ✅ | `hermes_loop.py` | <20 linhas orquestracao |
| **Hooks pre/post** | ✅ | `engine.py` | `HookManager` com setup_default |
| **Checkpointing** | ✅ | `engine.py` | `CheckpointManager` save/list/compact |
| **KV Cache sharing** | ✅ | `engine.py` | `KVCache` com TTL e compact |
| **Initializer + Coding Agent** | ✅ | `engine.py` | `InitializerAgent.setup()` + `CodingAgent.plan()` |
| **Subagent via worktree** | ✅ | `engine.py` | `criar_worktree()` / `remover_worktree()` |
| **Auto-compaction checkpoints** | ✅ | `engine.py` | Mantem os 10 mais recentes |
| **28 testes passando** | ✅ | `tests/` | core + economy + engine + router + workbench |
| **CI verde** | ✅ | `.github/workflows/` | Lint + pytest

O Fable 5 (Claude Code) demonstra que uma arquitetura de agente eficiente pode ser surpreendentemente simples:
- **Loop central**: ~20 linhas de `while True` que orquestram tudo
- **Harness é o complexo**: Permissões, contexto, memoria, ferramentas
- **Segurança embeded**: Nas descriptions das tools, não em policies externas
- **Haiku para decisões baratas**: Safety checks com modelo barato antes de actions caras
- **Memória como índice leve**: Retrieval sob demanda, não verdade absoluta
- **KV cache compartilhado**: Entre sub-agentes para 40-60% economia de tokens
- **Context Engineering > Prompt Engineering**: Estrutura do contexto é o diferencial
- **44 features escondidas**: Atras de compile-time flags

## Nosso Estado Atual vs Fable 5

### ✅ O que já temos de semelhante ao Fable 5

| Fable 5 Feature | Nossa Implementação | Status |
|---|---|---|
| Agent loop simples | `auto-executor` skill (Plan→Execute→Verify) | ✅ Similar conceito |
| Harness complexo | Nossa skill ecosystem + memory system | ✅ Abstraído em skills |
| Segurança em tool descriptions | Nossa abordagem de descrever regras nas skills | ✅ Em implementação |
| Modelo barato para decisões | `roteador-economico` (DeepSeek Flash 95%) | ✅ Implementado |
| Memória leve + retrieval | Hermes memory + skills system | ✅ Index-like system |
| Context Engineering | `hermes-progress.md` + session memory | ✅ Em evolução |
| KV cache compartilhado | `delegate_task` com `background=True` sharing | ✅ Parcial |

### ⚠️ Gaps Críticos a Implementar

| Fable 5 Feature | Nossa Lacuna | Prioridade | Como Implementar |
|---|---|---|---|
| **Loop verdadeiramente simples** | Nossa lógica está espalhada em skills | ALTA | Criar `agent_loop.py` com while True simples que dispacha skills |
| **Harness como biblioteca** | Skills são procedurais, não componentes reutilizáveis | ALTA | Transformar skills em módulos Python com API clara |
| **Security embedded** | Ainda dependemos de julgamento externo | ALTA | Embed rules diretamente nas tool descriptions (como Fable 5) |
| **Haiku para safety checks** | Nenhum safety check pré-execução | MÉDIA | Adicionar camada de validação leve antes de actions caras |
| **Memória como índice O(1)** | Nossa memory é mais como armazenamento que índice | MÉDIA | Implementar cache de acessos frequentes com TTL |
| **KV cache compartilhado real** | Compartilhamento limitado de output | ALTA | Implementar sistema de cache compartilhado entre sub-agents |
| **Context Engineering avançado** | Progresso linear, não estruturado | MÉDIA | Evoluir `hermes-progress.md` para structured context |
| **44 features escondidas** | Nossa config é explícita | BAIXA | Adicionar flags de performance/performance tradeoffs |

## Plano de Aproximação ao Fable 5

### Fase 1: Simplificação do Loop (Imediata)
- Criar `hermes_loop.py` com estrutura `while True:` mínima
- Loop deve: 
  1. Ler input do usuário
  2. Atualizar context (hermes-progress.md + memória)
  3. Escolher próxima action baseado em skills disponíveis
  4. Executar action via skill system
  5. Atualizar progress e aguardar próximo input
- Mantemos todas as skills existentes como "actions" que o loop pode chamar

### Fase 2: Harness como Biblioteca (Curto Prazo)
- Refatorar `watchdog/core.py` para ser um verdadeiro harness
- Extrair permissões, validações, logging como funções reutilizáveis
- Cada skill deve declarar seus requirements (permissions, context needed)
- Loop verifica requisitos antes de executar

### Fase 3: Segurança Embedded (Curto Prazo)
- Cada tool/skill deve ter sua security policy na description
- Exemplo: `patch` tool deve descrever exatamente quais arquivos pode modificar
- Loop valida action contra security policy antes de execução
- Reduzir necessidade de julgamento externo

### Fase 4: Haiku para Decisions Baratas (Médio Prazo)
- Antes de actions caras (pesquisa web, LLMs pesados), usar modelo barato para validação
- Exemplo: Antes de usar DeepSeek Pro, usar Flash para verificar se a pergunta é simples
- Implementar em `roteador-economico` avançado

### Fase 5: Memória como Índice (Médio Prazo)
- Implementar cache de acessos frequentes em memória
- LRU cache para skills mais usadas, context recente
- TTL para informações que expiram
- Manter persistência em disco para longo prazo

### Fase 6: KV Cache Compartilhado (Médio Prazo)
- Sistema de cache compartilhado entre sub-agents criados via `delegate_task`
- Quando sub-agent A gera output, armazena no cache compartilhado
- Sub-agent B pode ler do cache sem recomputar
- Reduz custos de tokens em 40-60% em workloads paralelos

### Fase 6: Context Engineering Avançado (Longo Prazo)
- Evoluir `hermes-progress.md` para structured context object
- Context = {session_state, available_skills, recent_actions, token_budget}
- Context é passado explícito para cada action
- Permite melhor reasoning sobre o que fazer próximo

### Fase 7: Features Escondidas (Longo Prazo)
- Adicionar compile-time-like flags para performance tradeoffs
- Exemplos: 
  - `--fast-mode`: prioriza velocidade sobre profundidade
  - `--thorough-mode`: prioriza completude sobre custo
  - `--safe-mode`: extra validação antes de actions
  - `--creative-mode`: permite mais assumptons

## Métricas de Aproximação

Nossa arquitetura será considerada "próxima do Fable 5" quando:

1. **Loop central** tem < 50 linhas de código puro de orquestração
2. **>80%** da complexidade está no harness (permissões, contexto, ferramentas)
3. **Security embedded**: >90% das regras de segurança estão nas tool descriptions
4. **Haiku usado**: >30% das decisions caras são validadas por modelo barato primeiro
5. **Memória eficiente**: Hit rate >70% no cache de contexto frequente
6. **KV sharing**: >40% redução em tokens quando sub-agents fazem work relacionado
7. **Context engenhED**: Context é passado explícito, não implicitamente via arquivos

## Implementação Inicial: Agent Loop Simplificado

Vamos criar o esboço do nosso `agent_loop.py` que encapsula a essência do Fable 5:

```python
#!/usr/bin/env python3
"""
Hermes Agent Loop - Inspired by Fable 5 (Claude Code)
Simple while loop that orchestrates everything through skills and harness.
"""

import sys
from pathlib import Path
from core import harness  # Nosso harness refatorado
from skills import loader   # Nosso sistema de skills

def main():
    """Simple agent loop: the core of our agentic system."""
    # Initialize harness (permissions, context, tools, memory)
    h = harness.HermesHarness()
    
    # Main agent loop - ~20 lines of orchestration logic
    while True:
        try:
            # 1. Get input from user/system
            user_input = input("hermes> ") if not sys.stdin.isatty() else sys.stdin.read()
            if not user_input.strip():
                continue
                
            # 2. Update context (hermes-progress.md + memory systems)
            h.update_context(user_input)
            
            # 3. Choose next action based on context and available skills
            action = h.choose_action(user_input)
            
            # 4. Execute action through skill system with harness validation
            result = h.execute_action(action, user_input)
            
            # 5. Update progress and show result
            h.update_progress(result)
            print(f"✅ {result.summary}")
            
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except Exception as e:
            h.handle_error(e)
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
```

Este loop tem ~15 linhas de lógica pura de orquestração. Toda a complexidade está no `harness` (permissões, contexto, memória, segurança, ferramentas) e no `skills` system (nossas 179+ skills).

Isso é exatamente o padrão Fable 5: loop simples, harness complexo.

## Próximos Passos Imediatos

1. Criar `hermes_loop.py` com esboço acima
2. Refatorar `harness` para ser verdadeiramente reutilizável
3. Adaptar nossas skills para trabalhar com esse loop
4. Testar com tarefas simples primeiro
5. Evoluir gradualmente para o estado completo

Esta abordagem nos permite:
- Manter toda nossa funcionalidade existente (skills, memória, etc)
- Aproximar nossa arquitetura do padrão comprovado do Fable 5
- Manter a simplicidade no núcleo enquanto mantemos o poder nas bordas
- Evoluir incrementalmente sem quebrar o sistema existente
