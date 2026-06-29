#!/usr/bin/env bash
# Headroom Proxy — Script de startup OBRIGATORIO
# Inicia o proxy de compressao de contexto antes do Hermes
# Uso: bash headroom-start.sh
# Adicionar ao startup do Hermes

HEADROOM_PORT=${HEADROOM_PORT:-8787}
HEADROOM_UPSTREAM=${HEADROOM_UPSTREAM:-https://api.deepseek.com}
WATCHDOG_DIR="$(dirname "$0")"

echo "Iniciando Headroom Proxy na porta $HEADROOM_PORT..."
echo "Upstream: $HEADROOM_UPSTREAM"
echo "Watchdog: $WATCHDOG_DIR"

# Verificar se ja esta rodando
if curl -sf http://localhost:$HEADROOM_PORT/health > /dev/null 2>&1; then
    echo "Headroom Proxy ja esta rodando em :$HEADROOM_PORT"
else
    # Iniciar em background
    cd "$WATCHDOG_DIR"
    python watchdog/headroom_proxy.py &
    HEADROOM_PID=$!
    echo "PID: $HEADROOM_PID"
    
    # Aguardar pronto
    for i in $(seq 1 10); do
        if curl -sf http://localhost:$HEADROOM_PORT/health > /dev/null 2>&1; then
            echo "Headroom Proxy pronto! (${i}s)"
            break
        fi
        sleep 1
    done
fi

# Health check final
curl -s http://localhost:$HEADROOM_PORT/health | python -m json.tool
