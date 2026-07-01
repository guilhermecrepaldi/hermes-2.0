# YouTube — Info + Legendas via yt-dlp

## Pré-requisito

```bash
pip install yt-dlp
```

## Comandos

### Info do vídeo

```bash
yt-dlp --dump-json "URL" 2>/dev/null | python -c "
import sys, json
d = json.load(sys.stdin)
print(f'Titulo: {d[\"title\"]}')
print(f'Duracao: {d[\"duration\"]}s')
print(f'Canal: {d.get(\"channel\",\"?\")}')
print(f'Views: {d.get(\"view_count\",\"?\")}')
print(f'Upload: {d.get(\"upload_date\",\"?\")}')
"
```

### Baixar legenda automática

```bash
# Legendas em portugues ou ingles
yt-dlp --write-auto-subs --sub-lang pt,en --skip-download --sub-format vtt -o "%(title)s" "URL" 2>/dev/null
```

Depois ler o arquivo .vtt gerado (fica no diretório atual).

### Fallback: transcrição via whisper (se configurado)

```bash
# Se tiver Groq ou OpenAI configurado no agent-reach
agent-reach transcribe "URL"
```

## Dependencias

- `yt-dlp` (pip)
- Para transcrição: ffmpeg (opcional)
