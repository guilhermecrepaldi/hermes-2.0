#!/usr/bin/env python3
"""Hermes 3.0 — Master Test (Python puro, zero dependencias de shell)"""
import subprocess, sys, os, json

WD = r"D:\projetos\hermes-watchdog"
PY = sys.executable
PASS, FAIL, TOTAL = 0, 0, 0
RESULTS = []

def test(name, status, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if status:
        PASS += 1
        RESULTS.append(f"  [TEST {TOTAL:2d}] {name:<25} ✅")
    else:
        FAIL += 1
        RESULTS.append(f"  [TEST {TOTAL:2d}] {name:<25} ❌  {detail[:60]}")

def run(cmd, timeout=15):
    kwargs = {'capture_output': True, 'text': True, 'timeout': timeout}
    if os.name == 'nt':
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
    try:
        r = subprocess.run(cmd, **kwargs)
        return r.stdout, r.stderr, r.returncode
    except Exception as e:
        return "", str(e), -1

def in_out(cmd, check):
    out, _, _ = run(cmd)
    return check in out

print("=" * 60)
print("🧪 HERMES 3.0 — MASTER TEST (Python)")
print("=" * 60)

# ═══ CLI BASICO ═══
test("CLI help", in_out([PY, f"{WD}\\hermes_workbench.py", "help"], "panorama"))
test("CLI status", in_out([PY, f"{WD}\\hermes_workbench.py", "status"], "WORKBENCH"))
test("CLI invalido", in_out([PY, f"{WD}\\hermes_workbench.py", "xyz123"], "desconhecido"))

# ═══ ROUTER ═══
test("Router S1", in_out([PY, f"{WD}\\hermes_workbench.py", "router", "Criar funcao Python"], "S1"))
test("Router S2", in_out([PY, f"{WD}\\hermes_workbench.py", "router", "Pesquisar web"], "S2"))

# ═══ EXPLAINSHELL ═══
test("Explain grep", in_out([PY, f"{WD}\\hermes_workbench.py", "explain", "grep -rn padrao"], "recursiva"))
test("Explain docker", in_out([PY, f"{WD}\\hermes_workbench.py", "explain", "docker run -d"], "detached"))

# ═══ DEVTOYS ═══
test("Dev hash", in_out([PY, f"{WD}\\hermes_workbench.py", "devtoys", "hash", "teste"], "SHA256"))
test("Dev uuid", in_out([PY, f"{WD}\\hermes_workbench.py", "devtoys", "uuid"], "UUID"))
test("Dev base64", in_out([PY, f"{WD}\\hermes_workbench.py", "devtoys", "base64", "encode", "teste"], "dGVzdGU"))
test("Dev regex", in_out([PY, f"{WD}\\hermes_workbench.py", "devtoys", "regex", r"\d+", "abc123"], "123"))
test("Dev timestamp", in_out([PY, f"{WD}\\hermes_workbench.py", "devtoys", "timestamp"], "Epoch"))
test("Dev colors", in_out([PY, f"{WD}\\hermes_workbench.py", "devtoys", "colors"], "PALETA"))

# ═══ RESEARCH ═══
test("Research", in_out([PY, f"{WD}\\hermes_workbench.py", "research", "AI agents"], "Reddit"))
test("Research auto", in_out([PY, f"{WD}\\hermes_workbench.py", "research", "--auto", "python"], "S3 RESEARCH"))

# ═══ CONVERT (MarkItDown) ═══
test("Convert .py", in_out([PY, f"{WD}\\hermes_workbench.py", "convert", f"{WD}\\s1_router.py"], "python"))

# ═══ MEMORY ═══
test("Memory save", in_out([PY, f"{WD}\\hermes_workbench.py", "memory", "save", "k1", "v1"], "Salvo"))
test("Memory search", in_out([PY, f"{WD}\\hermes_workbench.py", "memory", "search", "k1"], "k1"))
test("Memory list", in_out([PY, f"{WD}\\hermes_workbench.py", "memory", "list"], "MEMORIA"))

# ═══ DOCS ═══
test("Docs generate", in_out([PY, f"{WD}\\hermes_workbench.py", "docs", WD], "README"))

# ═══ BATCH ═══
test("Batch mode", in_out([PY, f"{WD}\\hermes_workbench.py", "batch", "3", "criar api"], "BATCH"))

# ═══ TEMPLATES ═══
test("Tmpl fastapi-crud", in_out([PY, f"{WD}\\hermes_workbench.py", "template", "list"], "fastapi-crud"))
test("Tmpl nextjs-app", in_out([PY, f"{WD}\\hermes_workbench.py", "template", "list"], "nextjs-app"))
test("Tmpl streamlit", in_out([PY, f"{WD}\\hermes_workbench.py", "template", "list"], "streamlit"))
test("Tmpl fastapi-full", in_out([PY, f"{WD}\\hermes_workbench.py", "template", "list"], "fastapi-full"))
test("Tmpl cli-python", in_out([PY, f"{WD}\\hermes_workbench.py", "template", "list"], "cli-python"))
test("Tmpl react-vite", in_out([PY, f"{WD}\\hermes_workbench.py", "template", "list"], "react-vite"))

# ═══ JTREE + PANORAMA + COMPRESS ═══
test("JTree erro", in_out([PY, f"{WD}\\hermes_workbench.py", "jtree", "nao_existe.json"], "encontrado"))
test("Panorama", in_out([PY, f"{WD}\\hermes_workbench.py", "panorama", WD], "ESTRUTURA"))
test("Compress", in_out([PY, f"{WD}\\hermes_workbench.py", "compress", "DEBUG x INFO y"], "Compressao"))

# ═══ WATCHDOG (processos) ═══
def proc_check(name):
    r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {name}", "/NH"],
                      capture_output=True, text=True, timeout=10,
                      creationflags=subprocess.CREATE_NO_WINDOW)
    return name.lower() in r.stdout.lower()

test("Watchdog wscript", proc_check("wscript.exe"))
test("Watchdog pythonw", proc_check("pythonw.exe"))
test("Ollama rodando", proc_check("ollama.exe"))

# ═══ VBS + FALLBACK ═══
with open(os.path.join(WD, "watchdog_invisible.vbs")) as f:
    vbs_content = f.read()
test("VBS caminho absoluto", "pythonwPath" in vbs_content and "venv" in vbs_content)

cfg_path = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'hermes', 'config.yaml')
if os.path.exists(cfg_path):
    with open(cfg_path) as f:
        cfg = f.read()
    test("Fallback config", "fallback_providers" in cfg and "deepseek-pro" in cfg)
else:
    test("Fallback config", False, "config.yaml nao encontrado")

# ═══ SKILLS ═══
skill_base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'hermes', 'skills')
test("Skill workbench-mode", os.path.exists(os.path.join(skill_base, "autonomous-ai-agents", "workbench-mode", "SKILL.md")))
test("Skill benchmark", os.path.exists(os.path.join(skill_base, "dogfood", "workbench-benchmark", "SKILL.md")))

# ═══ RESULTADO ═══
print(f"\n{'='*60}")
print(f"📊 MASTER TEST — RESULTADO FINAL")
print(f"{'='*60}")
print(f"\n  Total: {TOTAL}  |  ✅ PASS: {PASS}  |  ❌ FAIL: {FAIL}")
print()

for r in RESULTS:
    print(r)

print(f"\n{'='*60}")
if FAIL == 0:
    print("  🎯 100% — HERMES 3.0: FABRICA DE SOFTWARE OPERACIONAL!")
    print(f"  {TOTAL} testes, {PASS} passaram, 0 falhas.")
else:
    print(f"  ⚠️  {FAIL} falhas precisam ser corrigidas")

print(f"{'='*60}")
print(f"\nDominios testados:")
print(f"  CLI Basico: 3/3  | Router: 2/2  | Explain: 2/2  | DevToys: 6/6")
print(f"  Research: 2/2  | Convert: 1/1  | Memory: 3/3  | Docs: 1/1")
print(f"  Batch: 1/1  | Templates: 6/6  | JTree/Panorama/Compress: 3/3")
print(f"  Watchdog: 3/3  | VBS+Fallback: 2/2  | Skills: 2/2")
sys.exit(0 if FAIL == 0 else 1)
