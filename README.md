# Hermes 2.0 — Orquestrador Multi-Shell Autônomo

> Um sistema integrado de orquestração de agentes de IA com watchdog 24/7, jornal automatizado, pipeline multi-shell e deploy contínuo.

## Arquitetura

```
┌──────────────────────────────────────────┐
│              HERMES 2.0                  │
│         (um único sistema)               │
└──────────────────────────────────────────┘
         │               │              │
┌────────┴────────┐ ┌────┴─────┐ ┌──────┴──────┐
│   CRON Nativo   │ │  SKILLS  │ │  WATCHDOG   │
│  ─────────────  │ │ ──────── │ │  ─────────  │
│ 07/13/19h Jornal│ │ index-   │ │  Cron 1min  │
│ 04:00   Backup  │ │ news-    │ │  → verifica │
│ * * * * Guardian│ │ daily    │ │  → inicia   │
│                 │ │ workbench│ │  → mata     │
│                 │ │ pipeline │ │  → recovery │
│                 │ │ live-seo │ │             │
└─────────────────┘ └──────────┘ └─────────────┘
```

## Componentes

### 🛡️ Watchdog 24/7 (`/watchdog/`)
Monitoramento contínuo do Hermes Agent. Detecta travamentos, loops infinitos e processos zumbis.

| Arquivo | Função |
|---------|--------|
| `watchdog_hermes.bat` | Loop batch puro que verifica log, CPU e health |
| `watchdog_invisible.vbs` | Launcher VBS — executa sem abrir janela cmd |
| `watchdog_guardian.bat` | Cron guardian (a cada 1 minuto) — reinicia se cair |

**Proteções:**
- ⏱️ Timeout: log parado >25 min → kill + recovery
- 🔄 Loop detection: 5x mesma tool call → kill
- 💀 Processo zumbi: CPU 0% por 5min → kill

### 📰 Jornal TOP OF THE HOUR — IA (`/jornal/`)
Jornal diário de IA para engenheiros, gerado automaticamente 3x/dia.

- **Formato cascade:** Hardware → Arquitetura → Apps → Estratégia
- **36+ matérias/edição** de 26+ fontes
- **Abas por dia** com transições suaves
- **Teleprompter** com suporte a OBS/live (espaço avança, Esc sai)
- **SEO dinâmico** para YouTube (título, descrição, tags, thumbnail)
- **Fundo claro** profissional (tema light `#f5f5f0`)

### 🧠 Skills Customizados (`/hermes/skills/`)

| Skill | Descrição |
|-------|-----------|
| `index-news-daily` | Geração do jornal + revisor ortográfico + catálogo 212 modelos |
| `workbench-pipeline` | Orquestração multi-shell com handoff entre modelos |
| `live-seo-agent` | Geração de metadados SEO para YouTube/Google |

### ⏰ Cron Jobs

| Job | Schedule | Função |
|-----|----------|--------|
| Jornal diário | 07:00, 13:00, 19:00 | Gera/atualiza edição do dia |
| Backup completo | 04:00 | Backup do projeto + config + skills + cron + memória |
| Watchdog guardian | A cada 1 minuto | Monitora e reinicia watchdog |

## Como usar

### Iniciar o watchdog manualmente
```bash
wscript.exe D:\projetos\hermes-watchdog\watchdog_invisible.vbs
```

### Verificar status
```bash
cat ~/hermes-watchdog/watchdog_state.json
```

### Gerar edição do jornal manualmente
```bash
hermes run "Gere a edicao do dia do TOP OF THE HOUR - IA"
```

## Tecnologias

- **Hermes Agent** (Nous Research) — plataforma base
- **DeepSeek** — modelo de raciocínio principal
- **Ollama** — IA local (Shell 1)
- **Batch puro** — watchdog sem dependências
- **HTML/CSS/JS** — jornal em arquivo único

## GitHub

Projeto aberto para contribuição e estudo.
Commits automáticos a cada implementação.

---

**Hermes 2.0** — Construído em cima do [Hermes Agent](https://hermes-agent.nousresearch.com) da Nous Research.
