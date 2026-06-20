#!/bin/bash
# Hermes Finalizer Loop
# Roda a cada 2 minutos ateh nao haver mais pendencias.
# Uso: bash finalizer-loop.sh

MAX_ITER=10
ITER=0
INTERVAL=120  # 2 minutos em segundos

echo "🚀 Hermes Finalizer Loop iniciado"
echo "   Intervalo: ${INTERVAL}s | Max iteracoes: $MAX_ITER"
echo ""

while [ $ITER -lt $MAX_ITER ]; do
    ITER=$((ITER + 1))
    echo "[$(date '+%H:%M:%S')] Iteracao $ITER/$MAX_ITER"
    
    # Roda o finalizer
    OUTPUT=$(cd /d/projetos/hermes-2.0 && python watchdog/finalizer.py 2>&1)
    echo "$OUTPUT"
    
    # Se clean, para
    if echo "$OUTPUT" | grep -q "Clean"; then
        echo ""
        echo "✅ Clean — finalizer encerrado"
        break
    fi
    
    # Se nao clean mas nao conseguiu resolver, para
    if echo "$OUTPUT" | grep -q "Falhou"; then
        echo ""
        echo "⚠️  Falha nao recuperavel — finalizer encerrado"
        break
    fi
    
    echo ""
    echo "⏳ Aguardando ${INTERVAL}s..."
    sleep $INTERVAL
done

if [ $ITER -ge $MAX_ITER ]; then
    echo "⚠️  Maximo de iteracoes atingido ($MAX_ITER)"
fi
