# NEO HERMES — Guia de Recuperacao Total
# Se formatar o PC, siga ESTE arquivo para restaurar TUDO.
# https://github.com/guilhermecrepaldi/neo-hermes

## ═══════════════════════════════════════════════
## 1. CLONAR REPOSITORIOS
## ═══════════════════════════════════════════════

```bash
# Repo principal (NEO HERMES)
git clone https://github.com/guilhermecrepaldi/neo-hermes.git
cd neo-hermes

# Audit (skills backup)
git clone https://github.com/guilhermecrepaldi/hermes-2.0.git _audit
```

## ═══════════════════════════════════════════════
## 2. INSTALAR DEPENDENCIAS
## ═══════════════════════════════════════════════

```bash
# Python (no venv do Hermes)
python -m pip install --force-reinstall "headroom-ai[ml]"
python -m pip install requests supabase

# last30days (pesquisa em tempo real)
git clone https://github.com/mvanhorn/last30days-skill.git ~/last30days-skill

# Rust toolchain (para headroom Rust core)
winget install Rustlang.Rustup
rustup default stable
```

## ═══════════════════════════════════════════════
## 3. RESTAURAR .env
## ═══════════════════════════════════════════════

Arquivo: `C:\Users\<user>\AppData\Local\hermes\.env`

```env
# IA Local OBRIGATORIA
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b
HERMES_FORCE_LOCAL_PROCESSING=1

# DeepSeek API (S3 main brain)
DEEPSEEK_API_KEY=sk-sua_key_aqui

# Headroom Proxy
HEADROOM_PORT=8787
HEADROOM_UPSTREAM=https://api.deepseek.com

# last30days (pesquisa)
LAST30DAYS_DIR=C:\Users\<user>\last30days-skill
LAST30DAYS_REDDIT_BACKEND=public
LAST30DAYS_POLYMARKET_BACKEND=public
LAST30DAYS_GITHUB_BACKEND=public
LAST30DAYS_WEB_BACKEND=public
LAST30DAYS_HN_BACKEND=public
LAST30DAYS_MEMORY_DIR=C:\Users\<user>\Documents\Last30Days

# Supabase (se aplicavel)
SUPABASE_URL=https://bxmeatmsnmveisaqltfp.supabase.co
SUPABASE_KEY=sb_secret_sua_key
```

## ═══════════════════════════════════════════════
## 4. CONFIGURAR HERMES
## ═══════════════════════════════════════════════

```bash
# Autoload — shellz-environment SEMPRE primeiro
hermes config set agent.autoload_skills "shellz-environment,skill-router,ux-audit,stack-docs,auto-executor,auto-healing,output-coeso,roteador-economico,spec-agent,taste-skill,design-system-references"

# Modelo principal (S3 = DeepSeek)
hermes config set model.default deepseek-v4-flash
hermes config set model.provider deepseek
hermes config set model.base_url http://localhost:8787/v1

# Delegacao (S1 = Ollama)
hermes config set delegation.model qwen2.5-coder:7b
hermes config set delegation.provider ollama
hermes config set delegation.base_url http://localhost:11434/v1

# Browser (Chrome real)
hermes config set browser.cdp_url http://localhost:9222

# Compression
hermes config set compression.threshold 0.35
hermes config set compression.target_ratio 0.15
```

## ═══════════════════════════════════════════════
## 5. RESTAURAR SKILLS
## ═══════════════════════════════════════════════

```bash
# shellz-environment (skill principal)
cp -r _audit/shellz-environment/ "C:\Users\<user>\AppData\Local\hermes\skills\autonomous-ai-agents\shellz-environment"

# last30days (pesquisa) — ja clonado no passo 2
cp -r _audit/last30days-skill/ "C:\Users\<user>\AppData\Local\hermes\skills\research\last30days"
```

## ═══════════════════════════════════════════════
## 6. VERIFICAR TUDO
## ═══════════════════════════════════════════════

```bash
# Verificar instalacao
python -c "from headroom import __version__; print('headroom:', __version__)"
python -c "import sys; sys.path.insert(0,'watchdog'); from shellz import shellz; print('shellz OK')"
python -c "import sys; sys.path.insert(0,'watchdog'); from telemetry import telemetry; print('telemetry OK')"
python -c "import sys; sys.path.insert(0,'watchdog'); from headroom_bridge import doctor; print(doctor())"

# Verificar Ollama
ollama list

# Verificar last30days
ls ~/last30days-skill/

# Rodar testes
python -m pytest tests/ -q
```

## ═══════════════════════════════════════════════
## 7. INICIAR
## ═══════════════════════════════════════════════

```bash
# 1. Iniciar Ollama (se necessario)
ollama serve &
ollama run qwen2.5-coder:7b  # primeira vez baixa o modelo

# 2. Iniciar Headroom Proxy (auto-start pelo Hermes)
bash headroom-start.sh

# 3. Iniciar Chrome com CDP (browser real)
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:\Users\<user>\hermes-chrome-profile"

# 4. Iniciar Hermes
hermes
```

## ═══════════════════════════════════════════════
## REGRAS ETERNAS
## ═══════════════════════════════════════════════

- NUNCA remover shellz-environment do autoload
- NUNCA usar DeepSeek para tarefas S1 (Ollama)
- NUNCA omitir telemetria ao final de resposta
- NUNCA perder as melhorias — backup antes de update
- SEMPRE: bash hermes-fort-knox.sh backup antes de update
- SEMPRE: telemetry.mini_report() no final de toda resposta
- SEMPRE: S3 = DeepSeek (main brain), S1 = Ollama (worker)
- SEMPRE: 1M tok = $1.00 USD na telemetria
