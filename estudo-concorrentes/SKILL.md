---
name: estudo-concorrentes-hermes
description: "Estudo aprofundado dos concorrentes do Hermes Agent em 2025-2026: Claude Code/Opus (Anthropic), Google Antigravity 2.0/Gemini, Grok Build (xAI) e OpenAI GPT-5/Codex. Arquiteturas, features, loops autônomos, skills, multi-agentes e como aplicar no Hermes para torná-lo mais independente e responsivo."
category: software-development
tags: [hermes, concorrentes, agentes, arquitetura, copilot, claude-code, grok, openai, gemini, antigravity]
---

# Estudo de Concorrentes — Hermes Agent vs Big Tech (2025-2026)

## Contexto

O cenário de coding agents explodiu em 2025-2026. Cada big tech lançou seu agente autônomo de código com arquiteturas próprias. Este estudo mapeia cada um e extrai lições para evoluir o Hermes Agent.

---

## 1. Claude Code (Anthropic) — O Líder em Agentes de Código

### Modelos (Junho 2026)
- **Claude Opus 4.8** — Flagship, melhor para refatoração pesada e tarefas agentivas
- **Claude Sonnet 4.6** — Padrão, ótimo custo-benefício
- **Claude Haiku 4.5** — Rápido e barato para tarefas simples

### Arquitetura do Claude Code
```
[Terminal CLI] → [Claude Code Agent]
  ├── MCP Servers (tools externos: banco, APIs, sistema)
  ├── Skills (procedures reutilizáveis, 21.6K+ no marketplace)
  ├── Hooks (eventos pré/pós execução)
  ├── AGENTS.md / CLAUDE.md (contexto de projeto)
  ├── Sub-agents (delegação para tarefas paralelas)
  └── Permissions (aprovação humana para ações sensíveis)
```

### Inovações-Chave
| Feature | Descrição |
|---------|-----------|
| **Skills** | Procedimentos salvos que o agente carrega sob demanda. Ecossistema de 21.6K+ skills. |
| **MCP (Model Context Protocol)** | Protocolo aberto de ferramentas. Qualquer MCP server vira tool do agente. |
| **Sub-agents** | Claude Code spawna agentes-filho para tarefas paralelas (code review, testes, debugging) |
| **Claude Code Plugins** | Extensões que adicionam comandos e agentes customizados |
| **AGENTS.md** | Arquivo de configuração de projeto que define comportamento do agente |
| **Plan-Review-Approve** | Workflow: agente planeja → humano revisa → agente executa |
| **Ferramentas nativas** | Editor de arquivos, terminal, busca, git, visão |

### Lições para o Hermes
- ✅ Skills é o diferencial mais forte do Hermes — estamos no caminho certo
- ✅ Precisamos de um marketplace público de skills (como Claude tem 21.6K+)
- ❌ Claude Code tem hooks (eventos) — Hermes pode adicionar hooks pre/post tool
- ❌ MCP é protocolo aberto — Hermes já suporta MCP? Se não, deve suportar

---

## 2. Google Antigravity 2.0 + Gemini — A Plataforma Multi-Agente

### Lançamento: Google I/O 2026 (Maio 2026)

### Modelos
- **Gemini 3.5 Flash** — Rápido para coding
- **Gemini Omni** — Multimodal (texto, imagem, áudio, vídeo)
- **Gemini Spark** — Agente 24/7 autônomo
- **Gemini 3.1 Pro** — Pesado para tarefas complexas

### Arquitetura Antigravity 2.0
```
[Antigravity 2.0 Desktop App]
  ├── [Antigravity CLI] (Go-based, terminal)
  ├── [Antigravity SDK] (Python, programático)
  ├── [Antigravity IDE] (editor completo)
  │
  └── Orquestrador Multi-Agente
       ├── Agente 1 (projeto A)
       ├── Agente 2 (projeto B) ← paralelo
       ├── Agente 3 (projeto C) ← paralelo
       └── ... até N agentes simultâneos
```

### Inovações-Chave
| Feature | Descrição |
|---------|-----------|
| **Multi-agente nativo** | Orquestra N agentes autônomos em projetos independentes simultaneamente |
| **94 agentes construíram um SO** | Prova de conceito — agentes paralelos cooperaram num OS completo |
| **Managed Agents (Gemini API)** | Deploy enterprise de agentes com governança |
| **Antigravity SDK** | SDK Python para construir e orquestrar agentes programaticamente |
| **Plan-Execute-Verify** | Loop de 3 estágios: planejar, executar, verificar |
| **Google AI Studio** | "Vibe coding" nativo para Android |
| **Integração nativa** | Gemini em todo ecossistema Google (Search, Cloud, Workspace) |

### Lições para o Hermes
- ✅ Hermes já tem `delegate_task` (multi-agente paralelo) — similar ao Antigravity
- ❌ Antigravity tem orquestrador visual (desktop app) — Hermes já tem desktop GUI
- ❌ SDK programático (Antigravity SDK) — Hermes tem `execute_code` que faz papel similar
- ❌ Managed Agents com governança — Hermes pode evoluir perfis com permissões granulares

---

## 3. Grok Build (xAI) — O Novo Entrante Agressivo

### Lançamento: Maio 2026 (beta)

### Modelo Base: **Grok 4.3**
- Motor: `grok-code-fast-1` (especializado para código)
- Disponível via SuperGrok ($99/mo Heavy, $300/mo list)

### Arquitetura Grok Build
```
[Terminal CLI / TUI]
  ├── Grok Skills (compatível com Claude Code Skills)
  ├── Plugins Marketplace
  ├── AGENTS.md / CLAUDE.md (compatível com Claude)
  ├── MCP Servers (compatível)
  ├── ACP (Agent Client Protocol — padrão aberto)
  ├── Hooks (eventos pre/post)
  └── Sub-agentes (até 8 paralelos, cada um em git worktree próprio)
```

### Inovações-Chave
| Feature | Descrição |
|---------|-----------|
| **Compatibilidade com Claude Code** | Reusa skills, AGENTS.md, MCP servers do Claude |
| **ACP (Agent Client Protocol)** | Protocolo aberto da xAI para comunicação entre agentes |
| **8 sub-agentes paralelos** | Cada um em git worktree isolado — branches paralelas |
| **Plan-Review-Approve workflow** | Planejamento → Revisão humana → Execução |
| **/skillify** | Captura qualquer sessão como skill com um comando |
| **Headless mode** | Flag `-p` para rodar em CI/CD, sem terminal interativo |
| **Grok Automations** | Tarefas Grok que rodam automaticamente em schedule |

### Lições para o Hermes
- ✅ `/skillify` = Hermes já cria skills com `skill_manage(action='create')` — mas podia ser 1 comando
- ✅ Sub-agentes paralelos = Hermes já faz com `delegate_task`
- ❌ ACP (Agent Client Protocol) — Hermes pode adotar como padrão aberto de comunicação
- ❌ Headless mode para CI/CD — Hermes cronjob já faz isso parcialmente
- ❌ Compatibilidade entre skills de diferentes agentes — Hermes podia importar skills do Claude Code

---

## 4. OpenAI GPT-5 / Codex — O Unificado

### Lançamento GPT-5: Agosto 2025

### Modelos (Q2 2026)
- **GPT-5** — Primeiro modelo unificado (rápido + reasoning)
- **GPT-5.5** — Foco em produtividade, tool use autônomo
- **GPT-5.6 (iris-alpha)** — Vislumbrado, 1.5M tokens de contexto
- **o-series** — Reasoning puro (fundido no GPT-5)

### Arquitetura GPT-5
```
[GPT-5 Router] → Decide automaticamente:
  ├── Rota Rápida → tarefas simples (ex-GPT-4o)
  └── Rota Reasoning → tarefas complexas (ex-o3)

[OpenAI Codex] → Agente de código
  ├── Sandbox de execução
  ├── Visão (screenshots)
  ├── Git integrado
  └── Editor de arquivos
```

### Inovações-Chave
| Feature | Descrição |
|---------|-----------|
| **Roteamento automático** | Modelo decide sozinho quando pensar mais vs responder rápido |
| **50-80% menos tokens** que o3 em tarefas visuais, coding, científicas |
| **Unified system** — não precisa escolher entre GPT e o-series |
| **Codex Agent** — agente autônomo com sandbox, visão, git |
| **100K+ context** — e crescendo (1.5M no GPT-5.6) |

### Lições para o Hermes
- ✅ Roteamento automático = Hermes já escolhe modelo por tarefa (skill decide provider)
- ❌ GPT-5 unified = Hermes depende do provedor de fundo — mas skills ajudam a abstrair
- ❌ Codex sandbox = Hermes terminal já isola execução

---

## 5. Tabela Comparativa Geral (Q2 2026)

| Característica | Hermes Agent | Claude Code | Google Antigravity | Grok Build | OpenAI GPT-5 |
|---------------|:------------:|:-----------:|:------------------:|:----------:|:-----------:|
| **Open Source** | ✅ Sim | ❌ Fechado | ❌ Fechado | ❌ Fechado | ❌ Fechado |
| **Skills** | ✅ Nativo | ✅ 21.6K+ | ❌ | ✅ (compatível) | ❌ |
| **Multi-agente** | ✅ delegate_task | ✅ Sub-agents | ✅ Nativo N agentes | ✅ 8 worktrees | ❌ |
| **MCP** | ? | ✅ Nativo | ✅ | ✅ Nativo | ❌ |
| **Memory** | ✅ Persistente | ❌ Sessão | ✅ Gemini Spark | ❌ Sessão | ❌ Sessão |
| **Cron/Agendamento** | ✅ Nativo | ❌ | ❌ | ✅ Automations | ❌ |
| **Marketplace** | ❌ | ✅ 21.6K skills | ❌ | ✅ Plugins | ❌ |
| **Multi-plataforma** | ✅ Telegram, Discord, SMS, Email, WhatsApp, Signal | ❌ Terminal/IDE | ✅ Desktop, CLI, SDK | ❌ Terminal | ❌ ChatGPT/API |
| **Self-hosted** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Provider-agnostic** | ✅ Qualquer LLM | ❌ Só Claude | ❌ Só Gemini | ❌ Só Grok | ❌ Só OpenAI |
| **Plan-Review-Approve** | Parcial (skills) | ✅ Completo | ✅ Plan-Execute-Verify | ✅ Completo | Parcial |

---

## 6. Roadmap de Melhorias para o Hermes

Com base no estudo, aqui está o que implementar para tornar o Hermes **mais independente, responsivo e com loops validativos**:

### Prioridade Alta — Impacto Imediato

1. **Marketplace de Skills**
   - Criar repositório público de skills compartilháveis
   - Comando: `hermes skill install <name>` (baixa do repo)
   - Inspirado em: Claude Skills Directory (21.6K+) e Grok Plugins Marketplace

2. **Hooks (Eventos)**
   - Pré-hook: antes de executar tool (ex: validar permissão)
   - Pós-hook: depois de tool (ex: logar resultado, notificar)
   - Inspirado em: Claude Code Hooks

3. **Loop Plan → Execute → Verify**
   ```yaml
   workflow:
     - plan: skill planeja, mostra plano ao usuário
     - approve: usuário aprova ou ajusta
     - execute: skill executa
     - verify: skill valida resultado
     - loop: se falha, retorna ao plan
   ```
   - Inspirado em: Grok Build (Plan-Review-Approve), Antigravity (Plan-Execute-Verify)

### Prioridade Média — Diferenciação

4. **MCP Server Nativo**
   - Se Hermes já não expõe MCP, adicionar
   - Permite usar qualquer ferramenta MCP como tool do Hermes

5. **ACP (Agent Client Protocol)**
   - Adotar protocolo aberto da xAI para comunicação entre agentes
   - Permite Hermes coordenar com Claude Code, Grok Build, etc.

6. **/skillify (1 comando salvar skill)**
   - Comando único: `/skillify` ou `hermes skill save`
   - Captura automaticamente a sessão atual como skill
   - Inspirado em: Grok Build `/skillify`

7. **Compartilhamento de skills entre agentes**
   - Importar skills do Claude Code (CLAUDE.md, AGENTS.md)
   - Exportar skills do Hermes para formato Claude/Grok

### Prioridade Baixa — Visão

8. **Auto-healing e self-correction**
   - Se tool falha, Hermes tenta automaticamente abordagem alternativa
   - Loop de retry inteligente com mudança de estratégia
   - Inspirado em: Claude Code (retry automático com fallback)

9. **Agendamento avançado**
   - Grok Automations-like: tarefas recorrentes com notificação
   - Hermes cronjob já existe — evoluir para UI visual

10. **Modo headless CI/CD**
    - Hermes rodando em pipeline sem terminal interativo
    - Flag `--headless` ou `--ci`

---

## 7. Implementando o Loop de Autocorreção no Hermes

### Workflow de Autocorreção (3 estágios)

```python
# Pseudocódigo do loop validativo
def executar_com_loop(tarefa):
    max_attempts = 3
    for attempt in range(max_attempts):
        # 1. PLANEJAR
        plano = agente.planejar(tarefa)
        # 2. VALIDAR PLANO
        erros = validar_plano(plano)
        if erros:
            feedback = "Erro no plano: " + erros
            tarefa = ajustar_plano(tarefa, feedback)
            continue
        # 3. EXECUTAR
        resultado = agente.executar(plano)
        # 4. VERIFICAR
        erros_exec = verificar_resultado(resultado, tarefa)
        if not erros_exec:
            return resultado  # SUCESSO
        # 5. CORRIGIR E LOOP
        tarefa = ajustar_com_feedback(tarefa, erros_exec)
    return falha_max_attempts()
```

### Hooks no Hermes (Exemplo)

```yaml
# ~/.hermes/hooks.yaml
hooks:
  pre_tool:
    - name: validate_permissions
      script: scripts/check_perms.sh
    - name: log_start
      script: scripts/log_tool_start.py
  post_tool:
    - name: validate_output
      condition: exit_code != 0
      action: retry_with_fallback
    - name: log_result
      script: scripts/log_result.py
  pre_response:
    - name: validate_response
      script: scripts/sanity_check.py
```

### Auto-healing Pattern (aprendido com Claude Code e Devin)

```
[Tarefa] → [Plano] → [Validação do Plano] → Falhou? → [Replanejar]
  ↓ OK
[Executar] → [Verificar Resultado] → Falhou? → [Tentar Alternativa] → [Loop ou Escalar]
  ↓ OK
[Reportar Sucesso]
```

---

## 8. Conclusão: Onde o Hermes Ganha e Onde Precisa Melhorar

### Hermes já VENCE em:
- ✅ **Open Source** — único 100% aberto
- ✅ **Provider-agnóstico** — não prende a um modelo
- ✅ **Memória persistente** — ninguém mais tem isso em coding agent
- ✅ **Self-hosted** — controle total dos dados
- ✅ **Multi-plataforma** — Telegram, Discord, SMS, Email — ninguém mais entrega em tantos canais
- ✅ **Skills** — sistema de conhecimento procedural único
- ✅ **Cron/Agendamento** — nativo e maduro
- ✅ **Custo** — usa DeepSeek/Ollama, mais barato que qualquer concorrente

### Hermes precisa EVOLUIR em:
- ❌ **Marketplace de skills público** — Claude tem 21.6K+, Grok tem plugins
- ❌ **Hooks (eventos)** — Claude Code e Grok Build têm
- ❌ **Loop Plan→Execute→Verify** — todos os concorrentes têm
- ❌ **MCP nativo** — Claude e Grok são nativos
- ❌ **/skillify 1-command** — Grok tem, Hermes precisa de 2+ comandos
- ❌ **Auto-healing** — Claude Code e Devin tentam alternativas automaticamente
- ❌ **Compatibilidade entre skills** — Grok importa skills do Claude, Hermes podia fazer o mesmo
