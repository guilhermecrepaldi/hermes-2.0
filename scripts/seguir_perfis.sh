#!/usr/bin/env bash
# Seguir perfis no Instagram - execução direta (sem subprocess aninhado)
source ~/.agent-reach-venv/Scripts/activate

PERFIS=(
    landing.page_design landing.page.design landing.pagedesign
    hazel.landingpagedesigner webdia
    saaslandingpage thisi.saaslandingpage croissantsmoon
    saas.landingpage webuilder.gm
    _frontend_web_developer_ frontend.web.developer
    frontend_web_developer_ frontend_web_developer webticode
    dashkaacom alena_mitrohina ui__ux.designer gautam.designn
    ui.debbie ui_portfolio ui.fawad uidiksign
    uidesignportfolio ux.ui_portfolio ux_portfolio sk_visual_
    portfolio_uxui ux_ui_portfolio jaypee_ux
    ui.mob web.designinspiration webdesign.ox web.inspirations
    web_design_agency web.design.agency webdesignagency
    web_design_agency_ web.design_agency charm.digitalagency
    digital__agencyy mesondigital freshideas.digitalagency
    figma._.designer figma_designer_ figma_.designer figma_designer
    webdesigner_nocode umidjon_majiddev dana_webdesign
    mypageslab mgolinski_design
    websitedesigner_ng websitedesigners.la website_designer.india
    website.designer_ mvmtsocials
)

TOTAL=${#PERFIS[@]}
SEGUIDOS=0
FALHAS=0

echo "🚀 Seguindo $TOTAL perfis no Instagram..."
echo "   Conta: guilherme.crepaldi.dev"
echo ""

for i in "${!PERFIS[@]}"; do
    USER="${PERFIS[$i]}"
    NUM=$((i+1))
    printf "  [%02d/%02d] @%-30s ... " "$NUM" "$TOTAL" "$USER"

    RESULT=$(opencli instagram follow "$USER" --window foreground --site-session ephemeral 2>&1)
    if echo "$RESULT" | grep -q "Following"; then
        SEGUIDOS=$((SEGUIDOS+1))
        echo "✅ Seguindo"
    else
        FALHAS=$((FALHAS+1))
        echo "❌ $RESULT" | head -c 60
        echo ""
    fi

    sleep 4
done

echo ""
echo "──────────────────────────────────────"
echo "✅ Seguidos: $SEGUIDOS"
echo "❌ Falhas:   $FALHAS"
echo "📊 Total:    $TOTAL perfis"
