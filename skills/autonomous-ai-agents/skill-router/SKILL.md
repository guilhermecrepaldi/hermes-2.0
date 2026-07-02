---
name: skill-router
description: "Router automatico de skills: analisa o contexto da mensagem do usuario e carrega a skill correta sem perguntar. DEVE ser a primeira skill no autoload."
category: autonomous-ai-agents
tags: [router, auto-load, context-analysis, efficiency]
---

# Skill Router

## Identidade

Esta skill é carregada PRIMEIRO em toda sessão. O agente DEVE, antes de responder qualquer mensagem, analisar o contexto e carregar automaticamente as skills relevantes.

## Regra Única e Obrigatória

**NUNCA pergunte "quer que eu carregue X". Carregue automaticamente.**

Toda mensagem do usuario passa por este router. O agente analisa palavras-chave, intenção e contexto, e carrega as skills sem pedir permissão.

## Mapa de Contexto → Skills

| Se o usuario diz/fala sobre | Carregue estas skills | Observacao |
|---|---|---|
| UX / Design / Interface / "feio" / "bonito" / layout | `skill_view(name='design-system-references')` + `skill_view(name='ux-audit')` | UX Audit usa browser_vision + taste-skill para analisar tela real |
| Segurança / Vazamento / Credencial / Senha / .env | `skill_view(name='codewriter-cybersecurity-audit')` | |
| Build / Compilação / Erro de instalação / Pip / npm | `skill_view(name='auto-healing')` + `skill_view(name='roteador-economico')` | |
| Teste / Debug / Bug / "quebrou" / Erro 500 / Falha | `skill_view(name='systematic-debugging')` + `skill_view(name='tdd')` | |
| Arquitetura / Refactor / Estrutura / Módulo / Clean code | `skill_view(name='software-architecture-review')` + `skill_view(name='code-audit-engine')` | |
| Pesquisa / Mercado / Concorrente / Artigo / Paper | `skill_view(name='harness-1')` + `skill_view(name='open-source-landscape-research')` | |
| Documentação / SPEC / README / Especificação | `skill_view(name='spec-agent')` + `skill_view(name='stack-docs')` | |
| Banco / SQL / Query / Schema | `skill_view(name='stack-docs')` | |
| IA / Modelo / API / Prompt / LLM / DeepSeek / Ollama | `skill_view(name='roteador-economico')` + `skill_view(name='provider-troubleshooting')` | |
| Git / GitHub / PR / Commit / Push / Branch | `skill_view(name='github-pr-workflow')` + `skill_view(name='github-auth')` | |
| Setup / Novo projeto / Iniciar / Comecar / Criar do zero | `skill_view(name='auto-assembly-workflow')` + `skill_view(name='auto-executor')` | |
| Performance / Lento / Otimizacao / Latencia | `skill_view(name='taste-skill')` + `skill_view(name='code-audit-engine')` | |
| Inteligencia / Raciocinio / Pensar / Analisar profundamente | `skill_view(name='systematic-debugging')` + `skill_view(name='code-audit-engine')` | Use ReasoningEngine (reasoning.py) chain-of-thought |
| Orquestracao / Tarefa complexa / Multi-passo / Pipeline | `skill_view(name='auto-assembly-workflow')` + `skill_view(name='auto-executor')` | Use TaskDecomposer + Orchestrator |
| Autonomia / Auto-recuperacao / Resilience / Fallback | `skill_view(name='auto-healing')` | Use AutoHealer com 12 estrategias |
| Memoria / Lembrar / Aprender / Repetir | `skill_view(name='output-coeso')` | Use SemanticMemory + Reflector |
| Proativo / Sugerir / Melhoria / "o que fazer" | `skill_view(name='code-audit-engine')` + `skill_view(name='taste-skill')` | Use ProactiveAnalyzer.scan_all() |
| Compactacao / Contexto grande / Historico longo | `skill_view(name='auto-healing')` | Use compactor.py (128k tokens) |
| Observabilidade / Log / Telemetria / Data Masking / Erro silencioso / Token tracking | `skill_view(name='cybersec-code-review')` | Audit de logs + logger_pro.py. Telemetry.mini_report() para tokens/custo |
| Telemetria / Token / Custo / Consumo API / Gasto | `skill_view(name='cybersec-code-review')` | telemetry.mini_report() exibe tokens, cloud vs local, custo ao final da resposta |
| Supabase / Banco / DB / Tabela / SQL / PostgreSQL / CRUD | `skill_view(name='stack-docs')` | Usar supabase_connector.py (SupabaseClient com select/insert/update/delete/rpc) |
| Browser / Chrome / CDP / Navegador / Extensao | usar ferramentas de browser diretamente | Conectar Chrome real: `--remote-debugging-port=9222` + `hermes config set browser.cdp_url`. Ver `cybersec-code-review/references/browser-cdp-connection.md` |\n| ***NENHUM dos acima*** | `skill_view(name='stack-docs')` + `skill_view(name='auto-executor')` + `skill_view(name='auto-healing')` + `skill_view(name='output-coeso')` | Fallback padrao |
| **Review de codigo / Codigo Python / PR review** 🆕 | `skill_view(name='python-reviewer')` | Carregar python-reviewer |
| **Seguranca / Auditoria / Credencial / LGPD / Secret / CVE** 🆕 | `skill_view(name='security-reviewer')` | Carregar security-reviewer |
| **Arquitetura / Design patterns / Acoplamento / Refactor grande** 🆕 | `skill_view(name='architecture-reviewer')` | Carregar architecture-reviewer |
| **Aprender / Pattern / Melhoria continua / Extrair licao** 🆕 | `skill_view(name='continuous-learning')` | Carregar continuous-learning |

## Fluxo

```
1. Usuario envia mensagem
2. Skill-router analisa (antes de qualquer resposta)
3. Identifica contexto (pode ser multiplo! ex: "debug + seguranca + orquestracao")
4. Carrega 1 ou mais skills com skill_view()
5. So ENTÃO responde, ja com as skills carregadas
6. Se contexto for complexo, carrega multiplas skills em batch
```

## Cache

Skills ja carregadas na sessao NAO sao recarregadas. Se skill_view(name='X') ja foi chamado na sessao, pular.

## Regras de Ouro

- **NUNCA pergunte** "quer que eu carregue X". Carregue automaticamente. SEMPRE.
- **NUNCA delete ou recrie uma skill existente.** Se a skill ja existe, use patch/edit para melhora-la. Deleter e recriar perde historico, linked files e metadados. A regra do usuario: "nao delete o que temos, implemente, melhore."
- **Contexto multiplo**: se o usuario fala de "debug + seguranca", carregue ambas
- **Sem delay**: carregue ANTES de responder, nao depois
- **Batch**: se 3+ skills matcham, carregue todas em uma rodada
- **NUNCA entregue pendencias**: se identificou que falta uma skill, carregue agora
- **Preferencia do usuario**: respostas diretas e funcionais, sem explicacoes desnecessarias

## Exemplos

```
Usuario: "essa interface esta muito feia"
-> skill-view('design-system-references') [54 refs]
-> skill-view('ux-audit') [checklist UX]

Usuario: "preciso debugar esse erro 500"
-> skill-view('systematic-debugging')
-> skill-view('tdd')

Usuario: "quero um deploy seguro"
-> skill-view('codewriter-cybersecurity-audit')
-> skill-view('auto-healing')

Usuario: "cria um handler novo"
-> skill-view('software-architecture-review')
-> skill-view('stack-docs')

Usuario: "analisa esse projeto e sugere melhorias"
-> skill-view('code-audit-engine')
-> skill-view('taste-skill')
-> ProactiveAnalyzer.scan_all()

Usuario: "constroi uma API completa"
-> skill-view('auto-assembly-workflow')
-> skill-view('auto-executor')
-> TaskDecomposer + Orchestrator

Usuario: "aprende com o que fizemos"
-> skill-view('output-coeso')
-> Reflector.reflect() + SemanticMemory.remember()
```
