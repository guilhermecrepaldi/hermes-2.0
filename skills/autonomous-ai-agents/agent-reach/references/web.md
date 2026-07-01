# Web — Ler qualquer URL via Jina Reader

## Comando base

```bash
python watchdog/read_url.py "URL" [--max CHARS] [--json]
```

## Exemplos

```bash
# Ler pagina completa
python watchdog/read_url.py "https://example.com/article"

# Ler primeiros 3000 chars
python watchdog/read_url.py "https://example.com/longo" --max 3000

# Saida JSON com metadados
python watchdog/read_url.py "https://example.com" --json
```

## Fallback

Se Jina Reader falhar (HTTP 451 = blocked, 403 = forbidden, timeout):
1. Tentar de novo apos 2s
2. Se persistir, avisar: "URL pode estar bloqueada ou inacessivel"

## Uso direto via curl (sem Python)

```bash
curl -s "https://r.jina.ai/URL" | head -c 8000
```

## Dependencias

Nenhuma — usa urllib (stdlib) + Jina Reader gratuito.
