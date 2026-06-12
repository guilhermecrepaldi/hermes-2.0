---
name: open-notebook
description: "open-notebook — open-source NotebookLM implementation with REST API, local execution, multi-format support (PDF, HTML, Markdown, EPUB), and full data privacy"
category: research
tags: [auto-gerado, innovation-scanner, notebooklm, rag, research, open-source]
---

# open-notebook — Skill Auto-Gerado

## Fonte
Extraído da Edição #002 do TOP OF THE HOUR — IA (app-002-02)
Card: "open-notebook: Implementação Open-Source do NotebookLM com Mais Flexibilidade"

## O que é
open-notebook (29.2k estrelas) é uma implementação open-source do Google NotebookLM, oferecendo as mesmas funcionalidades com mais flexibilidade: múltiplos formatos de fonte (PDF, HTML, Markdown, EPUB), API REST customizável e execução local sem enviar dados para a nuvem.

Ideal para quem quer um assistente de pesquisa pessoal com controle total dos dados.

## Como implementar no Hermes 2.0

```bash
# Clonar e instalar
git clone https://github.com/lfnovo/open-notebook
cd open-notebook
pip install -r requirements.txt

# Iniciar servidor (execução local)
python server.py --port 8000

# API REST
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"source": "paper.pdf", "question": "sumarize este artigo"}'
```

## Comandos
```bash
# Analisar documento local
python analyze.py --file paper.pdf --query "principais conclusões"

# Iniciar com interface web
python server.py --ui
```

## Referência
- https://github.com/lfnovo/open-notebook
- Fonte: GitHub Trending (29.2k estrelas)
