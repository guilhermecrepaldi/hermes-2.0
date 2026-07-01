# Instalação Agent Reach no Windows (git-bash)

## Pré-requisitos
- Python 3.10+
- Node.js (para mcporter + OpenCLI)
- gh CLI (GitHub CLI)
- git-bash (MSYS2)

## Passo a passo

```bash
# 1. Criar venv dedicado
python -m venv ~/.agent-reach-venv

# 2. Ativar venv (sempre antes de usar)
source ~/.agent-reach-venv/Scripts/activate

# 3. Instalar agent-reach
pip install https://github.com/Panniantong/agent-reach/archive/main.zip

# 4. Setup base
agent-reach install --env=auto

# 5. Instalar OpenCLI (base para Instagram/Facebook/Reddit/小红书)
npm install -g @jackwener/opencli

# 6. Instalar busca semântica
npm install -g mcporter
mcporter config add exa https://mcp.exa.ai/mcp

# 7. Ativar canais
agent-reach install --channels=all

# 8. Corrigir YouTube (JS runtime)
mkdir -p "$APPDATA/yt-dlp"
echo "--js-runtimes node" > "$APPDATA/yt-dlp/config"

# 9. Verificar
source ~/.agent-reach-venv/Scripts/activate
agent-reach doctor
```

## Notas

- **mcporter** falha se instalado via agent-reach no Windows (WinError 2). Instalar manualmente com npm.
- **OpenCLI extension** precisa ser instalada manualmente no Chrome (não dá pra automatizar).
- **Sempre ativar venv** antes de chamar comandos agent-reach ou opencli.
