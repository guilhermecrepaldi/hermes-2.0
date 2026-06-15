---
name: copilot-coding-agent
description: "GitHub Copilot Coding Agent — agente autônomo que recebe issues diretamente do GitHub, implementa código e abre PRs autonomamente com integração nativa ao ecossistema GitHub"
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, github, copilot, coding-agent, pr-automation]
---

# Copilot Coding Agent — Skill Auto-Gerado

## Fonte
Extraído da Edição #005 do TOP OF THE HOUR — IA
Card: "Editor Wars 2026: Cursor, Windsurf e GitHub Copilot Disputam o Trono dos IDEs com IA Agêntica — Copilot Coding Agent Agora Recebe Issues e Abre PRs"

## O que é
O **GitHub Copilot Coding Agent** é um agente autônomo de codificação integrado nativamente ao ecossistema GitHub. Diferente de coding agents genéricos, ele:

1. **Recebe issues** diretamente do GitHub Issues — pode ser atribuído como "assignee" a uma issue
2. **Implementa autonomamente** — analisa o problema, escreve código, cria testes
3. **Abre Pull Requests** — submete a solução como PR com descrição automática
4. **Integração nativa** — funciona dentro do ecossistema GitHub sem configuração adicional

Faz parte do GitHub Copilot, concorrendo com Claude Code (Anthropic), Codex CLI (OpenAI) e Cursor (Anysphere).

## Como implementar no Hermes 2.0

### 1. Habilitar no repositório
```bash
# No GitHub, instale o GitHub Copilot com permissão de agente
# Ou use via GitHub CLI:
gh extension install github/gh-copilot
```

### 2. Atribuir uma issue ao agente
```
# Adicione o label "copilot" a uma issue, ou mencione @copilot
# O agente automaticamente:
# 1. Lê a descrição da issue
# 2. Clona o repositório
# 3. Implementa a solução
# 4. Abre um PR
```

### 3. Usar via GitHub CLI
```bash
# Criar uma issue e delegar ao Copilot
gh issue create --title "Implementar feature X" --body "Descrição..." --label "copilot"

# Verificar PRs gerados pelo agente
gh pr list --author "github-copilot"
```

### 4. Integração com o pipeline Hermes
O Hermes pode usar o Copilot Coding Agent como backend de automação de PRs:

```python
# Exemplo conceitual: delegar issue ao Copilot
import subprocess

def delegate_to_copilot(repo, issue_number):
    result = subprocess.run([
        "gh", "issue", "develop", str(issue_number),
        "--name", "copilot-coding-agent"
    ], capture_output=True, text=True)
    return result.stdout
```

## Comandos
```bash
# Via GitHub CLI (se disponível)
gh issue develop <issue-number> --name copilot

# Habilitar no repositório
gh copilot configure

# Verificar status
gh copilot status
```

## Dependências
- GitHub Copilot subscription (Individual, Business ou Enterprise)
- GitHub CLI (`gh`) instalado e autenticado
- Acesso ao repositório com permissão de escrita

## Comparação
| Aspecto | Copilot Coding Agent | Claude Code | Hermes Agent |
|---------|---------------------|-------------|--------------|
| Integração GitHub | Nativa | Manual | Manual |
| Abre PRs | ✅ Automático | ✅ Via CLI | Manual |
| Provider | OpenAI/Microsoft | Anthropic | Configurável |

## Referência
- GitHub Copilot Blog: https://github.blog/news-insights/product-news/github-copilot-coding-agent/
- Documentação: https://docs.github.com/en/copilot
- Fonte: GitHub Blog / VentureBeat
