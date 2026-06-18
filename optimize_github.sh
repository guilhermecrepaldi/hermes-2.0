#!/bin/bash
# ============================================================
# GitHub Profile Optimizer
# Automate: bio, pinned repos, topics, descriptions
# Uso: ./optimize_github.sh
# ============================================================

TOKEN="${GITHUB_TOKEN:-$(gh auth token)}"
USER="guilhermecrepaldi"
REPOS=(
  "hermes-2.0"
  "vagas-tech-scraper"
  "enem-data-hub"
  "drywall-performance-saas"
  "Crypto-Strategy"
)

echo "🚀 Otimizando perfil do GitHub: $USER"
echo "========================================"

# 1. Atualizar profile README (já feito)
echo "✅ Profile README: guilhermecrepaldi/guilhermecrepaldi"

# 2. Atualizar tópicos e descrições dos repositórios
for repo in "${REPOS[@]}"; do
  case "$repo" in
    hermes-2.0)
      desc="Orquestracao multi-shell com watchdog 24/7, jornal AI automatizado e pipeline de agentes autonomos"
      topics='["python","ai-agents","automation","watchdog","deepseek","coding-agent"]'
      ;;
    vagas-tech-scraper)
      desc="Scraper de vagas Python no Brasil - Programathor, GeekHunter, LinkedIn"
      topics='["python","web-scraping","data-analysis","job-market","brazil"]'
      ;;
    enem-data-hub)
      desc="Ferramenta para baixar, extrair e processar microdados do ENEM (INEP)"
      topics='["python","etl","data-science","education","brazilian-government"]'
      ;;
    drywall-performance-saas)
      desc="SaaS para gestao de performance em drywall com controle de equipes"
      topics='["php","saas","management","construction"]'
      ;;
    Crypto-Strategy)
      desc="Estrategia de trading automatizada com analise de dados em tempo real"
      topics='["python","trading","cryptocurrency","data-analysis"]'
      ;;
  esac
  
  echo "📦 Atualizando $repo..."
  curl -s -X PATCH \
    -H "Authorization: token $TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$USER/$repo" \
    -d "$(cat <<JSON
{
  "description": "$desc",
  "topics": $topics,
  "homepage": ""
}
JSON
)" > /dev/null
  echo "   ✅ $repo atualizado"
done

# 3. Verificar pinned repos (manual - GitHub Settings)
echo ""
echo "📌 Para fixar repos no perfil:"
echo "   Acesse: https://github.com/$USER?tab=repositories"
echo "   Clique em 'Customize your pinned repositories'"
echo "   Fixe os 6 principais repos"
echo ""
echo "   Recomendados:"
echo "   - hermes-2.0"
echo "   - vagas-tech-scraper"
echo "   - enem-data-hub"
echo "   - drywall-performance-saas"
echo "   - Crypto-Strategy"
echo "   - guilhermecrepaldi (profile README)"

echo ""
echo "✅ Otimizacao concluida!"
