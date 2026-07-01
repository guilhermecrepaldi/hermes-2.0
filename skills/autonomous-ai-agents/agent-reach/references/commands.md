# Agent Reach — Command Reference (Neo Hermes Context)

Caminhos absolutos para scripts no Windows:
```
watchdog/ = C:\Users\Home\neo-hermes\watchdog\
```

## Web (URLs)

```bash
python /c/Users/Home/neo-hermes/watchdog/read_url.py "URL"
python /c/Users/Home/neo-hermes/watchdog/read_url.py "URL" --max 3000
python /c/Users/Home/neo-hermes/watchdog/read_url.py "URL" --json
```

Jina Reader retorna markdown limpo. Gratuito, sem API key.
Bloqueia GitHub (451) — nesses casos, usar gh CLI.

## GitHub

```bash
gh repo view owner/repo
gh repo view owner/repo --json name,description,language,stargazerCount,forkCount
gh issue list --repo owner/repo --limit 5 --json title,state,updatedAt
gh search code "query" --repo owner/repo --limit 5
```

Se gh nao instalado: curl -s "https://r.jina.ai/https://github.com/owner/repo"

## RSS/Atom

```bash
python /c/Users/Home/neo-hermes/watchdog/read_feed.py "FEED_URL" --limit 5
python /c/Users/Home/neo-hermes/watchdog/read_feed.py "FEED_URL" --json
```

## YouTube

```bash
yt-dlp --dump-json "URL" 2>/dev/null
yt-dlp --write-auto-subs --sub-lang pt,en --skip-download --sub-format vtt -o "%(title)s" "URL" 2>/dev/null
```

## Roteamento

| Acao | Shell | Custo |
|------|-------|-------|
| Ler URL / RSS / GitHub / YouTube info | S1 (terminal) | $0 |
| Processar/resumir o conteudo lido | S3 (DeepSeek) | $0.15/1M |
