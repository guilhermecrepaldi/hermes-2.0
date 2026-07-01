# 🏠 AMBIENTE — NEO HERMES (Source of Truth)
> **Criado:** 2026-07-01 | **Última verificação:** 2026-07-01
> **Propósito:** Toda sessão nova deve ler este documento primeiro.
> **Regra:** Se algo estiver diferente do descrito aqui, corrija ou atualize este documento.

---

## 1. ARQUITETURA
```
S3 (DeepSeek V4 Flash) = cérebro principal → fala DIRETO com DeepSeek
S1 (Ollama qwen2.5-coder:7b) = trabalhador local → tarefas $0

SEM HEADROOM. SEM PROXY. SEM :8787. SEM PONTO ÚNICO DE FALHA.
DeepSeek direto + Ollama compress inline (>2K chars).
```

## 2. CONFIG HERMES

**Arquivo:** `~/AppData/Local/hermes/config.yaml`

| Chave | Valor |
|-------|-------|
| `model.default` | `deepseek-v4-flash` |
| `model.provider` | `deepseek` |
| `delegation.provider` | `ollama` |
| `delegation.model` | `qwen2.5-coder:7b` |
| `delegation.base_url` | `http://localhost:11434/v1` |
| `autoload_skills` | `caveman-hermes,agent-reach,shellz-environment` |

## 3. ORQUESTRAÇÃO S1/S3

| Tarefa | Rota | Custo |
|--------|:----:|:-----:|
| `ls, git, pip, criar arquivo, compilar, testar` | **S1** → terminal + Ollama | **$0** |
| `ajustar CSS, verificar, formatar, contar LOC` | **S1** → Ollama qwen2.5-coder | **$0** |
| `comprimir contexto (>2K chars)` | **S1** → `ollama_compress.py` | **$0** |
| `delegate_task` (subagentes) | **S1** → Ollama (configurado) | **$0** |
| Arquitetura, debug complexo, análise, pesquisa | **S3** → DeepSeek V4 Flash | $0.15/M |

> **Regra:** Classificar ANTES de agir. Toda tarefa é S1 ou S3. Se for S1, não gaste tokens do DeepSeek.

## 4. OLLAMA

| Item | Valor |
|------|-------|
| **Versão** | 0.30.7 |
| **Porta** | 11434 |
| **Modelo S1** | `qwen2.5-coder:7b` (7.6B, Q4_K_M) |
| **Iniciar** | `ollama serve` (background) |
| **Compressão** | `watchdog/ollama_compress.py` — 99% economia (1700→9 tok) |

### Modelos instalados (14)
- **ESSENCIAIS:** `qwen2.5-coder:7b`, `qwen3-vl:4b`, `deepseek-coder:6.7b`
- **EXTRAS (manter?):** mistral, llama3.1, qwen2.5, qwen2.5:14b, gemma3, llama3.2, deepseek-coder-v2:lite, nomic-embed-text, qwen2.5-coder:1.5b-base, llama3

## 5. AGENT REACH

| Item | Caminho / Comando |
|------|-------------------|
| **Venv** | `~/.agent-reach-venv/` |
| **Ativar** | `source ~/.agent-reach-venv/Scripts/activate` |
| **Versão** | 1.5.0 |
| **Canais** | 11/15 ativos |
| **Diagnóstico** | `agent-reach doctor` |

### OpenCLI (backbone browser)
| Item | Valor |
|------|-------|
| **Versão** | 1.8.5 |
| **Instalação** | `npm install -g @jackwener/opencli` |
| **Extensão Chrome** | `C:\opencli-extension\` (carregar sem compactação) |
| **Daemon** | Porta 19825 |
| **Status** | `opencli doctor` |

### ⚠️ REGRA DE RAM (sempre usar)
```bash
opencli instagram profile "x" -f yaml --window background --site-session persistent
# Aliases (definidos em ~/.bashrc):
oi="opencli instagram --window background --site-session persistent"
ot="opencli twitter --window background --site-session persistent"
of="opencli facebook --window background --site-session persistent"
or="opencli reddit --window background --site-session persistent"
ob="opencli bilibili --window background --site-session persistent"
ox="opencli xiaohongshu --window background --site-session persistent"
```

## 6. REPO NEO-HERMES

| Item | Valor |
|------|-------|
| **Local** | `~/neo-hermes/` |
| **GitHub** | `guilhermecrepaldi/neo-hermes` |
| **Branch** | `main` |
| **Commits** | 115+ |
| **Skills trackeadas** | 27 skills |
| **Testes** | 20 arquivos, 219+ testes |

### Comandos úteis
```bash
cd ~/neo-hermes
python -m pytest tests/ -v                                   # Todos os testes
python -m pytest tests/test_shellz.py -v                     # Só roteamento
python -c "import sys; sys.path.insert(0,'watchdog'); from shellz import shellz; print(shellz.rotear('sua tarefa'))"
```

## 7. TELEMETRIA (OBRIGATÓRIA)

**Toda resposta** DEVE terminar com:
```
── telemetria ───────────────
  S1 ollama: N tok (economia $X.XXXX)
  S3 deep:   N tok = $X.XXXX
```

Formato completo (padrão):
```bash
⚡ [X]k tokens | Régua US$ 1/1M → US$ [Y] | DeepSeek → US$ [Z] | Cache → US$ [W] | 🏆 Economia: US$ [E]
```

## 8. DEPENDÊNCIAS PYTHON

### Venv do Hermes (principal — `/c/Users/Home/AppData/Local/hermes/hermes-agent/venv/`)
✅ feedparser ✅ yt_dlp ✅ requests ✅ rich ✅ pyyaml ✅ Pillow ✅ pytest
❌ openpyxl ❌ loguru ❌ flask

Instalar se precisar: `pip install openpyxl loguru flask`

### Venv Agent Reach (`~/.agent-reach-venv/`)
Tem suas próprias deps (agent-reach, loguru, win32-setctime)

## 9. RECUPERAÇÃO (PC formatou?)

1. Instalar Hermes Desktop
2. Clonar repo: `git clone https://github.com/guilhermecrepaldi/neo-hermes.git`
3. Seguir `~/neo-hermes/hermes-config-essentials.md`
4. Instalar Ollama + `ollama pull qwen2.5-coder:7b`
5. Instalar Agent Reach (skill `agent-reach` → referência `install-windows.md`)
6. Configurar autoload: `hermes config set autoload_skills "caveman-hermes,agent-reach,shellz-environment"`

## 10. COMANDOS RÁPIDOS

```bash
# Saúde
agent-reach doctor           # Status dos 15 canais
opencli doctor               # Status OpenCLI bridge
curl -s http://localhost:11434/api/version   # Ollama UP?

# Compressão via Ollama
cd ~/neo-hermes && python -c "import sys; sys.path.insert(0,'watchdog'); from ollama_compress import doctor; d=doctor(); print(f'Ollama: {d[\"ollama\"]}, Compress: {d[\"compress_ok\"]}')"

# Prospecção Instagram
source ~/.agent-reach-venv/Scripts/activate
oi profile "username" -f yaml     # Perfil
oi search "landing page" -f yaml  # Buscar novos
oi user "username" -f yaml        # Posts

# Testes
cd ~/neo-hermes && python -m pytest tests/test_shellz.py tests/test_ollama_compress.py tests/test_economy.py tests/test_telemetry.py -v
```
