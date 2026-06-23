#!/usr/bin/env python3
"""Hermes Logger Profissional — JSON estruturado + Data Masking
Implementacao inspirada em winston/pino para Python.
Uso: from logger_pro import get_logger, mask_data
      logger = get_logger(__name__)
      logger.info({"event": "startup", "userId": 42}, data={"password": "secret"})
"""
from __future__ import annotations
import logging
import json
import sys
import re
import traceback
from datetime import datetime, timezone
from typing import Optional, Dict, Any


# ─── DATA MASKING ────────────────────────────────────

SENSITIVE_FIELDS = {
    "password", "passwd", "senha",
    "token", "api_key", "apikey", "api-key",
    "secret", "secret_key", "secretkey",
    "authorization", "auth",
    "cpf", "cnpj", "rg", 
    "email", "telefone", "phone", "celular",
    "credit_card", "card_number", "cvv",
    "access_token", "refresh_token",
    "jwt", "session_id",
}

SENSITIVE_PATTERNS = [
    re.compile(r'[A-Za-z0-9+/=]{40,}'),       # tokens longos
    re.compile(r'[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]+'),  # JWT
    re.compile(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'),   # CPF
    re.compile(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b'),  # CNPJ
    re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),  # email
]


def mask_data(data: Any, depth: int = 0) -> Any:
    """Sanitiza dados recursivamente antes de logar.
    Mascara: senhas, tokens, CPF, email, etc.
    Mantem: userId, action, event, requestId, timestamps.
    """
    if depth > 10:  # Protecao contra recursao infinita
        return str(data)[:200]
    
    if isinstance(data, dict):
        return mask_dict(data)
    
    if isinstance(data, list):
        return [mask_data(v, depth+1) for v in data[:100]]  # Limita tamanho
    
    if isinstance(data, str):
        # 1. Verificar patterns sensiveis
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(data):
                return "***MASKED***"
        if len(data) > 500:
            return data[:200] + "..."
        return data
    
    return data


def mask_dict(data: dict) -> dict:
    """Mascara campos sensiveis em dicionarios recursivamente."""
    result = {}
    for k, v in data.items():
        if k.lower() in SENSITIVE_FIELDS:
            result[k] = "***MASKED***"
        elif isinstance(v, dict):
            result[k] = mask_dict(v)
        elif isinstance(v, list):
            result[k] = [mask_dict(item) if isinstance(item, dict) else mask_data(item) for item in v]
        elif isinstance(v, str):
            result[k] = mask_data(v)
        else:
            result[k] = v
    return result


# ─── JSON FORMATTER ───────────────────────────────────

class HermesJSONFormatter(logging.Formatter):
    """Log formatado em JSON com data masking automatico."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module or "",
            "function": record.funcName or "",
            "line": record.lineno or 0,
            "message": record.getMessage(),
        }
        
        # Context extra (se passado como dict no record)
        if hasattr(record, "context") and isinstance(record.context, dict):
            log_entry["context"] = mask_dict(record.context)
        
        # Stack trace
        if record.exc_info and record.exc_info[0]:
            log_entry["stack"] = traceback.format_exception(*record.exc_info)
            log_entry["error_type"] = record.exc_info[0].__name__
        
        return json.dumps(log_entry, ensure_ascii=False)


# ─── LOGGER FACTORY ────────────────────────────────────

_loggers: dict = {}
_LOG_LEVELS = {
    "fatal": logging.CRITICAL,
    "error": logging.ERROR,
    "warn": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


def get_logger(
    name: str,
    level: str = "info",
    json_output: bool = True,
) -> logging.Logger:
    """Factory de logger profissional.
    
    Args:
        name: __name__ do modulo
        level: fatal|error|warn|info|debug
        json_output: True para JSON, False para texto
        
    Returns:
        Logger configurado com data masking
    """
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    numeric_level = _LOG_LEVELS.get(level.lower(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Remove handlers existentes para evitar duplicacao
    logger.handlers.clear()
    
    handler = logging.StreamHandler(sys.stdout)
    
    if json_output:
        handler.setFormatter(HermesJSONFormatter())
    else:
        fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
    
    logger.addHandler(handler)
    logger.propagate = False
    
    # Adiciona metodo fatal
    if not hasattr(logger, "fatal"):
        logger.fatal = lambda msg, *a, **kw: logger.critical(msg, *a, **kw)
    
    # Adiciona helper para log contextual
    logger.context_log = lambda level_name, event, **ctx: _context_log(logger, level_name, event, **ctx)
    
    _loggers[name] = logger
    return logger


def _context_log(logger: logging.Logger, level: str, event: str, **context):
    """Log contextualizado com data masking automatico.
    
    Uso:
        logger.context_log("info", "user_login", userId=42, action="login")
        # {"timestamp": "...", "level": "INFO", "event": "user_login",
        #  "context": {"userId": 42, "action": "login"}}
    """
    safe_ctx = mask_dict(context)
    extra = {"context": safe_ctx}
    
    # Cria LogRecord com contexto
    import logging
    record = logger.makeRecord(
        logger.name, 
        _LOG_LEVELS.get(level.lower(), logging.INFO),
        "", 0, event, (), None
    )
    record.context = safe_ctx
    
    # Cria mensagem JSON
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "event": event,
        "context": safe_ctx,
    }
    
    handler = logger.handlers[0] if logger.handlers else None
    if handler and isinstance(handler.formatter, HermesJSONFormatter):
        handler.emit(record)
    else:
        # Fallback: escreve JSON diretamente
        print(json.dumps(log_entry, ensure_ascii=False), file=sys.stdout)


# ═══════════════════════════════════════════════════
# COMPATIBILIDADE: logging tradicional vira JSON
# ═══════════════════════════════════════════════════

def setup_hermes_logging(level: str = "info"):
    """Configura o logging global do Hermes para JSON.
    Substitui handlers existentes. Chame uma vez no startup.
    """
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(HermesJSONFormatter())
    root.addHandler(handler)
    root.setLevel(_LOG_LEVELS.get(level.lower(), logging.INFO))
    
    # Configura loggers dos modulos Hermes
    for name in ["hermes_loop", "core", "engine", "providers", "healer",
                  "orchestrator", "reflector", "code_analyzer"]:
        log = logging.getLogger(name)
        log.handlers.clear()
        log.addHandler(handler)
        log.setLevel(_LOG_LEVELS.get(level.lower(), logging.INFO))
        log.propagate = False
    
    # Logger de erro separado para stderr
    err_handler = logging.StreamHandler(sys.stderr)
    err_handler.setFormatter(HermesJSONFormatter())
    err_handler.setLevel(logging.ERROR)
    root.addHandler(err_handler)
