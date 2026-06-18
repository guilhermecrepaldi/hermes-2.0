---
name: hermes-arquitetura-melhorias
description: "Melhorias implementáveis na ARQUITETURA, ECONOMIA e OUTPUT do Hermes Agent. Inclui lições do leak do Claude Code (Mar/2026), DeepSeek V4 (Engram Architecture), GLM-5, OpenAI Codex Symphony, e inovações chinesas. Tudo implementável com skills + scripts + config, sem modificar fonte do Hermes."
category: software-development
tags: [hermes, arquitetura, economia, output, plan-execute-verify, auto-healing, skills, melhoria, deepseek, claude-code-leak, codex-symphony, system-prompt-leak]
---

# Melhorias na Arquitetura, Economia e Output do Hermes

## Fontes deste Estudo

| Fonte | Data | Relevância |
|-------|------|-----------|
| **Leak Claude Code** (512K linhas via npm source map) | 31 Mar 2026 | Código completo exposto. Repo do código: https://github.com/chauncygu/collection-claude-code-source-code |
| **Claude Code System Prompt leak** | Jun 2026 | System prompt completo do Fable 5 extraído. Repo: https://github.com/asgeirtj/system_prompts_leaks (43.3K★) |
| **OpenAI Codex Agent Loop** (official deep dive) | Jan 2026 | https://openai.com/index/unrolling-the-codex-agent-loop/ |
| **OpenAI Codex Prompting Guide** (prompt leak) | Abr 2026 | System prompt architecture, personality modes, harness patterns |
| **OpenAI Codex Symphony** (orquestrador) | Abr 2026 | https://openai.com/index/open-source-codex-orchestration-symphony/ |
| **DeepSeek V4** — Engram Architecture, 1T MoE | Abr 2026 | Memória condicional O(1), CSA sparse attention, Muon optimizer |
| **GLM-5 (Zhipu AI)** — 745B MoE, ARC unified | Fev 2026 | Agentic + Reasoning + Coding num modelo só, 1M contexto, MIT |
| **Google Antigravity 2.0** — N agentes paralelos | Mai 2026 | Orquestração visual, CLI, SDK |
| **Grok Build** — ACP, /skillify, 8 worktrees | Mai 2026 | Protocolo aberto entre agentes |

## Documentos de Referência (nesta skill)
- `references/claude-code-leaked-system-prompt.md` — System prompt completo do Claude Code Fable 5
- `references/licoes-leaks-claude-codex-deepseek.md` — Lições aplicáveis de todos os leaks

---

## Filosofia
Todas as melhorias abaixo são **implementáveis com os recursos que o Hermes já tem**: skills, scripts, `execute_code`, `delegate_task`, cronjob, memory, config.yaml. Zero modificação no código-fonte do Hermes.

---

## EIXO 1: ARQUITETURA — Mais Independente e Responsiva

### Lições do Leak do Claude Code (Mar 2026)

**Descobertas do código vazado:**

1. **O agent loop é um while-loop simples.** 20 linhas. Toda complexidade (512K linhas) está no *harness* — permissões, contexto, memória, compressão, schemas.
   → **Lições**: Não inventar framework. O loop de tool calls simples já cobre 95%.

2. **Segurança embutida na tool, não em policy externa.** As regras de segurança (git, filesystem, rede) estão dentro da *descrição da tool* que o modelo lê. Ex: o Bash tool tem 30+ regras de segurança na própria descrição.
   → **Lições**: Nossas skills devem ter safety checks embutidos, não num documento separado.

3. **Modelo barato para decisões baratas.** Claude Code usa Haiku (o modelo mais rápido/barato) para *safety checks* antes de executar comandos sensíveis. Só chama Opus quando precisa de raciocínio pesado.
   → **Lições**: DeepSeek V4 Flash para 95%, V4 Pro só quando necessário.

4. **Memória como índice leve, não verdade absoluta.** Memory é um índice de hints com retrieval sob demanda, não um banco de fatos confiáveis. O modelo sempre verifica antes de confiar.
   → **Lições**: Nossa memory existente já faz isso — manter assim.

5. **KV cache compartilhado entre sub-agentes.** Claude Code clona KV cache do parent para sub-agents, economizando 40-60% em tokens de contexto em tarefas paralelas.
   → **Implementável no Hermes**: Delegate_task já compartilha contexto — otimizar.

6. **Context Engineering > Prompt Engineering.** O diferencial não é o prompt, é como o contexto é estruturado: estático vs dinâmico, compressão seletiva, cache-friendly.
   → **Lições**: Nossas skills já separam instrução fixa (frontmatter) de conteúdo variável.

7. **44 features escondidas atrás de compile-time flags.** Undercover mode, auto-commit naming, sandbox mode, etc. — tudo desligável por flag.
   → **Lições**: Nossos perfis/providers já fazem isso.

### Engram Architecture — DeepSeek V4 (Abr 2026)

Innovação chinesa mais relevante para nosso pipeline:

| Componente | O que é | Aplicação no Hermes |
|-----------|---------|-------------------|
| **Engram Memory** | Memória condicional O(1) — aprendida, não RAG | Nossa memory persistente + skills são nossa "Engram" |
| **CSA (DeepSeek Sparse Attention)** | Atenção esparsa que escala pra 1M tokens | Compressão de contexto agressiva (já fazemos) |
| **HCA (Hybrid Computing Architecture)** | CPU + GPU coordenados | Nosso terminal + execute_code já usa CPU/host |
| **Muon Optimizer** | 2x mais eficiente que AdamW | Não aplica (otimização de treino, não de inferência) |

**Engram Memory explicado para nosso uso:**
- Diferente de RAG (busca vetorial), Engram é *memória condicional aprendida* — o modelo decide quando lembrar.
- Equivalente prático no Hermes: nossas **skills + memory** fazem papel similar, mas de forma mais explícita (o modelo não "decide lembrar", a skill é carregada).

**Lições práticas:**
- ✅ Skills são nossa Engram — conhecimento procedural que o modelo carrega sob demanda
- ✅ Memory persistente é nossa memória de longo prazo
- ❌ Engram é O(1) durante inferência — nossa memory é O(n) na busca. Podemos melhorar com cache.

### DeepSeek V4 Pro vs Flash (Abr 2026)

| Variante | Params | Ativos | Preço/1M | Uso |
|----------|--------|--------|----------|-----|
| **V4 Flash** | 284B | 13B | $0.15 | **Padrão — 95% das tarefas** |
| **V4 Pro** | 1.6T | 49B | $0.50 | Reasoning, tarefas complexas |

**Roteamento: Flash para 95%, Pro só quando Flash falha 3x.** Já implementado na skill `roteador-economico`.

### GLM-5 (Zhipu AI) — ARC Unified (Fev 2026)

**Inovação**: Único modelo que unifica **Agentic + Reasoning + Coding (ARC)** numa arquitetura MoE de 745B (44B ativos), 1M tokens de contexto.

**Lições para o Hermes:**
- ❌ Não temos um modelo unificado (usamos provedores diferentes)
- ✅ Skills + providers diferentes já fazem "ARC" — skill escolhe o provider certo pra cada tipo de tarefa
- ❌ GLM-5 é aberto (MIT) — podemos usar como fallback ou alternativa ao DeepSeek

### Codex Symphony — OpenAI (Abr 2026)

**Inovação**: Orquestrador que transforma um board (Linear/Jira) em *control plane* para coding agents.

```
Board (tickets) → Symphony → Agentes autônomos executam em paralelo → Humanos revisam PRs
```

**Aplicação no Hermes:**
- ✅ Kanban do Hermes já faz exatamente isso: board SQLite + dispatcher + workers
- ✅ Cronjob pode substituir a camada de "agendamento contínuo"
- ❌ Symphony tem UI visual — Hermes kanban é CLI-only

---

## 1.1 Loop Plan → Execute → Verify (Implementado)
Skill: `auto-executor`

## 1.2 Auto-Healing Pattern (Implementado)
Skill: `auto-healing`

## 1.3 Hooks de Qualidade (Implementado)
Script: `~/.hermes/scripts/pre-response-validator.py`

---

## EIXO 2: ECONOMIA — Máximo Resultado, Mínimo Custo

### 2.1 Roteamento Inteligente (Implementado)
Skill: `roteador-economico`

### Modelo Atual vs Concorrentes

| Modelo | Custo/1M tokens | Relativo | Uso |
|--------|:--------------:|:--------:|-----|
| **DeepSeek V4 Flash** | **$0.15** | **1x** | ✅ **Padrão absoluto** |
| DeepSeek V4 Pro | $0.50 | 3x | ⚠️ Só se Flash falhar 3x |
| Claude Haiku 4.5 | $0.80 | 5x | Nunca (DeepSeek cobre) |
| Claude Sonnet 4.6 | $3.00 | 20x | Nunca (DeepSeek cobre) |
| Claude Opus 4.8 | $15.00 | 100x | **NUNCA** |
| GPT-5 | $30.00 | 200x | **NUNCA** |
| DeepSeek V4 Pro (via Ollama local) | $0 | 0x | Se GPU disponível |

### 2.2 Compressão de Contexto (Ajustada)
```yaml
compression:
  enabled: true
  threshold: 0.35       # mais agressivo
  target_ratio: 0.15
```

### 2.3 Cache Compartilhado (NOVO — inspirado no Claude Code)
Sub-agents que compartilham contexto inicial economizam 40-60% tokens repetidos.

**Implementação**: Quando usar `delegate_task` para tarefas similares, passar o mesmo contexto de setup:

```python
# Em vez de 3 delegate_tasks independentes:
delegate_task(tasks=[
    {"goal": "Testar módulo A", "context": setup_context},
    {"goal": "Testar módulo B", "context": setup_context},
    {"goal": "Testar módulo C", "context": setup_context},
])
```

### 2.4 Pipeline de Custo Zero (DeepSeek + Ollama)
- DeepSeek V4 Flash cloud: ~$0.30/mês para uso normal
- Ollama local (qualquer modelo): $0/mês
- **Economia vs Claude Opus: 99x-500x**

---

## EIXO 3: OUTPUT — Mais Coeso e Acionável

### 3.1 Formato Padrão (Implementado)
Skill: `output-coeso`

### 3.2 Validação Pré-Entrega (NOVO — inspirado no Claude Code)

Antes de enviar resposta, rodar verificação automática:

```python
# validador
def validar_resposta(resposta):
    problemas = []
    if not resposta.strip(): problemas.append("vazia")
    if not any(m in resposta for m in ["exit_code", "✅", "path:"]):
        problemas.append("sem evidência real")
    if "como IA" in resposta.lower() and "não posso" not in resposta.lower():
        problemas.append("alucinação de limitação")
    return problemas
```

### 3.3 Delivery Report (Referenciado)
Skill existente: `delivery-report`

---

## Resumo do Plano

### Já Implementado (HOJE)

| Tarefa | Skill/Script | Lição de |
|--------|-------------|----------|
| ✅ Loop Plan→Execute→Verify | `auto-executor` | Claude Code + Grok Build |
| ✅ Auto-healing com fallbacks | `auto-healing` | DeepSeek V4 resiliência |
| ✅ Roteador econômico (Flash 95%) | `roteador-economico` | Claude Code (Haiku cheap decisions) + DeepSeek |
| ✅ Output coeso template | `output-coeso` | Claude Code context engineering |
| ✅ Compressão agressiva | config.yaml | Claude Code + DeepSeek CSA |
| ✅ Cache compartilhado | delegate_task batching | Claude Code KV cache sharing |

### Próximos Passos

| Tarefa | Impacto | Inspiração |
|--------|---------|-----------|
| Segurança embutida nas tools/skills desc | 🎯 Segurança zero-friction | Claude Code leak |
| Kanban como Symphony (board → agentes) | 🎯 Automação multi-tarefa | OpenAI Codex Symphony |
| Importar skills do Claude/Grok | 📦 Ecossistema | Grok Build compatibilidade |
| DeepSeek V4 Pro via Ollama (self-host) | 💰 Custo zero | DeepSeek open source |

### Stack Atual Recomendada

```
MODELO: DeepSeek V4 Flash (cloud, $0.15/1M)
FALLBACK: DeepSeek V4 ou Flash (retry)
LOOP: auto-executor (Plan→Execute→Verify, 3 attempts)
HEALING: auto-healing (15+ fallbacks automáticos)
OUTPUT: output-coeso (template obrigatório)
ECONOMIA: roteador-economico (Flash no topo)
MEMÓRIA: Hermes memory + skills (nossa "Engram")
PARALELISMO: delegate_task batch (KV cache sharing)
```

Custo projetado: **~$0.30/mês**. Performance: **nível Claude Opus** para 95% das tarefas.
