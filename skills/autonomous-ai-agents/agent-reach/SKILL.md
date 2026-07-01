---
name: agent-reach
description: "Acesso total à internet via TERMINAL — 15 canais: Web, GitHub, YouTube, RSS, Instagram, Twitter/X, Reddit, Facebook, LinkedIn, Bilibili, Xiaohongshu, V2EX, 雪球, busca semântica, 小宇宙播客. Zero servidor, zero porta, zero background."
category: autonomous-ai-agents
---

# Agent Reach — Pool de Acesso à Internet (15 Canais)

> Baseado no projeto open-source **Panniantong/agent-reach** (47k+ stars, 299+ commits).
> CLI: `agent-reach` (gerenciamento/instalação/diagnóstico) + upstream tools diretos (nunca wrapper).

## 🔴 Regras Absolutas

- NUNCA iniciar servidor, proxy, ou processo em background para isso
- Só chame comandos via terminal() QUANDO o usuário pedir
- NUNCA usar S3 pra baixar/ler. S3 só processa/resume
- NUNCA tentar scrap direto do Instagram/Twitter/Facebook — usar OpenCLI + browser login

## Roteamento S1/S3

1. **S1 (terminal, $0)** — Leitura/busca via upstream tools diretos
2. **S3 (DeepSeek)** — Processar/resumir/analisar o conteúdo lido

## Instalação (Windows — git-bash)

```bash
# 1. Criar venv dedicado (não poluir workspace)
python -m venv ~/.agent-reach-venv
source ~/.agent-reach-venv/Scripts/activate

# 2. Instalar agent-reach
pip install https://github.com/Panniantong/agent-reach/archive/main.zip

# 3. Setup base (5 canais: Web, GitHub, YouTube, RSS, V2EX)
agent-reach install --env=auto

# 4. Instalar OpenCLI (base para Instagram, Facebook, Reddit, 小红书)
npm install -g @jackwener/opencli

# 5. Ativar canais adicionais
agent-reach install --channels=instagram,facebook,reddit,twitter,linkedin,xiaohongshu

# 6. Verificar status
agent-reach doctor
```

**Sempre ativar o venv antes de usar:**
```bash
source ~/.agent-reach-venv/Scripts/activate
```

## Diagnóstico

```bash
agent-reach doctor
# Mostra status de cada canal: ✅ disponível, [!] precisa config, [X] não instalado
```

## Canais e Comandos

### 🌐 Web (Jina Reader — zero config)
```bash
curl -s "https://r.jina.ai/URL"
```
Retorna markdown limpo. Fallback: `https://r.jina.ai/http://URL`.

### 📦 GitHub (gh CLI — zero config)
```bash
# Info + README
gh repo view owner/repo

# JSON
gh repo view owner/repo --json name,description,language,stargazerCount,forkCount

# Issues
gh issue list --repo owner/repo --limit 5 --json title,state,updatedAt

# Código
gh search code "query" --repo owner/repo --limit 5
```

### 📡 RSS/Atom (feedparser — zero config)
```bash
python /c/Users/Home/neo-hermes/watchdog/read_feed.py "URL_DO_FEED" --limit 5
```

### 🎬 YouTube (yt-dlp — zero config)
```bash
# Info do vídeo
yt-dlp --dump-json "URL" 2>/dev/null

# Legenda automática
yt-dlp --write-auto-subs --sub-lang pt,en --skip-download --sub-format vtt -o "%(title)s" "URL" 2>/dev/null
```

### 💻 V2EX (API pública — zero config)
```bash
# Tópicos quentes
curl -s "https://www.v2ex.com/api/v2/topics/hot"
```

### 📷 Instagram (via OpenCLI — precisa extensão Chrome + login)
> ⚠️ **SEMPRE** usar `--window background --site-session persistent` para não abrir janelas Chrome e não consumir RAM extra!

```bash
# Perfil
opencli instagram profile "username" -f yaml --window background --site-session persistent

# Busca de usuários
opencli instagram search "query" -f yaml --window background --site-session persistent

# Posts recentes de um usuário
opencli instagram user "username" -f yaml --window background --site-session persistent

# Explore
opencli instagram explore -f yaml --window background --site-session persistent
```
**Aliases (definidos em ~/.bashrc):** `oi` = instagram, `ot` = twitter, `of` = facebook, `or` = reddit, `ob` = bilibili, `ox` = xiaohongshu

**Setup manual único:**
1. Instalar extensão OpenCLI no Chrome: https://github.com/jackwener/opencli/releases
2. chrome://extensions/ → Modo Desenvolvedor → "Carregar sem compactação"
3. Estar logado no Instagram.com pelo Chrome
4. Verificar: `opencli doctor` (mostrar "Extension: connected")

### 📘 Facebook (via OpenCLI — precisa extensão Chrome + login)
```bash
opencli facebook search "query" -f yaml
opencli facebook profile username -f yaml
opencli facebook groups -f yaml
```

### 🐦 Twitter/X (via twitter-cli — precisa Cookie)
```bash
# Instalar
pip install twitter-cli

# Configurar Cookie (usuário precisa exportar do Chrome via Cookie-Editor)
agent-reach configure twitter-cookies "header_string"

# Buscar
twitter search "query" -f yaml
```

### 📖 Reddit (via OpenCLI — precisa extensão Chrome + login)
```bash
# Via OpenCLI (recomendado — reusa login do Chrome)
opencli reddit search "query" -f yaml

# Alternativa: rdt-cli + Cookie
pip install rdt-cli
```

### 💼 LinkedIn (Jina Reader público + linkedin-scraper-mcp)
```bash
# Perfil público (Jina Reader)
curl -s "https://r.jina.ai/https://www.linkedin.com/in/username/"

# Completo (linkedin-scraper-mcp)
pip install linkedin-scraper-mcp
```

### 📺 Bilibili (bili-cli — sem login para busca)
```bash
# Busca
bili search "query"

# Info vídeo
bili video "BV1xx"
```

### 📕 小红书 (via OpenCLI — precisa extensão Chrome + login)
```bash
opencli xiaohongshu search "query" -f yaml
opencli xiaohongshu note "note_id" -f yaml
```

### 🔍 Busca Semântica (Exa — via mcporter)
```bash
npm install -g mcporter
mcporter config add exa https://mcp.exa.ai/mcp
```

### 📈 雪球/Xueqiu (via Cookie)
```bash
agent-reach configure --from-browser chrome
```

### 🎙️ 小宇宙播客 (via Groq Whisper — precisa Groq API Key grátis)
```bash
# Configurar key
agent-reach configure groq-key gsk_xxxxx

# Transcrever
bash ~/.agent-reach/tools/xiaoyuzhou/transcribe.sh "URL_DO_EPISÓDIO"
```

## Fallbacks Gerais

- Jina Reader falhou? Esperar 2s e tentar de novo. Se persistir: "URL pode estar bloqueada"
- gh não instalado? Usar Jina Reader em `https://github.com/owner/repo`
- yt-dlp não instalado? `pip install yt-dlp`
- feedparser não instalado? `pip install feedparser`
- OpenCLI não conectado? Pedir usuário verificar extensão Chrome + `opencli daemon restart`

## Pós-processamento

Conteúdo lido:
- < 2000 chars → entrega direto
- > 2000 chars → oferece resumo ou passa pro S3
- Listas (issues, resultados, buscas) → bullets

## Pitfalls (Windows)

- **OpenCLI no Windows**: npm install -g funciona, mas extensão Chrome é MANUAL
- **GitHub download URL com maiúscula**: OpenCLI extension ZIP está em `https://github.com/jackwener/OpenCLI/releases/...` (O maiúsculo). Usar `opencli` (minúsculo) dá 404.
- **agent-reach doctor** não mostra Instagram instalado até OpenCLI extension conectar
- **yt-dlp JS runtime**: precisa config no Windows: `New-Item -ItemType Directory -Force -Path "$env:APPDATA\yt-dlp"` + config com `--js-runtimes node`
- **mcporter** falha no Windows (WinError 2) — necessário `npm install -g mcporter` manual
- **Sempre ativar venv**: `source ~/.agent-reach-venv/Scripts/activate` antes de comandar

## Referências

| Categoria | Arquivo | Conteúdo |
|-----------|---------|----------|
| 📷 Instagram + OpenCLI | `references/instagram-opencli.md` | Setup passo a passo, comandos, troubleshooting |
| 🖥️ Instalação Windows | `references/install-windows.md` | Roteiro completo de instalação no Windows (git-bash) |
| 📖 Web (URLs) | `references/web.md` | Jina Reader: comandos, fallbacks, exemplos |
| 📦 GitHub | `references/github.md` | gh CLI: repo view, issues, code search, PRs |
| 🎬 YouTube | `references/video.md` | yt-dlp: info, legendas, transcrição |
| 📡 RSS | `references/rss.md` | Feedparser: feeds, limit, JSON output |
