"""Hermes 2.0 — Monitor de processos (Windows).
Checagem de watchdog, Ollama, tray e shellz.

Uso: from monitor import proc_check, status_report
"""
from __future__ import annotations

import os
import subprocess


def proc_check(name: str) -> bool:
    """Verifica se um processo esta rodando via tasklist (Windows).

    Args:
        name: Nome do executavel (ex: 'ollama.exe', 'wscript.exe').

    Returns:
        True se o processo foi encontrado, False caso contrario.
    """
    kwargs = {"capture_output": True, "text": True, "timeout": 10}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    else:
        return False  # tasklist e Windows-only

    try:
        r = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {name}", "/NH"], **kwargs
        )
        return name.lower() in r.stdout.lower()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def status_report() -> dict:
    """Gera relatorio de status de todos os processos monitorados.

    Returns:
        Dict com nome do processo e status (bool).
    """
    targets = [
        ("ollama.exe", "S1 (Ollama)"),
        ("wscript.exe", "Watchdog Guardian"),
        ("pythonw.exe", "Watchdog (pythonw)"),
    ]
    return {label: proc_check(exe) for exe, label in targets}


def ensure_tools_exist(tools: list[tuple[str, str]]) -> list[tuple[str, str, bool]]:
    """Verifica se ferramentas do watchdog existem no diretorio.

    Args:
        tools: Lista de (nome_arquivo, descricao).

    Returns:
        Lista de (descricao, arquivo, existe).
    """
    wd = os.path.dirname(os.path.abspath(__file__))
    return [(desc, fname, os.path.exists(os.path.join(wd, fname))) for fname, desc in tools]
