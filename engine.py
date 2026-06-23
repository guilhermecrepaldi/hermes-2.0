#!/usr/bin/env python3
"""Hermes Agent Engine — Context, Subagents, Checkpoints, Hooks, Cache.

Motor de servicos do Hermes 2.0: tudo que nao e loop puro nem harness.
"""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# Logger setup
try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════
# CONTEXT ENGINEERING — hermes-progress.md
# ═══════════════════════════════════════════════

PROGRESS_FILE = ROOT / "hermes-progress.md"


def carregar_progresso() -> dict:
    """Carrega estado da sessao do hermes-progress.md."""
    if not PROGRESS_FILE.exists():
        return {"feito": [], "pendente": [], "artefatos": [],
                "ultima_sessao": ""}
    try:
        texto = PROGRESS_FILE.read_text(encoding="utf-8")
        estado = {"feito": [], "pendente": [],
                  "artefatos": [], "ultima_sessao": texto[:200]}
        for line in texto.split("\n"):
            l = line.strip()
            if l.startswith("- [x]") or l.startswith("- [X]"):
                estado["feito"].append(l[5:].strip())
            elif l.startswith("- [ ]"):
                estado["pendente"].append(l[5:].strip())
            elif l.startswith("  -"):
                estado["artefatos"].append(l.strip())
        return estado
    except Exception:
        return {"feito": [], "pendente": [],
                "artefatos": [], "ultima_sessao": ""}


def salvar_progresso(acao: str, resultado: str) -> None:
    """Registra progresso no hermes-progress.md."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- {ts}: {acao} -> {resultado[:80]}"
    try:
        if PROGRESS_FILE.exists():
            texto = PROGRESS_FILE.read_text(encoding="utf-8")
        else:
            texto = "# Hermes Progress\n\n"
        texto += f"\n{entry}"
        PROGRESS_FILE.write_text(texto, encoding="utf-8")
    except Exception:
        pass


# ═══════════════════════════════════════════════
# SUBAGENT SPAWNING — git worktrees
# ═══════════════════════════════════════════════

def criar_worktree(nome: str) -> dict:
    """Cria subagent isolado via git worktree."""
    path = ROOT / f"../subagents/{nome}"
    branch = f"agent/{nome}"
    try:
        r = subprocess.run(["git", "worktree", "list"],
                           capture_output=True, text=True,
                           cwd=str(ROOT), timeout=10)
        if nome in r.stdout:
            return {"status": "existente", "path": str(path)}

        subprocess.run(["git", "branch", "-f", branch, "main"],
                       capture_output=True, cwd=str(ROOT), timeout=10)
        r = subprocess.run(["git", "worktree", "add", str(path), branch],
                           capture_output=True, text=True,
                           cwd=str(ROOT), timeout=15)
        if r.returncode == 0:
            return {"status": "criado", "path": str(path), "branch": branch}
        return {"status": "erro", "erro": r.stderr[:200]}
    except Exception as e:
        return {"status": "erro", "erro": str(e)}


def remover_worktree(nome: str) -> dict:
    """Remove subagent (worktree)."""
    path = ROOT / f"../subagents/{nome}"
    branch = f"agent/{nome}"
    try:
        subprocess.run(["git", "worktree", "remove", str(path)],
                       capture_output=True, cwd=str(ROOT), timeout=10)
        subprocess.run(["git", "branch", "-D", branch],
                       capture_output=True, cwd=str(ROOT), timeout=5)
        return {"status": "removido"}
    except Exception as e:
        return {"status": "erro", "erro": str(e)}


# ═══════════════════════════════════════════════
# INITIALIZER + CODING AGENT PATTERN
# ═══════════════════════════════════════════════

class InitializerAgent:
    """Setup e planejamento."""

    @staticmethod
    def setup(descricao: str) -> dict:
        logger.info(f"Initializer: {descricao[:60]}...")
        salvar_progresso("INIT", descricao)
        return {
            "status": "setup_ok",
            "context": {
                "descricao": descricao,
                "rules": [
                    "Usar taste-skill: 10 regras",
                    "Sem paths hardcoded",
                    "Nao quebrar funcional",
                    "Commit a cada passo"
                ]
            }
        }


class CodingAgent:
    """Execucao incremental."""

    @staticmethod
    def plan_and_execute(setup: dict) -> list:
        logger.info("CodingAgent: plan_and_execute")
        carregar_progresso()
        plan = [
            f"1. {setup['context']['descricao'][:50]}",
            "2. Implementar com type hints",
            "3. Escrever testes pytest",
            "4. Verificar quality gate (taste-skill)",
            "5. Commit"
        ]
        salvar_progresso("PLAN", "; ".join(plan))
        return plan


# ═══════════════════════════════════════════════
# CHECKPOINTING + AUTO-COMPACTION
# ═══════════════════════════════════════════════

class CheckpointManager:
    """Gere checkpoints de estado."""

    DIR = ROOT / ".hermes" / "checkpoints"

    @classmethod
    def save(cls, nome: str = "auto") -> dict:
        cls.DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = cls.DIR / f"{nome}_{ts}.json"
        estado = {
            "nome": nome,
            "timestamp": ts,
            "progresso": carregar_progresso(),
        }
        try:
            r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                               capture_output=True, text=True,
                               cwd=str(ROOT), timeout=5)
            estado["git_hash"] = r.stdout.strip()
        except Exception:
            estado["git_hash"] = "unknown"
        path.write_text(json.dumps(estado, indent=2), encoding="utf-8")
        logger.info(f"Checkpoint salvo: {path.name}")
        salvar_progresso("CHECKPOINT", path.name)
        return {"status": "ok", "path": str(path), "hash": estado["git_hash"]}

    @classmethod
    def list(cls) -> list:
        if not cls.DIR.exists():
            return []
        return sorted([p.name for p in cls.DIR.glob("*.json")], reverse=True)

    @classmethod
    def auto_compact(cls, max_cp: int = 10) -> dict:
        cps = cls.list()
        if len(cps) <= max_cp:
            return {"removidos": 0, "mantidos": len(cps)}
        for nome in cps[max_cp:]:
            (cls.DIR / nome).unlink(missing_ok=True)
        logger.info(f"Auto-compact: removidos {len(cps) - max_cp}, mantidos {max_cp}")
        return {"removidos": len(cps) - max_cp, "mantidos": max_cp}


# ═══════════════════════════════════════════════
# HOOKS EXECUTION
# ═══════════════════════════════════════════════

class HookManager:
    """Gere hooks pre/post para ferramentas."""

    _hooks: Dict[str, Dict[str, list]] = {"pre": {}, "post": {}}

    @classmethod
    def register(cls, hook_type: str, tool: str, fn) -> None:
        if tool not in cls._hooks[hook_type]:
            cls._hooks[hook_type][tool] = []
        cls._hooks[hook_type][tool].append(fn)
        logger.debug(f"Hook {hook_type}/{tool} registrado")

    @classmethod
    def execute(cls, hook_type: str, tool: str,
                ctx: dict) -> dict:
        hooks = cls._hooks.get(hook_type, {}).get(tool, [])
        results = []
        for fn in hooks:
            try:
                results.append(fn(ctx))
            except Exception as e:
                logger.error(f"Hook {hook_type}/{tool}: {e}")
                results.append({"error": str(e)})
        return {"executed": len(results), "results": results}

    @classmethod
    def setup_default(cls) -> None:
        def pre_patch(ctx):
            p = ctx.get("path", "")
            if p and not os.path.exists(p):
                return {"warning": f"Arquivo nao existe: {p}"}
            return {"status": "ok"}
        def post_terminal(ctx):
            ec = ctx.get("exit_code", -1)
            if ec != 0:
                return {"warning": f"Exit code {ec}"}
            return {"status": "ok"}
        cls.register("pre", "patch", pre_patch)
        cls.register("post", "terminal", post_terminal)
        logger.info("Default hooks configurados")


# ═══════════════════════════════════════════════
# KV CACHE
# ═══════════════════════════════════════════════

class KVCache:
    """Cache compartilhado entre sub-agents."""

    _cache: Dict[str, dict] = {}
    _max_size = 100

    @classmethod
    def get(cls, key: str) -> Any:
        entry = cls._cache.get(key)
        if entry and entry.get("expires", 0) > datetime.now().timestamp():
            return entry["value"]
        return None

    @classmethod
    def set(cls, key: str, value: Any, ttl: int = 300) -> None:
        cls._cache[key] = {
            "value": value,
            "expires": datetime.now().timestamp() + ttl
        }
        if len(cls._cache) > cls._max_size:
            cls._compact()

    @classmethod
    def _compact(cls) -> None:
        now = datetime.now().timestamp()
        expired = [k for k, v in cls._cache.items()
                   if v.get("expires", 0) < now]
        for k in expired:
            del cls._cache[k]
        if len(cls._cache) > cls._max_size:
            items = sorted(cls._cache.items(),
                           key=lambda x: x[1].get("expires", 0),
                           reverse=True)
            cls._cache = dict(items[:cls._max_size])


# ═══════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════

__all__ = [
    "carregar_progresso", "salvar_progresso",
    "criar_worktree", "remover_worktree",
    "InitializerAgent", "CodingAgent",
    "CheckpointManager", "HookManager", "KVCache",
]
