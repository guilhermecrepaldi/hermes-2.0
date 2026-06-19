#!/bin/bash
# ============================================================
# Hermes 2.0 — Backup & Restore
# Protege config.yaml e skills contra updates do Hermes Agent.
# ============================================================

HERMES_DIR="$HOME/AppData/Local/hermes"
BACKUP_DIR="$HOME/AppData/Local/hermes-backup"
DATE=$(date +%Y%m%d_%H%M%S)

case "${1:-}" in
  backup)
    echo "📦 Fazendo backup do Hermes..."
    mkdir -p "$BACKUP_DIR/snapshots/$DATE"
    
    # Config
    cp "$HERMES_DIR/config.yaml" "$BACKUP_DIR/snapshots/$DATE/config.yaml"
    echo "  ✅ config.yaml salvo"
    
    # Skills (backup incremental)
    mkdir -p "$BACKUP_DIR/skills"
    cp -r "$HERMES_DIR/skills/" "$BACKUP_DIR/skills/$DATE"
    echo "  ✅ skills ($(find "$HERMES_DIR/skills" -name SKILL.md | wc -l) skills) salvas"
    
    echo ""
    echo "📋 Backup completo em: $BACKUP_DIR/snapshots/$DATE"
    echo "   Para restaurar: $0 restore $DATE"
    ;;
    
  restore)
    SNAPSHOT="${2:-latest}"
    if [ "$SNAPSHOT" = "latest" ]; then
      SNAPSHOT=$(ls -1 "$BACKUP_DIR/snapshots/" | sort -r | head -1)
    fi
    
    echo "♻️ Restaurando snapshot: $SNAPSHOT"
    
    if [ ! -f "$BACKUP_DIR/snapshots/$SNAPSHOT/config.yaml" ]; then
      echo "❌ Snapshot nao encontrado: $SNAPSHOT"
      exit 1
    fi
    
    # Restaurar config
    cp "$BACKUP_DIR/snapshots/$SNAPSHOT/config.yaml" "$HERMES_DIR/config.yaml"
    echo "  ✅ config.yaml restaurado"
    
    echo ""
    echo "✅ Restaurado. Autoload ativo:"
    grep autoload_skills "$HERMES_DIR/config.yaml"
    ;;
    
  list)
    echo "📋 Snapshots disponiveis:"
    ls -1 "$BACKUP_DIR/snapshots/" 2>/dev/null | while read s; do
      if [ -f "$BACKUP_DIR/snapshots/$s/config.yaml" ]; then
        auto=$(grep autoload_skills "$BACKUP_DIR/snapshots/$s/config.yaml" 2>/dev/null || echo "sem autoload")
        echo "  📅 $s  →  $auto"
      fi
    done
    ;;
    
  auto)
    # Agenda backup automatico no .bashrc
    echo 'alias hermes-backup="bash ~/hermes-backup.sh backup"' >> ~/.bashrc
    echo "✅ Alias 'hermes-backup' adicionado ao .bashrc"
    echo "   Rode: hermes-backup"
    ;;
    
  *)
    echo "Uso: $0 {backup|restore [snapshot]|list|auto}"
    echo ""
    echo "  backup        Cria snapshot do config.yaml + skills"
    echo "  restore [id]  Restaura snapshot (padrao: latest)"
    echo "  list          Lista snapshots disponiveis"
    echo "  auto          Configura alias no .bashrc"
    ;;
esac
