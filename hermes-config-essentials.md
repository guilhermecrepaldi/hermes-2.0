# NEO HERMES — Guia de Recuperacao Total
# Se formatar o PC, siga ESTE arquivo para restaurar TUDO.
# https://github.com/guilhermecrepaldi/neo-hermes

## ─── 1. CLONAR ───────────────────────────────

```bash
git clone https://github.com/guilhermecrepaldi/neo-hermes.git
cd neo-hermes
```

## ─── 2. DEPENDENCIAS ─────────────────────────

```bash
# Python
pip install headroom-ai

# Ollama (IA local S1)
winget install Ollama.Ollama
ollama pull qwen2.5-coder:7b

# Rust (opcional, para compressao headroom avancada)
winget install Rustlang.Rustup
rustup default stable
pip install --force-reinstall headroom-ai
```

## ─── 3. RESTAURAR CONFIG ─────────────────────

```bash
# Caminho: C:\Users\<user>\AppData\Local\hermes\
copy neo-hermes\hermes\config.example.yaml config.yaml
copy neo-hermes\hermes\env.example .env
# Editar .env e colocar sua DEEPSEEK_API_KEY real
```

## ─── 4. INICIAR TUDO ─────────────────────────

```bash
# 1. Ollama
ollama serve

# 2. Headroom Proxy
cd neo-hermes\hermes
python headroom_proxy.py --port 8787 --upstream https://api.deepseek.com

# 3. Verificar
curl http://localhost:8787/health

# 4. Abrir Hermes Desktop
hermes
```

## ─── 5. SCRIPTS UTEIS ───────────────────────

```
hermes/ativar_headroom.bat    → Ativacao segura do Headroom
hermes/rollback_headroom.bat  → Rollback em 1 clique
hermes/kill_port_8787.bat     → Limpar processos na porta
```

## ─── 6. ECONOMIA REAL ────────────────────────

```
Shellz S1 (Ollama)  → R$ 0,00 por tarefa simples
Headroom proxy      → Compressao quando torch disponivel
Caveman skill       → 65-75% menos tokens de output
```

## ─── REGRAS ETERNAS ─────────────────────────

- NUNCA deletar shellz-environment do autoload
- NUNCA usar DeepSeek para tarefas S1 (use Ollama)
- NUNCA omitir telemetria no final da resposta
- SEMPRE: backup antes de update do Hermes
- SEMPRE: 1M tok = US$ 1.00 na telemetria
