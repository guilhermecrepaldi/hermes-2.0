---
name: headroom
description: "Compress tool outputs, RAG chunks, and logs by 60-95% before sending to LLMs — saves context window space and API costs"
category: autonomous-ai-agents
tags: [auto-gerado, innovation-scanner, compression, tokens, optimization]
---

# headroom — Tool Output Compression for LLMs

## Fonte
Extraído da Edição #002 do TOP OF THE HOUR — IA
Card: "headroom: Compressão de Tool Output para LLM — 60-95% Menos Tokens, Mesmas Respostas" (app-002-01)

## O que é
headroom (22.8k estrelas no GitHub) é uma biblioteca Python open-source que comprime tool outputs, logs, arquivos e chunks RAG antes de enviá-los ao LLM. Reduz 60-95% do consumo de tokens sem afetar a qualidade das respostas.

Oferece três modos de uso:
1. **Library** — importar diretamente no código Python
2. **Proxy** — age como intermediário transparente entre sua aplicação e a API do LLM
3. **MCP Server** — servidor do Model Context Protocol para integrar com ferramentas MCP-compatíveis

## Como implementar no Hermes 2.0

### Instalação
```bash
pip install headroom
```

### Uso como library (modo mais prático para Hermes)
```python
from headroom import compress

# Comprime tool output antes de enviar ao LLM
tool_output = open("large_log.txt").read()
compressed = compress(tool_output, target_ratio=0.3)  # reduz a 30% do tamanho original

# headroom mantém as informações essenciais
print(f"Original: {len(tool_output)} chars → Comprimido: {len(compressed)} chars")
```

### Uso como proxy
```bash
# Inicia proxy na porta 8080 que comprime requests automaticamente
headroom proxy --port 8080 --target http://localhost:11434/v1/chat/completions
```

### Uso como servidor MCP
```bash
headroom mcp-server --port 9000
```

## Comandos
```bash
pip install headroom
headroom --help
headroom proxy --help
headroom mcp-server --help
```

## Integração com Hermes
- Use no pipeline de tool calls para comprimir outputs grandes antes de voltarem ao LLM
- Use como proxy para comprimir requests de RAG automaticamente
- O modo MCP Server é compatível com o ecossistema de ferramentas do Hermes

## Referência
https://github.com/chopratejas/headroom
