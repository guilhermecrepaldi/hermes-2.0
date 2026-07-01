# GitHub — Ler repositórios via gh CLI

## Pré-requisito

```bash
# gh CLI: https://cli.github.com
gh --version
```

Autenticar (uma vez):
```bash
gh auth login
```

## Comandos

### Info do repositório

```bash
# README + metadados
gh repo view owner/repo

# JSON estruturado
gh repo view owner/repo --json name,description,language,stargazerCount,forkCount,createdAt,updatedAt
```

### Issues

```bash
# Issues recentes
gh issue list --repo owner/repo --limit 5 --json title,state,updatedAt,labels,author

# Issue especifica
gh issue view 123 --repo owner/repo
```

### Buscar código

```bash
# Buscar no repo
gh search code "query" --repo owner/repo --limit 5

# Buscar repositorios
gh search repos "topic:llm language:python" --limit 5 --json name,description,stargazerCount
```

### Pull Requests

```bash
gh pr list --repo owner/repo --limit 5 --json title,state,updatedAt,author
gh pr view 123 --repo owner/repo
```

## Fallback

Se `gh` não estiver instalado:
```bash
curl -s "https://r.jina.ai/https://github.com/owner/repo"
```
