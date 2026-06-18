#!/bin/bash
# ============================================================
# GitHub Auto-Contributor
# Mantém o gráfico de contribuições verde diariamente
# Uso: ./auto_contrib.sh
# ============================================================

REPO_DIR="/d/projetos/_audit"
cd "$REPO_DIR" || exit 1

# Arquivo de log de contribuição
CONTRIB_FILE="daily_log.md"

# Garantir que o arquivo existe
if [ ! -f "$CONTRIB_FILE" ]; then
  echo "# Daily Contributions Log" > "$CONTRIB_FILE"
  echo "" >> "$CONTRIB_FILE"
  echo "Log automático de contribuições diárias." >> "$CONTRIB_FILE"
  echo "" >> "$CONTRIB_FILE"
fi

# Adicionar entrada do dia
echo "## $(date '+%Y-%m-%d %H:%M')" >> "$CONTRIB_FILE"
echo "- Estudos e melhorias contínuas no ecossistema Hermes 2.0" >> "$CONTRIB_FILE"
echo "- Pesquisa de arquitetura de coding agents" >> "$CONTRIB_FILE"
echo "" >> "$CONTRIB_FILE"

# Commit e push
git add "$CONTRIB_FILE"
git commit -m "chore: contribuicao diaria $(date '+%Y-%m-%d')"
git push origin master 2>/dev/null || git push origin main 2>/dev/null

echo "✅ Contribuicao registrada: $(date '+%Y-%m-%d %H:%M')"
