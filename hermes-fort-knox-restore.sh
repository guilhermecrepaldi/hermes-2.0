#!/bin/bash
# ============================================================
# HERMES FORT KNOX — Restore
# ============================================================
# Uso: bash hermes-fort-knox.sh restore <data>
#      bash hermes-fort-knox.sh list
#      bash hermes-fort-knox.sh auto
# ============================================================

set -euo pipefail

HERMES_CONFIG="$HOME/AppData/Local/hermes"
BACKUP_ROOT="$HOME/hermes-2.0-hermes-backups"
ACTION="${1:-backup}"

case "$ACTION" in
    backup)
        bash "$(dirname "$0")/hermes-fort-knox.sh"
        ;;
    restore)
        DATE="${2:-latest}"
        if [ "$DATE" = "latest" ]; then
            DATE=$(ls -1 "$BACKUP_ROOT" 2>/dev/null | sort -r | head -1)
        fi
        BACKUP_DIR="$BACKUP_ROOT/$DATE"
        if [ ! -d "$BACKUP_DIR" ]; then
            echo "❌ Backup nao encontrado: $BACKUP_DIR"
            exit 1
        fi
        echo "Restaurando: $DATE"
        [ -f "$BACKUP_DIR/config/config.yaml" ] && cp "$BACKUP_DIR/config/config.yaml" "$HERMES_CONFIG/config.yaml" && echo "  ✅ config restaurado"
        [ -d "$BACKUP_DIR/skills" ] && cp -r "$BACKUP_DIR/skills/"* "$HERMES_CONFIG/skills/" 2>/dev/null && echo "  ✅ skills restauradas"
        echo "✅ Restaurado: $DATE"
        ;;
    list)
        echo "Backups disponiveis:"
        ls -1 "$BACKUP_ROOT" 2>/dev/null | sort -r || echo "  (nenhum)"
        ;;
    *)
        echo "Uso: bash hermes-fort-knox.sh [backup|restore [data]|list]"
        exit 1
        ;;
esac
