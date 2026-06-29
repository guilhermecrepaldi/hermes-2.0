#!/usr/bin/env python3
"""Agent Shield — Seguranca pre/post tool call (ECC AgentShield).
https://github.com/affaan-m/ecc

Verifica antes de executar ferramentas:
- Arquivos sensiveis (.env, config.yaml, chaves)
- Comandos destrutivos (rm -rf, format, drop)
- Exposicao de secrets em tool calls
- Operacoes de rede para hosts nao autorizados
"""
from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from logger_pro import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# ─── ARQUIVOS SENSIVEIS — NUNCA expor/modificar ───
SENSITIVE_FILES = [
    ".env", ".env.local", ".env.production",
    "config.yaml", "config.yml",
    "*.pem", "*.key", "*.cert",
    "credentials.json", "credentials.yml",
    "token*", "secret*", "key*",
    ".gitconfig", ".netrc", ".npmrc",
]

# ─── COMANDOS DESTRUTIVOS — bloquear se sem aprovacao ───
DESTRUCTIVE_PATTERNS = [
    r"rm\s+(-rf|--recursive|-r)\s+/",
    r"format\s+\w:",
    r"drop\s+(table|database|schema)",
    r"truncate\s+(table|database)",
    r"shutdown|poweroff|reboot",
    r"dd\s+if=.*of=",
    r">\s*/dev/(sda|sdb|sdc|nvme)",
]

# ─── HOSTS AUTORIZADOS (default: apenas local) ───
AUTHORIZED_HOSTS = [
    "localhost", "127.0.0.1",
    "api.deepseek.com",
    "api.openai.com",
    "api.anthropic.com",
    "api.github.com",
    "raw.githubusercontent.com",
    "registry.npmjs.org",
    "pypi.org", "files.pythonhosted.org",
    "ollama:11434", "localhost:11434",
]


def verify_pre_tool(tool_name: str, args: dict) -> dict:
    """Verifica seguranca ANTES de executar uma ferramenta.
    
    Returns:
        Dict com: allowed (bool), reason (str), modified_args (dict)
    """
    if tool_name == "Terminal":
        command = args.get("command", "")
        
        # Verificar comandos destrutivos
        for pattern in DESTRUCTIVE_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return {
                    "allowed": False,
                    "reason": f"COMANDO DESTRUTIVO BLOQUEADO: {pattern}",
                    "modified_args": args,
                }
        
        # Verificar acesso a hosts nao autorizados
        if "curl" in command or "wget" in command:
            for host in AUTHORIZED_HOSTS:
                if host in command:
                    break
            else:
                logger.warning(f"Host nao autorizado no comando: {command[:80]}")
    
    elif tool_name in ("Write", "Patch"):
        path = args.get("path", "")
        if path:
            # Verificar se e arquivo sensivel
            for pattern in SENSITIVE_FILES:
                if pattern.endswith("*"):
                    base = pattern[:-1]
                    if base in path:
                        return {
                            "allowed": False,
                            "reason": f"ARQUIVO SENSIVEL BLOQUEADO: {path}",
                            "modified_args": args,
                        }
                elif pattern in path:
                    return {
                        "allowed": False,
                        "reason": f"ARQUIVO SENSIVEL BLOQUEADO: {path}",
                        "modified_args": args,
                    }
    
    return {"allowed": True, "reason": "", "modified_args": args}


def verify_post_tool(tool_name: str, result: dict) -> dict:
    """Verifica seguranca DEPOIS de executar uma ferramenta.
    
    Verifica se o resultado nao expoe secrets ou dados sensiveis.
    """
    output = result.get("output", "") if isinstance(result, dict) else str(result)
    
    # Padroes de secrets
    secret_patterns = [
        r"(?i)(api[_-]?key|secret|token|password)\s*[=:]\s*['\"][^'\"]+['\"]",
        r"(?i)(api[_-]?key|secret|token|password)\s*[=:]\s*\S+",
        r"(?i)sk-[a-zA-Z0-9]{20,}",
        r"(?i)ghp_[a-zA-Z0-9]{36}",
        r"(?i)eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}",
    ]
    
    for pattern in secret_patterns:
        if re.search(pattern, output):
            logger.warning(f"SECRET DETECTADO no output de {tool_name}")
            return {"safe": False, "reason": "Secret detectado no output"}
    
    return {"safe": True, "reason": ""}


def doctor() -> dict:
    """Status do Agent Shield."""
    return {
        "destructive_patterns": len(DESTRUCTIVE_PATTERNS),
        "sensitive_files": len(SENSITIVE_FILES),
        "authorized_hosts": len(AUTHORIZED_HOSTS),
        "status": "active",
    }
