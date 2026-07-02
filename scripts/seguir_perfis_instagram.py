#!/usr/bin/env python3
"""Segue todos os novos perfis no Instagram via OpenCLI."""
import subprocess, time, json, sys

# Lista de novos usernames (extraídos das buscas)
NOVOS = [
    # Landing Page Design
    "landing.page_design", "landing.page.design", "landing.pagedesign",
    "hazel.landingpagedesigner", "webdia",
    "saaslandingpage", "thisi.saaslandingpage", "croissantsmoon",
    "saas.landingpage", "webuilder.gm",
    # Frontend Dev
    "_frontend_web_developer_", "frontend.web.developer",
    "frontend_web_developer_", "frontend_web_developer", "webticode",
    # UI UX Design
    "dashkaacom", "alena_mitrohina", "ui__ux.designer", "gautam.designn",
    "ui.debbie", "ui_portfolio", "ui.fawad", "uidiksign",
    "uidesignportfolio", "ux.ui_portfolio", "ux_portfolio", "sk_visual_",
    "portfolio_uxui", "ux_ui_portfolio", "jaypee_ux",
    # Web Design Inspiracao
    "ui.mob", "web.designinspiration", "webdesign.ox", "web.inspirations",
    # Design Studios and Agencies
    "web_design_agency", "web.design.agency", "webdesignagency",
    "web_design_agency_", "web.design_agency", "charm.digitalagency",
    "digital__agencyy", "mesondigital", "freshideas.digitalagency",
    # Figma e Ferramentas
    "figma._.designer", "figma_designer_", "figma_.designer", "figma_designer",
    # NoCode e Webflow
    "webdesigner_nocode", "umidjon_majiddev", "dana_webdesign",
    "mypageslab", "mgolinski_design",
    # Website Designers
    "websitedesigner_ng", "websitedesigners.la", "website_designer.india",
    "website.designer_", "mvmtsocials",
]

def follow(username):
    cmd = [
        "bash", "-c",
        f'source ~/.agent-reach-venv/Scripts/activate && '
        f'opencli instagram follow {username} '
        f'--window foreground --site-session ephemeral'
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if r.returncode == 0 and "Following" in r.stdout:
            return True, r.stdout.strip()
        return False, r.stderr.strip() or r.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "timeout"

print("🚀 Seguindo novos perfis no Instagram...")
print(f"   Conta: guilherme.crepaldi.dev\n")

seguidos = 0
falhas = 0
pausa = 5  # segundos entre follows pra evitar rate limit

for i, username in enumerate(NOVOS, 1):
    sys.stdout.write(f"  [{i:02d}/{len(NOVOS):02d}] @{username:30s} ... ")
    sys.stdout.flush()

    ok, msg = follow(username)
    if ok:
        seguidos += 1
        print("✅ Seguindo")
    else:
        falhas += 1
        print(f"❌ {msg[:50]}")

    # Pausa entre follows (rate limit)
    if i < len(NOVOS):
        time.sleep(pausa)

print(f"\n{'─' * 50}")
print(f"✅ Seguidos: {seguidos}")
print(f"❌ Falhas:   {falhas}")
print(f"📊 Total:    {len(NOVOS)} perfis")
