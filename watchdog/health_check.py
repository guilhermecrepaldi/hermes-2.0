#!/usr/bin/env python3
"""Verificação de saúde do ambiente Neo Hermes."""
import json, urllib.request, subprocess, sys, os
from datetime import datetime

def check_ollama():
    try:
        req = urllib.request.Request("http://localhost:11434/api/version", method="GET")
        resp = urllib.request.urlopen(req, timeout=3)
        v = json.loads(resp.read())
        return ("UP", v.get("version", "?"))
    except Exception as e:
        return ("DOWN", str(e))

def check_modelo():
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
        resp = urllib.request.urlopen(req, timeout=3)
        modelos = json.loads(resp.read())["models"]
        nomes = [m["name"] for m in modelos]
        if "qwen2.5-coder:7b" in nomes:
            return ("OK", "qwen2.5-coder:7b presente")
        return ("MISSING", f"Modelos: {', '.join(nomes[:3])}")
    except:
        return ("ERROR", "consulta falhou")

def check_opencli():
    try:
        r = subprocess.run(["opencli", "doctor"], capture_output=True, text=True, timeout=5)
        if "connected" in r.stdout.lower():
            return ("OK", "extension connected")
        return ("WARN", "instalado mas sem extensao")
    except:
        return ("DOWN", "nao instalado")

def check_repo():
    repo = os.path.expanduser("~/neo-hermes")
    if os.path.exists(os.path.join(repo, ".git")):
        r = subprocess.run(["git", "log", "--oneline", "-1"], cwd=repo, capture_output=True, text=True, timeout=3)
        return ("OK", r.stdout.strip()[:60])
    return ("MISSING", "repo nao encontrado")

# Executar checagens
checks = [
    ("Ollama", *check_ollama()),
    ("Modelo S1", *check_modelo()),
    ("OpenCLI", *check_opencli()),
    ("Repo", *check_repo()),
]

# Formatar saída
data = {"timestamp": datetime.now().isoformat(), "status": "OK", "checks": {}}
all_ok = True
for name, status, detail in checks:
    data["checks"][name] = {"status": status, "detail": detail}
    if status != "OK":
        all_ok = False

data["status"] = "OK" if all_ok else "ISSUES"

# Output único para o cron job ler
print(json.dumps(data, indent=2))
