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

| Se o usuario diz/fala sobre | Carregue estas skills |
|---|---|
| UX / Design / Interface / "feio" / "bonito" / layout | `skill_view(name='design-system-references')` |
| Segurança / Vazamento / Credencial / Senha / .env | `skill_view(name='codewriter-cybersecurity-audit')` |
| Build / Compilação / Erro de instalação / Pip / npm | `skill_view(name='auto-healing')` + `skill_view(name='roteador-economico')` |
| Teste / Debug / Bug / "quebrou" / Erro 500 / Falha | `skill_view(name='systematic-debugging')` + `skill_view(name='tdd')` |
| Arquitetura / Refactor / Estrutura / Módulo / Clean code | `skill_view(name='software-architecture-review')` + `skill_view(name='code-audit-engine')` |
| Pesquisa / Mercado / Concorrente / Artigo / Paper | `skill_view(name='harness-1')` + `skill_view(name='open-source-landscape-research')` |
| Documentação / SPEC / README / Especificação | `skill_view(name='spec-agent')` + `skill_view(name='stack-docs')` |
| Banco / SQL / Query / Schema | `skill_view(name='stack-docs')` |
| IA / Modelo / API / Prompt / LLM / DeepSeek / Ollama | `skill_view(name='roteador-economico')` + `skill_view(name='provider-troubleshooting')` |
| Git / GitHub / PR / Commit / Push / Branch | `skill_view(name='github-pr-workflow')` + `skill_view(name='github-auth')` |
| Setup / Novo projeto / Iniciar / Começar / Criar do zero | `skill_view(name='auto-assembly-workflow')` + `skill_view(name='auto-executor')` |
| Performance / Lento / Otimização / Latência | `skill_view(name='taste-skill')` + `skill_view(name='code-audit-engine')` |
| ***NENHUM dos acima*** | `skill_view(name='stack-docs')` + `skill_view(name='auto-executor')` + `skill_view(name='auto-healing')` + `skill_view(name='output-coeso')` |

## Fluxo

```
1. Usuario envia mensagem
2. Skill-router analisa (antes de qualquer resposta)
3. Identifica contexto (pode ser multiplo! ex: "debug + seguranca")
4. Carrega 1 ou mais skills com skill_view()
5. Só ENTÃO responde, ja com as skills carregadas
6. Se contexto for complexo, carrega multiplas skills em batch
```

## Cache

Skills ja carregadas na sessao NAO sao recarregadas. Se skill_view(name='X') ja foi chamado na sessao, pular.

## Exemplos

```
Usuario: "essa interface está muito feia"
→ skill-view('design-system-references') [54 referencias visuais]

Usuario: "preciso debugar esse erro 500"
→ skill-view('systematic-debugging')

Usuario: "quero um deploy seguro"
→ skill-view('codewriter-cybersecurity-audit')
→ skill-view('auto-healing')

Usuario: "cria um handler novo"
→ skill-view('software-architecture-review')
→ skill-view('stack-docs')
```
