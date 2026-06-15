---
name: exoskeleton
description: "Deterministic engineering harness for AI agents — 'model proposes, code disposes.' Preflight checks, security blast radius, intent classification, and evidence grounding. Open-source from BitGN."
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, guardrails, safety, deterministic-harness, model-dispatcher]
---

# Exoskeleton — Deterministic Harness para Agentes de IA

## Fonte
Extraído da Edição #006 do TOP OF THE HOUR — IA
Card: "Exoskeleton: Framework Open-Source de Deterministic Harness para Despacho de Modelos em Produção"

## O que é

Exoskeleton é um framework open-source de **deterministic engineering harness** para agentes de IA, desenvolvido por BitGN para o benchmark ECOM1 (agente de e-commerce simulado). O princípio central é **"the model proposes, the code disposes"** — o modelo LLM funciona como *dispatcher* (despachante), enquanto código determinístico executa a lógica de domínio pesada, valida as evidências, controla o formato exato da resposta e protege as fronteiras de segurança.

**Resultados comprovados:**
- **1º lugar** — Live PROD leaderboard (BitGN ECOM1)
- **1º lugar** — Hall of Fame: Speed
- **10º lugar** — Hall of Fame: Ultimate

### Arquitetura (4 estágios)

```
[1] START                     [2] PREFLIGHT CHECKS         [3] MAIN LOOP              [4] ANSWER ASSEMBLY
│                              │                           │                         │
├─ Environment map loading    ├─ Intent classifier         ├─ Model dispatcher        ├─ Evidence ledger
├─ Intent classification      │  (gpt-5.4-nano)           │  (gpt-5.4-mini)          ├─ Reference normalization
│  (gpt-5.4-nano, paralelo)   ├─ Security gate            │  ├─ Tool calling          ├─ Formatter
│                             │  (blast radius + /bin/id) │  ├─ Domain helpers        │  (gpt-5.4-nano)
│                             ├─ Refund preflight          │  ├─ Environment tools     │
│                             ├─ Arithmetic preflight      │  └─ report_completion     │
│                             ├─ Date preflight            │                           │
│                             └─ City preflight            └─ Step budget (75)         └─ Outcome + message + refs
```

### Componentes

| Componente | Estágio | Responsabilidade |
|---|---|---|
| Intent Classifier | (1) Start | Extrai intenções e entidades do texto da tarefa |
| Flag Normalization | (2) Preflight | Avalia "blast radius" — dano máximo se executar |
| Security Gate | (2) Preflight | Recusas de segurança ANTES do loop principal |
| Domain Preflights | (2) Preflight | Data, refund, /tmp, count, city, fraud-history |
| Dispatcher | (3) Loop | Entende a tarefa, escolhe ferramentas, decide |
| Environment Tools | (3) Loop | Leitura/execução no snapshot do SO |
| Domain Helpers | (3) Loop | Catálogo, recibos, dispatch, fraude, 3DS |
| Evidence Ledger | (4) Assembly | Acumula e aplica referências dos helpers |
| Reference Normalization | (4) Assembly | Canonicaliza, auto-adiciona, filtra, protege |
| Formatter | (4) Assembly | Formata mensagem visível no contrato exato |

### Princípios-Chave

1. **"Don't plug holes, look for a systemic solution"** — Onde o modelo tropeça na mesma classe de tarefas, resolva com ferramenta separada ou verificação determinística, não com outra linha no prompt.
2. **Blast radius, não blocklist** — A decisão de segurança não é baseada em palavras suspeitas, mas na resposta à pergunta: "se eu simplesmente fizer o que a tarefa literalmente pede, qual é o pior que pode acontecer?"
3. **Degradação suave** — Se o classificador de intenção falhar completamente, todos os preflight checks ficam vazios e o modelo comum resolve a tarefa.
4. **Parallel tool calls** — O modelo pode chamar 2-5 ferramentas por turno, executadas em lote.
5. **Step budget com safety net** — Se o modelo não completar dentro do orçamento, o agente submete uma resposta de erro interno.

## Como implementar no Hermes 2.0

### 1. Clonar o repositório
```bash
git clone https://github.com/muxx/bitgn-ecom1-exoskeleton.git
cd bitgn-ecom1-exoskeleton
```

### 2. Configurar
```bash
cp .env.example .env
# Preencher BITGN_API_KEY, MODEL_ID, etc.
```

### 3. Instalar dependências
```bash
make sync
```

### 4. Executar benchmark
```bash
make run
make task TASKS="t01 t04"   # tarefas específicas
```

### 5. Integração com Hermes
- Use o padrão Exoskeleton para adicionar **preflight checks determinísticos** antes de qualquer tarefa de agente Hermes
- Implemente o **security gate** como middleware entre o input do usuário e o loop principal do agente
- Use o **evidence ledger** para rastrear fontes e referências em respostas multi-step
- Adicione **intent classification** como camada de roteamento antes de delegar para modelos especializados

## Comandos
```bash
# Benchmark completo
make run

# Tarefas específicas
make task TASKS="t01 t04 t07"

# Heatmap de scores
make runs-html

# Sincronizar ambiente
make sync
```

## Variáveis de Ambiente
| Variável | Padrão | Descrição |
|---|---|---|
| `BITGN_API_KEY` | — | Chave para runs oficiais ECOM |
| `BENCH_ID` | `bitgn/ecom1-dev` | ID do benchmark |
| `MODEL_ID` | `gpt-5.4-mini` | Modelo dispatcher |
| `HELPER_MODEL` | `gpt-5.4-nano` | Modelo para helpers |
| `AGENT_MAX_STEPS` | `75` | Máx. de steps por trial |
| `TRIAL_BATCH_SIZE` | `10` | Trials concorrentes |
| `OPENAI_TIMEOUT_SECONDS` | `40` | Timeout por request |

## Referência
- Repositório: https://github.com/muxx/bitgn-ecom1-exoskeleton
- Arquitetura: https://github.com/muxx/bitgn-ecom1-exoskeleton/blob/main/articles/ARCHITECTURE.md
- BitGN ECOM1 Challenge: https://bitgn.com/challenge/ecom
- Paper relacionado: "Adapting the Interface, Not the Model" — arXiv:2605.22166
