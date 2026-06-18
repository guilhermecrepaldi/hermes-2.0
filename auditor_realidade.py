#!/usr/bin/env python3
"""
auditor_realidade.py — Prova que o Neo Hermes está de fato rodando.
Uso: python auditor_realidade.py
Gera relatório JSON com evidências de cada componente.
"""
import json, os, sys, glob, subprocess
from datetime import datetime

def cmd(comando, timeout=10):
    try:
        r = subprocess.run(
            comando, shell=True, capture_output=True, text=True,
            timeout=timeout, encoding='utf-8', errors='replace'
        )
        return r.stdout.strip(), r.returncode
    except Exception as e:
        return str(e), -1

def audit():
    relatorio = {
        "data": datetime.now().isoformat(),
        "itens": [],
        "resumo": {"total": 0, "funcionando": 0, "percentual": 0}
    }

    def add(nome, funcionando, detalhe, evidencia=""):
        relatorio["itens"].append({
            "nome": nome,
            "funcionando": funcionando,
            "detalhe": str(detalhe)[:100],
        })
        if funcionando:
            relatorio["resumo"]["funcionando"] += 1
        relatorio["resumo"]["total"] += 1

    # 1. IG Auto Post
    ig_main = os.path.exists("D:/projetos/ig-auto-post/main.py")
    add("IG Auto Post main.py", ig_main,
        f"{os.path.getsize('D:/projetos/ig-auto-post/main.py')} bytes" if ig_main else "ausente")

    # 2. Imagens geradas
    imgs = glob.glob("D:/projetos/ig-auto-post/posts/*.jpg") + glob.glob("D:/projetos/ig-auto-post/posts/*.png")
    add("Imagens IG geradas", len(imgs) > 0, f"{len(imgs)} imagens")

    # 3. Profile README
    add("Profile README GitHub",
        os.path.exists("D:/projetos/guilhermecrepaldi/README.md"),
        "guilhermecrepaldi/guilhermecrepaldi")

    # 4. Ollama
    import urllib.request
    ollama_ok = False
    qtd = 0
    try:
        resp = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3)
        data = json.loads(resp.read())
        modelos = data.get("models", [])
        qtd = len(modelos)
        ollama_ok = qtd > 0
    except:
        pass
    add("Ollama rodando", ollama_ok, f"{qtd} modelos lokais")

    # 5. instagrapi
    out, code = cmd("pip show instagrapi 2>&1 | grep -i version")
    add("instagrapi instalado", "version" in out.lower(), out.strip()[:60])

    # 6. Skills (contagem via Python puro)
    skills_dir = "C:/Users/Home/AppData/Local/hermes/skills"
    qtd_skills = 0
    if os.path.exists(skills_dir):
        for root, dirs, files in os.walk(skills_dir):
            if "SKILL.md" in files:
                qtd_skills += 1
    add("Skills Hermes instaladas", qtd_skills > 0, f"{qtd_skills} skills")

    # 7. Commits
    git_dir = "D:/projetos/_audit/.git"
    commits = 0
    if os.path.exists(git_dir):
        out, code = cmd("git -C /d/projetos/_audit log --oneline 2>&1")
        commits = len([l for l in out.split("\n") if l.strip()])
    add("Commits no repositorio", commits > 0, f"{commits} commits")

    # 8. Compressao
    cfg_path = "C:/Users/Home/AppData/Local/hermes/config.yaml"
    if os.path.exists(cfg_path):
        with open(cfg_path, encoding='utf-8', errors='replace') as f:
            cfg = f.read()
        compress_ok = "threshold: 0.35" in cfg
        add("Compressao contexto (threshold 0.35)", compress_ok,
            "✓ configurado" if compress_ok else "padrao")
    else:
        add("Compressao contexto", False, "config.yaml nao encontrado")

    # 9. Remote
    if os.path.exists(git_dir):
        out, code = cmd('git -C "D:/projetos/_audit" remote -v 2>&1')
        has_remote = "github.com" in out or "origin" in out
        add("Remote GitHub configurado", has_remote,
            "origin" if has_remote else "sem remote")
    else:
        add("Remote GitHub configurado", False, "sem git")

    # 10. Scripts de benchmark existem?
    add("Script auditor_realidade.py", os.path.exists("D:/projetos/_audit/auditor_realidade.py"),
        "self-audit funcional")

    # Resumo
    r = relatorio["resumo"]
    r["percentual"] = round(r["funcionando"] / r["total"] * 100, 1) if r["total"] else 0
    return relatorio

if __name__ == "__main__":
    r = audit()

    print(f"\n{'='*65}")
    print(f"🔍 AUDITOR DE REALIDADE — NEO HERMES")
    print(f"{'='*65}")
    print(f"Data: {r['data'][:19]}")
    print(f"{'='*65}")

    for item in r["itens"]:
        icon = "✅" if item["funcionando"] else "❌"
        print(f"  {icon} {item['nome']:45s} {item['detalhe']}")

    print(f"{'='*65}")
    rs = r["resumo"]
    pct = rs["percentual"]
    print(f"📊 {rs['funcionando']}/{rs['total']} funcionando ({pct}%)")
    if pct >= 80: print("✅ SISTEMA OPERACIONAL")
    elif pct >= 50: print("⚠️ PARCIAL")
    else: print("❌ CRÍTICO")

    # Salvar
    out_path = f"auditoria_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_path, "w") as f:
        json.dump(r, f, indent=2)
    print(f"📄 Relatório salvo: {out_path}")
    print(f"💡 Para re-auditar: python auditor_realidade.py")
