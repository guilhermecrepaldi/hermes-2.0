#!/bin/bash
# ============================================================
# HERMES FORT KNOX — Sistema de backup blindado
# ============================================================
# Este script é OBRIGATORIO rodar antes de qualquer update do
# Hermes Agent. Ele protege: config, skills, memorias, modulos.
# ============================================================

set -euo pipefail

HERMES_CONFIG="$HOME/AppData/Local/hermes"
BACKUP_ROOT="$HOME/hermes-2.0-hermes-backups"
DATE=$(date '+%Y-%m-%d_%H-%M-%S')
BACKUP_DIR="$BACKUP_ROOT/$DATE"

echo "╔══════════════════════════════════════╗"
echo "║   HERMES FORT KNOX — BACKUP BLINDADO  ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "📦 Backup em: $BACKUP_DIR"
echo ""

# 1. Config.yaml
mkdir -p "$BACKUP_DIR/config"
cp "$HERMES_CONFIG/config.yaml" "$BACKUP_DIR/config/" 2>/dev/null && echo "  ✅ config.yaml" || echo "  ❌ config.yaml NAO ENCONTRADO"

# 2. Skills (todas)
mkdir -p "$BACKUP_DIR/skills"
cp -r "$HERMES_CONFIG/skills/" "$BACKUP_DIR/skills/" 2>/dev/null && echo "  ✅ skills/ ($(find "$HERMES_CONFIG/skills" -name 'SKILL.md' 2>/dev/null | wc -l) skills)" || echo "  ❌ skills/ NAO ENCONTRADO"

# 3. Nossos modulos Python
mkdir -p "$BACKUP_DIR/modulos"
cp -r /d/projetos/hermes-2.0/watchdog/*.py "$BACKUP_DIR/modulos/" 2>/dev/null && echo "  ✅ watchdog/ ($(ls /d/projetos/hermes-2.0/watchdog/*.py 2>/dev/null | wc -l) modulos)" || echo "  ❌ watchdog/ NAO ENCONTRADO"

# 4. Memorias semanticas
mkdir -p "$BACKUP_DIR/memory"
cp -r "$HOME/.hermes/semantic_memory/" "$BACKUP_DIR/memory/" 2>/dev/null && echo "  ✅ semantic memory/" || echo "  ⚠️  semantic memory/ vazio"
cp -r "$HOME/.hermes/reflections/" "$BACKUP_DIR/memory/" 2>/dev/null && echo "  ✅ reflections/" || echo "  ⚠️  reflections/ vazio"

# 5. Hermes progress
cp /d/projetos/hermes-2.0/hermes-progress.md "$BACKUP_DIR/" 2>/dev/null && echo "  ✅ hermes-progress.md" || echo "  ⚠️  hermes-progress.md vazio"

# 6. Autoload skills (extraido do config)
grep "autoload_skills" "$HERMES_CONFIG/config.yaml" 2>/dev/null > "$BACKUP_DIR/autoload_skills.txt" && echo "  ✅ autoload registrado" || echo "  ⚠️  autoload nao encontrado"

# 7. Manifesto
cat > "$BACKUP_DIR/MANIFESTO.md" << EOF
# Hermes Fort Knox — Backup Manifesto

**Data:** $DATE
**Hermes Config:** $HERMES_CONFIG
**Projeto:** D:\\projetos\\hermes-2.0

## Conteudo
$(if [ -f "$BACKUP_DIR/config/config.yaml" ]; then echo "- config.yaml"; fi)
$(if [ -d "$BACKUP_DIR/skills" ]; then echo "- skills/ ($(find "$BACKUP_DIR/skills" -name 'SKILL.md' 2>/dev/null | wc -l) skills)"; fi)
$(if ls "$BACKUP_DIR/modulos/"*.py 2>/dev/null > /dev/null; then echo "- $(ls "$BACKUP_DIR/modulos/"*.py 2>/dev/null | wc -l) modulos Python"; fi)
$(if [ -f "$BACKUP_DIR/hermes-progress.md" ]; then echo "- hermes-progress.md"; fi)
$(if [ -f "$BACKUP_DIR/autoload_skills.txt" ]; then echo "- autoload config"; fi)

## Restauracao
Para restaurar:
  bash hermes-2.0-hermes-backups/restore.sh $DATE
EOF

echo ""
echo "📋 Manifesto criado"
echo ""
echo "✅ BACKUP CONCLUIDO: $BACKUP_DIR"
echo ""
echo "📊 Estatisticas:"
echo "   Skills: $(find "$BACKUP_DIR/skills" -name 'SKILL.md' 2>/dev/null | wc -l)"
echo "   Modulos: $(ls "$BACKUP_DIR/modulos/"*.py 2>/dev/null | wc -l)"
echo "   Tamanho: $(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)"
