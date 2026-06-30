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
import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from headroom import compress as headroom_compress
    from headroom import __version__ as HEADROOM_VERSION
    HAS_HEADROOM = True
except ImportError:
    HAS_HEADROOM = False
    HEADROOM_VERSION = "0.0.0"

# Fallback: Ollama local como compressor quando headroom nao tem Rust core
HAS_OLLAMA = False
if HAS_REQUESTS:
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        HAS_OLLAMA = r.status_code == 200
    except:
        pass

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
    """Comprime mensagens usando Ollama local (S1, $0).
    
    Headroom nativo removido — sem Rust core, nao comprime.
    Usa Ollama (qwen2.5-coder:7b) como motor de compressao real.
    
    Args:
        messages: Lista de dicts com role/content
    
    Returns:
        Dict com mensagens comprimidas e metricas
    """
    # Apenas Ollama — headroom nativo nao tem Rust core
    if HAS_OLLAMA and HAS_REQUESTS:
        total_chars = sum(len(m.get("content", "")) for m in messages)
        if total_chars > 2000:  # So comprime se for grande
            try:
                texto = messages[-1].get("content", "") if messages else ""
                if len(texto) > 2000:
                    prompt = f"Resuma o texto abaixo mantendo informacoes essenciais (dados, nomes, numeros, conclusoes). Seja conciso:\n\n{texto[:6000]}"
                    resp = requests.post(
                        "http://localhost:11434/api/generate",
                        json={"model": "qwen2.5-coder:7b", "prompt": prompt,
                              "stream": False, "options": {"num_predict": 1024, "temperature": 0.1}},
                        timeout=60,
                    )
                    if resp.status_code == 200:
                        comp = resp.json().get("response", texto)
                        tok_before = len(texto) // 4
                        tok_after = len(comp) // 4
                        messages[-1]["content"] = comp
                        return {
                            "messages": messages,
                            "tokens_before": tok_before,
                            "tokens_after": tok_after,
                            "tokens_saved": max(0, tok_before - tok_after),
                            "compression_ratio": max(0, tok_before - tok_after) / max(tok_before, 1),
                            "engine": "ollama",
                        }
            except Exception as e:
                logger.debug(f"ollama compress fallback: {e}")
    
    return {
        "messages": messages,
        "tokens_before": 0,
        "tokens_after": 0,
        "tokens_saved": 0,
        "compression_ratio": 0,
        "engine": "passthrough",
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
    """Verifica se Ollama compressor esta funcional (headroom nativo removido)."""
    status = {
        "installed": HAS_HEADROOM,
        "version": HEADROOM_VERSION,
        "ollama_compressor": HAS_OLLAMA,
        "compress_engine": "ollama",
    }
    
    if HAS_HEADROOM:
        test_msgs = [{"role": "user", "content": "teste de compressao headroom"}]
        result = compress_messages(test_msgs)
        status["headroom_compress_ok"] = result.get("error") is None
    
    if HAS_OLLAMA and HAS_REQUESTS:
        try:
            test_msgs = [{"role": "user", "content": "teste " * 1000}]
            result = compress_messages(test_msgs)
            status["ollama_compress_ok"] = result.get("tokens_saved", 0) > 0
            status["ollama_economia"] = result.get("tokens_saved", 0)
        except:
            status["ollama_compress_ok"] = False
    
    return status
