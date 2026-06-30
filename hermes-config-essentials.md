# NEO HERMES — Setup Completo em outro PC
# https://github.com/guilhermecrepaldi/neo-hermes
# Siga em ordem. 15 minutos. Nada se perde.

## ─── 1. CLONAR ───────────────────────────────

```bash
git clone https://github.com/guilhermecrepaldi/neo-hermes.git
cd neo-hermes
```

## ─── 2. INSTALAR DEPENDENCIAS ─────────────────

```bash
# Python 3.11+
# Se nao tiver: https://www.python.org/downloads/

# Hermes Agent (se ainda nao tiver)
# Seguir: https://hermes-agent.nousresearch.com/docs

# Dependencias Python
pip install requests

# Ollama (IA local S1)
# Download: https://ollama.com/download
ollama pull qwen2.5-coder:7b
```

## ─── 3. CONFIGURAR HERMES ────────────────────

```bash
# Caminho: C:\\Users\\<seu_user>\\AppData\\Local\\hermes\\

# EDITAR config.yaml com sua DEEPSEEK_API_KEY:
# provider: deepseek
# model: deepseek-v4-flash

# OU copiar do repo:
copy neo-hermes\\config.example.yaml %LOCALAPPDATA%\\hermes\\config.yaml
```

### Config Mínima funcional:

```yaml
model:
  default: deepseek-v4-flash
  provider: deepseek

delegation:
  model: qwen2.5-coder:7b
  provider: ollama
  base_url: http://localhost:11434/v1

agent:
  autoload_skills: "caveman-hermes,shellz-environment,output-coeso,roteador-economico,skill-router,auto-healing"
```

## ─── 4. AUTOLOAD (config.yaml) ───────────────

Editar `%LOCALAPPDATA%\\hermes\\config.yaml`:

```yaml
model:
  default: deepseek-v4-flash
  provider: deepseek

delegation:
  model: qwen2.5-coder:7b
  provider: ollama
  base_url: http://localhost:11434/v1

agent:
  autoload_skills: "caveman-hermes,shellz-environment,output-coeso,roteador-economico,skill-router,auto-healing"
```

## ─── 5. INICIAR ─────────────────────────

```bash
# So precisa do Ollama rodando:
ollama serve

# Abrir Hermes Desktop
hermes
```

## ─── 6. SCRIPTS UTEIS ────────────────────────

```bash
# Iniciar tudo:
ollama serve
hermes

# Verificar Ollama:
curl http://localhost:11434/api/tags

# Verificar Hermes:
hermes --version
```

## ─── ECONOMIA ────────────────────────────────

```
Shellz S1 (Ollama)   → R$ 0,00 por tarefa simples
Caveman skill        → 65-75% menos tokens de output
Ollama compress      → Compressao inline sem proxy
```

## ─── SE FORMATAR O PC ───────────────────────

```
1. Instalar: Git, Ollama, Hermes Agent
2. git clone https://github.com/guilhermecrepaldi/neo-hermes.git
3. pip install requests
4. ~10 minutos
```

## ─── REGRAS ETERNAS ─────────────────────────

- NUNCA usar proxy entre Hermes e DeepSeek
- NUNCA usar DeepSeek para tarefas S1 (use Ollama)
- NUNCA omitir telemetria no final da resposta
- Caveman no autoload para economia de output
- 1M tok = US$ 1.00 na telemetria
