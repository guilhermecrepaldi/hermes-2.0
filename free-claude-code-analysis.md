# Análise free-claude-code → Melhorias no Hermes

## Sobre o free-claude-code

**36.4k★ | 5.7k forks | 712 commits | Python 3.14 | MIT**
Proxy que roteia chamadas Anthropic/OpenAI → 17 providers (NVIDIA NIM, OpenRouter, DeepSeek, Gemini, Ollama, etc).

## Arquitetura Revelada

```
free-claude-code/
├── api/              # FastAPI routes + service layer
│   └── app.py        # create_app() → FastAPI
├── core/
│   ├── anthropic/    # Protocolo Anthropic Messages API
│   ├── openai_responses/  # Protocolo OpenAI Responses API
│   ├── rate_limit.py      # Rate limiting (token bucket)
│   └── trace.py           # Tracing/observability
├── providers/
│   ├── registry.py   # (19KB) Registro central de providers
│   ├── base.py       # Transport base class
│   ├── error_mapping.py # (10KB) Mapa de erros provider→padrão
│   └── (17 providers)    # Cada um: transports + adapter
├── config/
│   ├── settings.py   # Settings global
│   └── catalog.py    # Catálogo de modelos
├── cli/              # fcc-claude, fcc-codex launchers
├── messaging/        # Discord/Telegram bots
├── server.py         # Entrypoint (5 linhas)
└── pyproject.toml    # Python 3.14, uv, ruff, ty, pytest
```

## 7 Melhorias Imediatas para o Hermes

### 🔴 1. Provider Registry (CRÍTICO)
free-claude-code has `providers/registry.py` (19KB) com 17 providers registrados.
**Hermes hoje:** providers hardcoded em core.py.
**Implementar:** `providers/registry.py` + `providers/base.py` — cada provider é um módulo separado com transporte próprio.

### 🔴 2. Rate Limiting (CRÍTICO)
free-claude-code has `core/rate_limit.py` + `providers/rate_limit.py` (10KB).
**Hermes hoje:** zero rate limiting.
**Implementar:** Token bucket per-provider, com fallback para local quando excedido.

### 🟡 3. Admin UI (ALTO VALOR)
free-claude-code has `/admin` UI FastAPI.
**Hermes hoje:** config editada manualmente.
**Implementar:** FastAPI minimalista (`api/app.py`) com formulário para config.

### 🟡 4. Error Mapping (ALTO VALOR)
free-claude-code has `providers/error_mapping.py` (10KB).
**Hermes hoje:** erros genéricos.
**Implementar:** Mapa de erro provider→padrão com fallbacks.

### 🟢 5. Transport Pattern (MÉDIO VALOR)
free-claude-code has `providers/transports/` — cada transport implementa interface base.
**Hermes hoje:** chamadas diretas.
**Implementar:** ProviderTransport (base) + HTTPTransport + LocalTransport.

### 🟢 6. Launchers (MÉDIO VALOR)
free-claude-code has `cli/` — fcc-claude, fcc-codex.
**Hermes hoje:** comandos soltos em hermes_workbench.py.
**Implementar:** hermes-claude, hermes-codex wrappers.

### ⚪ 7. Model Picker (FUTURO)
free-claude-code has native `/v1/models` endpoint + model catalog.
**Hermes hoje:** modelo fixo.
**Implementar:** Catálogo de modelos com `hermes /model` comando.

## Plano de Implementação

```
FASE 1 (agora): Provider Registry + Rate Limiting
FASE 2 (próximo): Admin UI + Error Mapping
FASE 3 (futuro): Launchers + Model Picker
```
