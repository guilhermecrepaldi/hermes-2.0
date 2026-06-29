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
# Python 3.11+ (obrigatorio para torch)
# Se nao tiver: https://www.python.org/downloads/

# Hermes Agent (se ainda nao tiver)
# Seguir: https://hermes-agent.nousresearch.com/docs

# Headroom + torch (compressao real)
pip install headroom-ai
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Ollama (IA local S1)
# Download: https://ollama.com/download
ollama pull qwen2.5-coder:7b

# Rust (opcional, para _core do headroom)
# Download: https://rustup.rs
rustup default stable
pip install --force-reinstall headroom-ai
```

## ─── 3. CONFIGURAR HERMES ────────────────────

```bash
# Caminho: C:\Users\<seu_user>\AppData\Local\hermes\

# Copiar configs do repo:
copy neo-hermes\hermes\config.example.yaml %LOCALAPPDATA%\hermes\config.yaml
copy neo-hermes\hermes\env.example %LOCALAPPDATA%\hermes\.env

# EDITAR .env e colocar sua DEEPSEEK_API_KEY real:
# DEEPSEEK_API_KEY=sk-sua_chave_aqui

# Copiar scripts:
copy neo-hermes\hermes\headroom_proxy.py %LOCALAPPDATA%\hermes\hermes-agent\
copy neo-hermes\hermes\ativar_headroom.bat %LOCALAPPDATA%\hermes\
copy neo-hermes\hermes\rollback_headroom.bat %LOCALAPPDATA%\hermes\
copy neo-hermes\hermes\startup_headroom.bat %LOCALAPPDATA%\hermes\
copy neo-hermes\hermes\kill_port_8787.bat %LOCALAPPDATA%\hermes\

# Copiar watchdog:
copy neo-hermes\hermes\headroom_watchdog.py %LOCALAPPDATA%\hermes\scripts\watchdog\

# Copiar skills (opcional):
xcopy neo-hermes\skills\caveman-hermes %LOCALAPPDATA%\hermes\skills\autonomous-ai-agents\caveman-hermes\ /E /I
```

## ─── 4. AUTOLOAD (config.yaml) ───────────────

Editar `%LOCALAPPDATA%\hermes\config.yaml`:

```yaml
model:
  base_url: http://localhost:8787/v1   # Headroom proxy
  default: deepseek-v4-flash
  provider: deepseek

delegation:
  model: qwen2.5-coder:7b              # S1 = Ollama local
  provider: ollama
  base_url: http://localhost:11434/v1

agent:
  autoload_skills: "caveman-hermes,output-coeso,roteador-economico,telemetria,shellz-environment,auto-healing,repo-cloner,auto-implementer,complex-reasoner,assertive-executor,skill-router"
```

## ─── 5. INICIAR TUDO ─────────────────────────

```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Headroom Proxy (usar venv do Hermes!)
%LOCALAPPDATA%\hermes\hermes-agent\venv\Scripts\python.exe ^
  %LOCALAPPDATA%\hermes\hermes-agent\headroom_proxy.py ^
  --port 8787 --upstream https://api.deepseek.com

# Verificar
curl http://localhost:8787/health

# Abrir Hermes Desktop
hermes
```

## ─── 6. STARTUP AUTOMATICO (opcional) ────────

Para Headroom + Ollama iniciarem com o Windows:

```bash
# Copiar script para pasta Startup:
copy neo-hermes\hermes\startup_headroom.bat ^
  "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\"
```

Ou manual: executar `startup_headroom.bat` antes do Hermes.

## ─── 7. VERIFICAR TUDO ───────────────────────

```bash
# Headroom esta comprimindo?
curl http://localhost:8787/health
# "requests": N > 0 = comprimindo

# Ollama esta respondendo?
curl http://localhost:11434/api/tags

# Testar chamada via proxy:
curl -X POST http://localhost:8787/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" ^
  -d "{\"model\":\"deepseek-v4-flash\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}],\"max_tokens\":5}"
```

## ─── 8. SCRIPTS UTEIS ────────────────────────

```
hermes/ativar_headroom.bat     → Ativa Headroom no config.yaml
hermes/rollback_headroom.bat   → Volta ao DeepSeek direto
hermes/startup_headroom.bat    → Inicia Headroom + Ollama
hermes/kill_port_8787.bat      → Mata processos na porta
```

## ─── ECONOMIA ────────────────────────────────

```
Shellz S1 (Ollama)   → R$ 0,00 por tarefa simples
SmartCrusher (torch) → 35% menos tokens de input (tool outputs JSON)
Caveman skill        → 65-75% menos tokens de output
```

## ─── SE FORMATAR O PC ───────────────────────

```
1. Instalar: Python, Git, Ollama, Hermes Agent
2. git clone https://github.com/guilhermecrepaldi/neo-hermes.git
3. Seguir passos 3 a 6 acima
4. ~15 minutos
```

## ─── REGRAS ETERNAS ─────────────────────────

- NUNCA deletar shellz-environment do autoload
- NUNCA usar DeepSeek para tarefas S1 (use Ollama)
- NUNCA omitir telemetria no final da resposta
- SEMPRE: backup antes de update do Hermes
- SEMPRE: 1M tok = US$ 1.00 na telemetria
