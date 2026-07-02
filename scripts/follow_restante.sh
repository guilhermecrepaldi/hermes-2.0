#!/usr/bin/env bash
# Segue todos os perfis NOVOS da planilha - execução contínua
source ~/.agent-reach-venv/Scripts/activate

PERFIS=(
    # NoCode e Webflow
    dana_webdesign mypageslab mgolinski_design
    # Website Designers
    websitedesigner_ng websitedesigners.la website_designer.india
    website.designer_ mvmtsocials
)

for user in "${PERFIS[@]}"; do
    echo "→ @$user"
    opencli instagram follow "$user" --window foreground --site-session ephemeral 2>&1 | head -2
    echo "  Aguardando..."
    sleep 6
done
echo "✅ Concluido!"
