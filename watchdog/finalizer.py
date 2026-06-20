#!/usr/bin/env python3
"""
Hermes Finalizer — Watchdog de pendencias.
Roda a cada ~2 min e fecha o que estiver pendente.
Chame apos qualquer task: python watchdog/finalizer.py
"""
from __future__ import annotations
import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def run(cmd: list, timeout: int = 30) -> dict:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           cwd=str(ROOT), timeout=timeout)
        return {"ok": r.returncode == 0, "out": r.stdout, "err": r.stderr}
    except Exception as e:
        return {"ok": False, "err": str(e)}


def check_pending() -> list:
    """Varre o projeto por pendencias e retorna lista do que fazer."""
    todo = []

    # 1. Testes falhando?
    r = run([sys.executable, "-m", "pytest", "tests/", "-q"])
    if not r["ok"]:
        todo.append({"type": "test", "detail": "Testes falhando", "fix": "pytest"})

    # 2. Arquivos nao commitados?
    r = run(["git", "status", "--short"])
    if r["ok"] and r["out"].strip():
        todo.append({"type": "git", "detail": "Arquivos nao commitados", "fix": "commit"})

    # 3. Remote atrasado?
    r = run(["git", "rev-list", "--count", "HEAD..origin/main"])
    if r["ok"] and r["out"].strip() and int(r["out"].strip()) > 0:
        todo.append({"type": "git", "detail": "Push pendente", "fix": "push"})

    # 4. TODO/FIXME/HACK no codigo? (ignora comentarios de estrutura)
    r = run(["grep", "-rn", "--include=*.py", "TODO\\|FIXME\\|HACK",
             "watchdog/", "tests/", "hermes_loop.py"])
    if r["ok"] and r["out"].strip():
        # Filtra: so considera se tem descricao acionavel (nao estrutura)
        lines = [l for l in r["out"].split("\\n") if l.strip() and "ignore" not in l.lower()]
        # Ignora linhas que sao apenas nomes de metodos ou comentarios de bloco
        real_todos = [l for l in lines if len(l) > 60]  # TODO verdadeiro tem contexto
        if real_todos:
            todo.append({"type": "code", "detail": f"TODOs: {real_todos[0][:60]}", "fix": "resolve"})

    # 5. CI falhou?
    r = run(["gh", "run", "list", "--limit", "1",
             "--json", "conclusion,status"])
    if r["ok"] and r["out"].strip():
        try:
            data = json.loads(r["out"])
            if data and data[0].get("conclusion") == "failure":
                todo.append({"type": "ci", "detail": "CI falhou", "fix": "fix_ci"})
        except (json.JSONDecodeError, IndexError):
            pass

    # 6. SPEC desatualizada?
    r = run(["grep", "-c", "## Estado Atual", "SPEC_ARQUITETURA_HERMES.md"])
    if r["ok"] and int(r["out"].strip()) == 0:
        todo.append({"type": "doc", "detail": "SPEC desatualizada", "fix": "update_spec"})

    return todo


def fix_pending(todo: list) -> list:
    """Tenta corrigir cada pendencia."""
    results = []
    for item in todo:
        logger.info(f"Fix: {item['fix']} -> {item['detail']}")
        if item["fix"] == "commit":
            run(["git", "add", "-A"])
            run(["git", "commit", "-m", "auto: finalizer commit"])
            r = run(["git", "push", "origin", "main"])
            results.append({"item": item, "fixed": r["ok"], "detail": r["out"][:80] if r["ok"] else r["err"][:80]})
        elif item["fix"] == "push":
            r = run(["git", "push", "origin", "main"])
            results.append({"item": item, "fixed": r["ok"], "detail": r["out"][:80] if r["ok"] else r["err"][:80]})
        elif item["fix"] == "pytest":
            r = run([sys.executable, "-m", "pytest", "tests/", "-q"])
            results.append({"item": item, "fixed": r["ok"], "detail": r["out"][:80] if r["ok"] else f"Ainda falha: {r['out'][:80]}"})
        else:
            results.append({"item": item, "fixed": False, "detail": "Auto-fix nao implementado para este tipo"})
    return results


def main() -> None:
    logger.info("=== Finalizer ===")
    todo = check_pending()
    if not todo:
        logger.info("Nada pendente. Clean.")
        print("\u2705 Clean — zero pendencias")
        return

    logger.warning(f"{len(todo)} pendencias encontradas")
    print(f"\u26a0️ {len(todo)} pendencias: {[t['type'] for t in todo]}")

    results = fix_pending(todo)
    fixed = [r for r in results if r["fixed"]]
    failed = [r for r in results if not r["fixed"]]

    if fixed:
        print(f"\u2705 Corrigidos: {len(fixed)}")
    if failed:
        print(f"\u274c Falhou: {len(failed)}")
        for f in failed:
            print(f"  - {f['item']['type']}: {f['detail'][:60]}")

    # Re-check se sobrou algo
    remaining = check_pending()
    if remaining:
        print(f"\u26a0️ Ainda pendente: {len(remaining)} — execute finalizer novamente")
    else:
        print("\u2705 Tudo resolvido apos finalizer")


if __name__ == "__main__":
    main()
