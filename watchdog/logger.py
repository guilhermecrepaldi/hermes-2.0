"""Hermes 2.0 — Logging estruturado.
Uso: from logger import get_logger; log = get_logger(__name__)

Ative HERMES_DEBUG=1 no ambiente para verbose.
"""
from __future__ import annotations
import logging
import os
import sys
from pathlib import Path


def setup_logger(
    name: str = "hermes",
    level: int | None = None,
    log_file: str | Path | None = None,
) -> logging.Logger:
    """Configura e retorna um logger.

    Args:
        name: Nome do logger.
        level: Nivel de log (default: DEBUG se HERMES_DEBUG=1, senao INFO).
        log_file: Caminho opcional para arquivo de log.

    Returns:
        logging.Logger configurado.
    """
    if level is None:
        level = logging.DEBUG if os.environ.get("HERMES_DEBUG") else logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Handler stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    # Handler arquivo (opcional)
    if log_file:
        fh = logging.FileHandler(str(log_file), encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger


def get_logger(name: str = "hermes") -> logging.Logger:
    """Retorna logger existente ou cria um novo."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
