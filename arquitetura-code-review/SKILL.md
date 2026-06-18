---
name: arquitetura-code-review-loops
description: "Arquitetura de code review e loops de correção de código baseada em práticas do Nubank, Google, Netflix, Spotify e outras big techs. Inclui processos, ferramentas, quality gates, CI/CD, revisão automatizada com IA, inner source e métricas."
category: software-development
tags: [code-review, arquitetura, loops, pr-review, ci-cd, qualidade, eng-pratices, ia]
---

# Arquitetura de Code Review e Loops de Correção

## Visão Geral

Baseado nas práticas documentadas de **Nubank, Google, Netflix, Spotify** e no estado-da-arte de ferramentas de revisão automatizada (2024-2026).

---

## 1. Nubank — Engenharia e Revisão

### Princípios
- **Revisão obrigatória em todo PR** — nenhum código vai a produção sem passar por review
- **Inner Source** — repositórios internos abertos para contribuição entre times, com processo similar ao open source
- **Qualidade em cada estágio** — testes automatizados, canary deployments, feature flags, rollouts controlados
- **Deploy incremental e reversível** — feature flags permitem ativar/desativar sem novo deploy
- **AI integrada ao workflow** — AI tools em code generation, automated quality checks, accelerated code reviews

### Pipeline de Revisão
```
[Commit] → [Pre-commit Hooks] → [CI: Lint + Testes + SAST] → [Aprovação Automática Gate]
  → [PR Aberto] → [Review Humano (LGTM)] → [Code Owner Aprova] → [Merge] → [Canary Deploy]
```

### Caso Nubank + Devin (Refatoração 6M linhas)
- **Problema**: Monólito ETL de 8 anos, 6M+ linhas de código para sub-módulos
- **Processo Devin**: Agente autônomo → analisa → mapeia dependências → implementa → cria branch → abre PR
- **Revisão humana**: Única etapa que requer humano — revisa o PR gerado pelo agente
- **Resultados**: 12x melhoria em horas de engenharia, 20x economia de custos
- **Fonte**: https://devin.ai/customers/nubank

---

## 2. Google — Processo de Code Review

### Estrutura
- **Revisão obrigatória** — toda CL (changelist) precisa de aprovação
- **Duas ferramentas internas**: Critique (maioria) e Gerrit (open source, projetos públicos)
- **Processo em 2 etapas**: LGTM de peer + aprovação de code owner/readability

### Readability Process
- **Conceito**: Certificação de que o engenheiro escreve código no estilo correto da linguagem
- **Como funciona**: Mentor aleatório revisa o código do engenheiro; após aprovações consistentes, o engenheiro recebe certificação "readability" naquela linguagem
- **Objetivo**: Garantir que código seja claro, consistente e sustentável em escala
- **Benefício**: Revisor confia mais no código de quem tem readability, acelera revisões futuras

### Quality Gates do Google
1. **Pre-submit**: Lint, testes unitários, análise estática, verificação de dependências
2. **Code Review**: LGTM humano + readability + code owner
3. **Post-submit**: Testes de integração, canary, monitoramento

### Referência
- https://google.github.io/eng-practices/review/
- https://abseil.io/resources/swe-book/html/ch09.html (Software Engineering at Google)

---

## 3. Netflix — CI/CD e Qualidade

### Pipeline
```
[Planejamento: JIRA] → [Coding: Java/outras] → [Pre-commit: Testes + Lint]
  → [Build: Spinnaker] → [Testes Automatizados (milhares)] → [Canary Deploy]
  → [Production] → [Monitoring: Atlas/Telegraf] → [Incident Response]
```

### Práticas
- **PR size limit**: 400 linhas — para manter revisão eficiente
- **Automated testing**: Milhares de testes integrados ao pipeline
- **Spinnaker**: CI/CD próprio, multi-cloud, deploys canários
- **Feature flags**: Ativação/desativação sem novo deploy
- **Chaos engineering**: Chaos Monkey testa resiliência em produção

---

## 4. Spotify — Cultura e Guildas

### Estrutura
- **Squads**: Times autônomos e multi-disciplinares
- **Guildas**: Comunidades de prática transversais (ex: "Code Review Guild")
- **Inner Source**: Cultura de compartilhamento de repositórios entre squads

### Revisão
- Revisão obrigatória entre pares dentro do squad
- Guildas definem padrões e melhores práticas de revisão
- Ferramentas automatizadas para lint, formatação, testes

---

## 5. Arquitetura de Loops de Correção (Recomendada)

### Fluxo Completo

```
┌──────────────────────────────────────────────────────────────────┐
│                        LOOP DE CORREÇÃO                         │
│                                                                  │
│  [1] PR Aberto                                                   │
│       │                                                          │
│       ▼                                                          │
│  [2] QUALITY GATES (automático)                                  │
│       ├── Lint / Formatação                                      │
│       ├── Testes Unitários                                       │
│       ├── SAST (SonarQube, Semgrep)                              │
│       ├── Análise de Dependências (Snyk, Dependabot)             │
│       ├── Verificação de Tamanho do PR                           │
│       └── Verificação de Cobertura de Testes                     │
│       │                                                          │
│       ▼ (se alguma falha)                                        │
│  [3] FEEDBACK AUTOMÁTICO                                         │
│       ├── Mensagem no PR com lista de problemas                  │
│       └── Bloqueio de merge até correção                         │
│       │                                                          │
│       ▼ (se tudo OK)                                             │
│  [4] REVIEW HUMANO                                               │
│       ├── Revisor atribuído (code owner / squad)                 │
│       ├── Comentários inline no diff                             │
│       └── Aprovação (LGTM) ou Solicitação de Mudanças            │
│       │                                                          │
│       ▼ (se mudanças solicitadas)                                │
│  [5] CORREÇÃO → LOOP                                             │
│       ├── Autor implementa correções                             │
│       ├── NOVOS commits no mesmo PR                              │
│       ├── Quality Gates rodam novamente (etapa 2)                │
│       └── Revisor reavalia                                       │
│       │                                                          │
│       ▼ (após aprovação)                                         │
│  [6] MERGE GATE                                                  │
│       ├── Code Owner aprovação final                             │
│       ├── Merge commit                                           │
│       └── Disparo CI/CD de deploy                                │
│       │                                                          │
│       ▼                                                          │
│  [7] PÓS-MERGE                                                   │
│       ├── Deploy canário                                         │
│       ├── Testes de integração                                   │
│       ├── Monitoramento (logs, métricas, alertas)                │
│       └── Rollback automático se anomalia                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Implementação Prática com GitHub Actions

```yaml
# .github/workflows/code-review-gates.yml
name: Code Review Gates
on: [pull_request]

jobs:
  quality-gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Lint
        run: make lint

      - name: Unit Tests
        run: make test

      - name: SAST - Semgrep
        uses: semgrep/semgrep-action@v1

      - name: Dependency Check
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: PR Size Check
        uses: actions/github-script@v7
        with:
          script: |
            const additions = context.payload.pull_request.additions;
            if (additions > 400) {
              core.setFailed(`PR too large: ${additions} lines (max 400)`);
            }
```

### Ferramentas para cada Gate

| Gate | Ferramentas Open Source | Comerciais |
|------|----------------------|------------|
| **Lint** | ESLint, Prettier, Black, Ruff, golangci-lint | SonarQube |
| **Testes** | pytest, jest, vitest, go test | — |
| **SAST** | Semgrep, SonarQube CE, Bandit | Snyk Code, Checkmarx |
| **Dependências** | Dependabot, Renovate | Snyk, Black Duck |
| **Segurança** | OWASP ZAP, Trivy | Snyk, Wiz |
| **Cobertura** | pytest-cov, c8, JaCoCo | CodeCov |
| **Review IA** | Kodus (open source) | GitHub Copilot, Cursor, Devin |
| **Infra as Code** | Checkov, tfsec | Snyk IaC |

### Ferramentas de Revisão com IA (2025-2026)

| Ferramenta | Tipo | Modelo | Features |
|-----------|------|--------|----------|
| **GitHub Copilot Code Review** | Automatizado | Pago (GitHub) | Revisão automática em PRs, comentários inline |
| **Kodus / Kody** | Open Source | Gratuito | Review que aprende workflow do time, qualidade/segurança/performance |
| **Cursor Bugbot** | Automatizado | Pago | /review command, detecção de bugs e segurança |
| **Devin** | Agente autônomo | Pago | Cria PRs completos, migração, refatoração |
| **Baz AI Code Review** | Automatizado | Pago | Agentes de review customizados por time/domínio |
| **Qodo (CodiumAI)** | Automatizado | Freemium | PR review com contexto, testes sugeridos |

### Métricas de Efetividade

| Métrica | O que mede | Alvo |
|---------|-----------|------|
| **PR Cycle Time** | Tempo entre abertura e merge | < 24h |
| **PR Size** | Linhas alteradas por PR | < 400 |
| **Review Depth** | Comentários por PR review | 3-10 |
| **First Response Time** | Tempo até primeiro review | < 4h |
| **Re-review Rate** | % de PRs que precisam de 2+ revisões | < 30% |
| **Bug Escape Rate** | Bugs que passaram pelo review | < 5% |
| **Deploy Frequency** | Deploys por semana | Diário+ |

---

## 6. Resumo da Arquitetura Recomendada

### Minimum Viable Code Review (para começar amanhã)
1. ✅ **Pre-commit hooks** (lint + formatação)
2. ✅ **CI com testes** rodando em todo PR
3. ✅ **PR obrigatório** (sem push direto pra main)
4. ✅ **Quality Gate automatizado** (lint + tests + SAST)
5. ✅ **Code Owners** definidos
6. ✅ **Review humano obrigatório** (pelo menos 1 LGTM)

### Padrão Big Tech (meta a médio prazo)
1. ✅ Tudo acima +
2. ✅ **Readability/mentoring** (estilo Google)
3. ✅ **Revisão com IA** (Copilot, Kodus, ou similar)
4. ✅ **Tamanho máximo de PR** (400 linhas)
5. ✅ **Deploy canário** com feature flags
6. ✅ **Métricas de revisão** monitoradas
7. ✅ **Inner source** entre times
8. ✅ **Post-merge monitoring** com rollback automático

### Loop de Correção Típico
```
PR → [Gates Automáticos] → Falha? → Feedback → Correção → Loop
                         → OK?    → Review Humano → Mudanças? → Loop
                                                   → OK? → Merge → Deploy → Monitor
```
