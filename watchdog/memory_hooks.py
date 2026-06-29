#!/usr/bin/env python3
"""Memory Hooks — Auto-persistencia inspirada no ECC (223K stars).
https://github.com/affaan-m/ecc

Salva automaticamente contexto importante na memoria apos:
- Comandos que criam/modificam arquivos
- Decisoes importantes de roteamento (S3)
- Erros e recuperacoes

Padrao ECC: memory-persistence hooks + agent-self-evaluation
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from logger_pro import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

MEMORY_DIR = Path.home() / ".hermes" / "memory_hooks"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def hook_pre_tool(tool_name: str, args: dict) -> dict:
    """Hook executado ANTES de um tool call (ECC PreToolUse pattern).
    
    Args:
        tool_name: Nome da ferramenta (terminal, write, etc)
        args: Argumentos da chamada
    
    Returns:
        Dict com possiveis modificacoes nos args
    """
    if tool_name in ("Write", "Patch", "Edit"):
        path = args.get("path", "")
        if path:
            logger.debug(f"Pre-hook: {tool_name} em {path}")
    
    return {"modified_args": args}


def hook_post_tool(tool_name: str, result: dict, context: dict) -> None:
    """Hook executado DEPOIS de um tool call (ECC PostToolUse pattern).
    
    Salva na memoria:
    - Arquivos criados/modificados
    - Decisoes de roteamento
    - Erros e recuperacoes
    """
    if not result.get("success", True):
        return  # So registra sucessos
    
    entry = {
        "timestamp": time.time(),
        "tool": tool_name,
        "context": context.get("summary", ""),
        "session": context.get("session_id", ""),
    }
    
    # Salva em arquivo rotativo (max 100 entries)
    filepath = MEMORY_DIR / "memory_hooks.jsonl"
    with open(filepath, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    # Rotacao: manter so as ultimas 100 entradas
    _rotate(filepath, 100)


def _rotate(filepath: Path, max_entries: int = 100):
    """Mantem apenas as N entradas mais recentes."""
    try:
        lines = filepath.read_text().strip().split("\n")
        if len(lines) > max_entries:
            filepath.write_text("\n".join(lines[-max_entries:]) + "\n")
    except (FileNotFoundError, ValueError):
        pass


def get_memory_feed(limit: int = 10) -> List[dict]:
    """Retorna as ultimas memorias salvas pelos hooks."""
    filepath = MEMORY_DIR / "memory_hooks.jsonl"
    if not filepath.exists():
        return []
    
    try:
        lines = filepath.read_text().strip().split("\n")
        entries = [json.loads(l) for l in lines[-limit:] if l.strip()]
        return entries
    except (json.JSONDecodeError, FileNotFoundError):
        return []


# Instancia global
hooks = {
    "pre_tool": hook_pre_tool,
    "post_tool": hook_post_tool,
}
