#!/usr/bin/env python3
"""Hermes Headroom — Integracao com headroom.ai (compressor de contexto).
headroom.ai: 60-95% menos tokens, mesmo resultado.
https://github.com/headroomlabs-ai/headroom

Integra com:
- compress(): comprime contexto antes de enviar ao LLM
- proxy: modo servidor para compressao em tempo real
- metricas: economia de tokens e custo
"""
from __future__ import annotations
import os
import json
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    from headroom import compress as headroom_compress
    from headroom import __version__ as HEADROOM_VERSION
    HAS_HEADROOM = True
except ImportError:
    HAS_HEADROOM = False
    HEADROOM_VERSION = "0.0.0"

try:
    from logger_pro import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from telemetry import telemetry, estimate_cost
    HAS_TELEMETRY = True
except ImportError:
    HAS_TELEMETRY = False


# ─── COMPRESSAO ──────────────────────────────────

def compress_messages(messages: List[dict]) -> dict:
    """Comprime mensagens usando headroom.ai.
    
    Args:
        messages: Lista de dicts com role/content
    
    Returns:
        Dict com mensagens comprimidas e metricas
    """
    if not HAS_HEADROOM:
        return {
            "messages": messages,
            "tokens_before": 0,
            "tokens_after": 0,
            "savings": 0,
            "error": "headroom nao instalado",
        }
    
    try:
        result = headroom_compress(messages)
        
        tokens_before = getattr(result, 'tokens_before', 0)
        tokens_after = getattr(result, 'tokens_after', 0)
        tokens_saved = getattr(result, 'tokens_saved', 0)
        ratio = getattr(result, 'compression_ratio', 0.0)
        
        return {
            "messages": getattr(result, 'messages', messages),
            "tokens_before": tokens_before,
            "tokens_after": tokens_after,
            "tokens_saved": tokens_saved,
            "compression_ratio": ratio,
            "transforms": getattr(result, 'transforms_applied', []),
        }
    except Exception as e:
        logger.warning(f"headroom compress falhou: {e}")
        return {
            "messages": messages,
            "tokens_before": 0,
            "tokens_after": 0,
            "savings": 0,
            "error": str(e),
        }


def compress_text(text: str, context: Optional[str] = None) -> str:
    """Comprime texto simples (converte para formato de mensagens)."""
    messages = [{"role": "user", "content": text}]
    if context:
        messages.insert(0, {"role": "system", "content": context})
    
    result = compress_messages(messages)
    compressed_msgs = result.get("messages", messages)
    
    if compressed_msgs and len(compressed_msgs) > 0:
        return compressed_msgs[-1].get("content", text)
    return text


# ─── METRICAS ────────────────────────────────────

def format_savings(tokens_saved: int, cost_per_m: float = 0.30) -> str:
    """Formata economia de tokens em texto legivel."""
    if tokens_saved <= 0:
        return "0 tok"
    
    cost_saved = (tokens_saved * cost_per_m) / 1_000_000
    
    if tokens_saved >= 1000:
        return f"{tokens_saved/1000:.1f}K tok (${cost_saved:.4f})"
    return f"{tokens_saved} tok (${cost_saved:.6f})"


def get_version() -> str:
    """Versao do headroom instalado."""
    return HEADROOM_VERSION


# ═══════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════

def doctor() -> dict:
    """Verifica se headroom esta funcional."""
    status = {
        "installed": HAS_HEADROOM,
        "version": HEADROOM_VERSION,
    }
    
    if HAS_HEADROOM:
        # Teste simples de compressao
        test_msgs = [{"role": "user", "content": "teste de compressao headroom"}]
        result = compress_messages(test_msgs)
        status["compress_ok"] = result.get("error") is None
        status["tokens_antes"] = result.get("tokens_before", 0)
        status["tokens_depois"] = result.get("tokens_after", 0)
    
    return status
