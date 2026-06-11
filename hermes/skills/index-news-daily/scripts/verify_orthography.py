#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_orthography.py — Auto-check orthographic rules for AI MARKDOWN NEWS HTML.

Usage:\n    python scripts/verify_orthography.py \"D:/projetos/TOP OF THE HOUR — IA/index.html\""

Checks the 11 rules from the "REVISÃO ORTOGRÁFICA" section:
  1. "agêntico/a" — never "agentic" in running text
  2. "multipasso" — no hyphen
  3. "multiplataforma" — no hyphen
  4. "Autogerado" — no hyphen
  5. Articles before companies: "a Apple", "a NVIDIA", "o Google", "a Microsoft"
  6. "responsável" — never "liable"
  7. "está disponível" — not "é disponível"
  8. "redescobrir" — never "redescoberir"
  9. Adjective before complement (manual check)
  10. Gender/number concordance
  11. Accepted anglicisms bypass list
"""

import re
import sys


def read_html(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    text_only = re.sub(r'<[^>]+>', ' ', content)
    text_only = re.sub(r'\s+', ' ', text_only)
    return content, text_only


def check_rule1(text, _html):
    issues = []
    for m in re.finditer(r'\bagentic\b', text, re.IGNORECASE):
        start = max(0, m.start() - 60)
        end = min(len(text), m.end() + 60)
        ctx = text[start:end]
        if re.search(r'(https?://|\.com/|href=|src=)', ctx):
            continue
        issues.append(f"  Rule 1: Use 'agêntico/a' instead of 'agentic':\n    ...{ctx.strip()}...")
    return issues


def check_rule2(text, _html):
    issues = []
    for m in re.finditer(r'multi-passo', text, re.IGNORECASE):
        start = max(0, m.start() - 30)
        end = min(len(text), m.end() + 30)
        issues.append(f"  Rule 2: Use 'multipasso' (no hyphen):\n    ...{text[start:end].strip()}...")
    return issues


def check_rule3(text, _html):
    issues = []
    for m in re.finditer(r'multi-plataforma', text, re.IGNORECASE):
        start = max(0, m.start() - 30)
        end = min(len(text), m.end() + 30)
        issues.append(f"  Rule 3: Use 'multiplataforma' (no hyphen):\n    ...{text[start:end].strip()}...")
    return issues


def check_rule4(text, _html):
    issues = []
    for m in re.finditer(r'auto-gerado', text, re.IGNORECASE):
        start = max(0, m.start() - 30)
        end = min(len(text), m.end() + 30)
        issues.append(f"  Rule 4: Use 'Autogerado' (no hyphen):\n    ...{text[start:end].strip()}...")
    return issues


def check_rule5(text, html):
    issues = []
    patterns = [
        (r'(?<!a )Apple(?=\s+(anunciou|lançou|revelou|disse|teria|teve|está|vai))',
         "Use 'a Apple' (com artigo definido)"),
        (r'(?<!a )NVIDIA(?=\s+(anunciou|lançou|revelou|disse|teria|teve|está|vai))',
         "Use 'a NVIDIA' (com artigo definido)"),
        (r'(?<!o )Google(?=\s+(anunciou|lançou|revelou|disse|teria|teve|está|vai))',
         "Use 'o Google' (com artigo definido)"),
        (r'(?<!a )Microsoft(?=\s+(anunciou|lançou|revelou|disse|teria|teve|está|vai))',
         "Use 'a Microsoft' (com artigo definido)"),
        (r'(?<!a )OpenAI(?=\s+(anunciou|lançou|revelou|disse|teria|teve|está|vai))',
         "Use 'a OpenAI' (com artigo definido)"),
    ]
    for pattern, msg in patterns:
        for m in re.finditer(pattern, html):
            start = max(0, m.start() - 40)
            end = min(len(html), m.end() + 40)
            ctx = html[start:end].strip()
            if re.search(r'["\'\(\)]', ctx[:min(10, len(ctx))]):
                continue
            issues.append(f"  Rule 5: {msg}:\n    ...{re.sub(r'<[^>]+>', '', ctx)}...")
    return issues


def check_rule6(text, _html):
    issues = []
    for m in re.finditer(r'\bliable\b', text, re.IGNORECASE):
        start = max(0, m.start() - 40)
        end = min(len(text), m.end() + 40)
        issues.append(f"  Rule 6: Use 'responsável' instead of 'liable':\n    ...{text[start:end].strip()}...")
    return issues


def check_rule7(text, _html):
    issues = []
    for m in re.finditer(r'é disponível', text, re.IGNORECASE):
        start = max(0, m.start() - 30)
        end = min(len(text), m.end() + 30)
        issues.append(f"  Rule 7: Use 'está disponível' not 'é disponível':\n    ...{text[start:end].strip()}...")
    return issues


def check_rule8(text, _html):
    issues = []
    for m in re.finditer(r'redescoberir', text, re.IGNORECASE):
        start = max(0, m.start() - 30)
        end = min(len(text), m.end() + 30)
        issues.append(f"  Rule 8: Use 'redescobrir' not 'redescoberir':\n    ...{text[start:end].strip()}...")
    return issues


def check_rule10(text, html):
    issues = []
    patterns = [
        (r'os ferramentas?\b', "'as ferramentas' (feminino)"),
        (r'a dados?\b(?=\s+foi)', "'os dados' (masculino) — 'dado' é masculino"),
    ]
    for pattern, msg in patterns:
        for m in re.finditer(pattern, html, re.IGNORECASE):
            start = max(0, m.start() - 30)
            end = min(len(text), m.end() + 30)
            ctx = html[start:end].strip()
            issues.append(f"  Rule 10 (possible): {msg}:\n    ...{re.sub(r'<[^>]+>', '', ctx)}...")
    return issues


def check_rule11(text, _html):
    issues = []
    for m in re.finditer(r'\bagents\b', text):
        start = max(0, m.start() - 40)
        end = min(len(text), m.end() + 40)
        ctx = text[start:end].strip()
        if not re.search(r'(href=|src=|\.com|api|openai|anthropic)', ctx, re.IGNORECASE):
            issues.append(f"  Rule 11: Use 'agentes' instead of 'agents':\n    ...{ctx}...")
    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_orthography.py <path/to/index.html>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        html, text = read_html(path)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        sys.exit(1)

    print(f"🔍 Checking orthography: {path}\n")

    checks = [
        ("1: agêntico/a (not 'agentic')", check_rule1),
        ("2: multipasso (no hyphen)", check_rule2),
        ("3: multiplataforma (no hyphen)", check_rule3),
        ("4: Autogerado (no hyphen)", check_rule4),
        ("5: Articles before companies", check_rule5),
        ("6: responsável (not 'liable')", check_rule6),
        ("7: está disponível", check_rule7),
        ("8: redescobrir", check_rule8),
        ("10: Gender/number concordance", check_rule10),
        ("11: Unexpected anglicisms (agents)", check_rule11),
    ]

    total = 0
    for label, fn in checks:
        issues = fn(text, html)
        if issues:
            print(f"❌ {label} — {len(issues)} issue(s)")
            for i in issues:
                print(i)
            total += len(issues)
        else:
            print(f"✅ {label} — OK")

    print(f"\n{'─' * 50}")
    if total == 0:
        print("✅ Nenhum problema ortográfico encontrado.")
    else:
        print(f"⚠️  {total} problema(s) ortográfico(s) encontrado(s).")
        print("   Corrija com patch antes de finalizar.")


if __name__ == '__main__':
    main()
