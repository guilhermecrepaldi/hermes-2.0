#!/usr/bin/env python3
"""
HERMES HOOKS — Lifecycle Hooks
Executados pela Queen Agent nos pontos de vida do sistema.

Hooks disponíveis:
  validate.py   → Antes de cada tarefa (validação)
  notify.py     → Depois de cada tarefa (notificação)
  check_perms.py → Antes de comandos críticos
  log_error.py  → Em caso de erro
  report.py     → Relatório final

Cada hook recebe um JSON com contexto via stdin ou argv.
"""

import sys
import json
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def hook_log(hook_name: str, context: dict, status: str = "ok"):
    """Log do hook."""
    logfile = os.path.join(LOG_DIR, f"hooks_{datetime.now().strftime('%Y%m%d')}.log")
    with open(logfile, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] [{hook_name}] [{status}] {json.dumps(context)[:200]}\n")


def run_hook(hook_name: str, default_context: dict = None):
    """Executa um hook específico."""
    context = default_context or {}
    
    # Se recebeu JSON via argv
    if len(sys.argv) > 1:
        try:
            context = json.loads(sys.argv[1])
        except:
            pass

    try:
        hook_log(hook_name, context, "started")
        # Aqui vai a lógica do hook
        # Por enquanto só loga
        hook_log(hook_name, context, "completed")
        return True
    except Exception as e:
        hook_log(hook_name, context, f"error: {e}")
        return False


if __name__ == "__main__":
    hook_name = os.path.splitext(os.path.basename(__file__))[0]
    run_hook(hook_name)
