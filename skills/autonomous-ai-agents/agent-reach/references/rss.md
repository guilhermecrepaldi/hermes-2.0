# RSS — Ler feeds via feedparser

## Comando

```bash
python watchdog/read_feed.py "URL_DO_FEED" [--limit N] [--json]
```

## Exemplos

```bash
# Hacker News
python watchdog/read_feed.py "https://hnrss.org/frontpage" --limit 5

# TechCrunch
python watchdog/read_feed.py "https://techcrunch.com/feed/" --limit 5

# ArsTechnica
python watchdog/read_feed.py "https://feeds.arstechnica.com/arstechnica/index" --limit 5

# Saida JSON (para processamento automatico)
python watchdog/read_feed.py "URL" --json
```

## Saida esperada

```
📡 Título do Feed
   https://link-do-feed
   20 entries | ultimas 5:

1. Titulo da noticia
   https://link-da-noticia
   [Data de publicacao]
   Resumo da noticia...
```

## Dependencias

```bash
pip install feedparser
```

## Dicas

- Usar `--limit 5` por padrao (mais que isso enche contexto)
- Usar `--json` se for processar por S3
- Feeds comuns: HN, TechCrunch, ArsTechnica, dev.to, medium
