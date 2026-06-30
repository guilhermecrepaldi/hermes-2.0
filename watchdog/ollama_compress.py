#!/usr/bin/env python3
"""Ollama Compress — Compressor de contexto usando Ollama local (S1, $0).
Usa qwen2.5-coder:7b para comprimir tool outputs longos antes de enviar ao S3.

Zero Headroom. Zero proxy. Zero dependencias externas.
So Ollama + requests.

Uso:
    from ollama_compress import compress_messages
    result = compress_messages(messages)
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

# Verifica se Ollama esta respondendo
HAS_OLLAMA = False
OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

if HAS_REQUESTS:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
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

    Só comprime se o texto for > 2000 chars.
    Usa qwen2.5-coder:7b com temperatura 0.1 para consistencia.

    Args:
        messages: Lista de dicts com role/content

    Returns:
        Dict com mensagens comprimidas e metricas
    """
    if not HAS_OLLAMA or not HAS_REQUESTS:
        return {
            "messages": messages,
            "tokens_before": 0,
            "tokens_after": 0,
            "tokens_saved": 0,
            "compression_ratio": 0,
            "engine": "passthrough",
            "error": "Ollama indisponivel",
        }

    total_chars = sum(len(m.get("content", "")) for m in messages)
    if total_chars < 2000:  # Só comprime se for grande
        return {
            "messages": messages,
            "tokens_before": 0,
            "tokens_after": 0,
            "tokens_saved": 0,
            "compression_ratio": 0,
            "engine": "passthrough",
            "reason": "texto pequeno, sem compressao necessaria",
        }

    try:
        texto = messages[-1].get("content", "") if messages else ""
        if len(texto) < 2000:
            return {
                "messages": messages,
                "tokens_before": 0,
                "tokens_after": 0,
                "tokens_saved": 0,
                "compression_ratio": 0,
                "engine": "passthrough",
                "reason": "ultima mensagem pequena",
            }

        prompt = (
            "Resuma o texto abaixo mantendo APENAS informacoes essenciais: "
            "dados numericos, nomes proprios, conclusoes, decisoes, caminhos de arquivo. "
            "Seja CONCISO. Remova repeticao, filler, elogios.\n\n"
            f"{texto[:6000]}"
        )

        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 1024,
                    "temperature": 0.1,
                },
            },
            timeout=60,
        )

        if resp.status_code == 200:
            comp = resp.json().get("response", texto)
            tok_before = len(texto) // 4
            tok_after = len(comp) // 4
            messages[-1]["content"] = comp

            saved = max(0, tok_before - tok_after)
            ratio = saved / max(tok_before, 1)

            if HAS_TELEMETRY:
                telemetry.record(
                    user_input="auto-compress",
                    action_taken="ollama_compress",
                    shell_used="S1",
                    model_used=OLLAMA_MODEL,
                    provider="ollama",
                    total_tokens=tok_before,
                    tokens_input=tok_before,
                    tokens_output=tok_after,
                )

            return {
                "messages": messages,
                "tokens_before": tok_before,
                "tokens_after": tok_after,
                "tokens_saved": saved,
                "compression_ratio": ratio,
                "engine": "ollama",
            }
        else:
            logger.warning(f"Ollama compress retornou {resp.status_code}")
    except Exception as e:
        logger.debug(f"ollama compress fallback: {e}")

    return {
        "messages": messages,
        "tokens_before": 0,
        "tokens_after": 0,
        "tokens_saved": 0,
        "compression_ratio": 0,
        "engine": "passthrough",
        "error": str(e) if 'e' in dir() else "erro desconhecido",
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

def format_savings(tokens_saved: int, cost_per_m: float = 1.00) -> str:
    """Formata economia de tokens em texto legivel.

    Args:
        tokens_saved: Tokens economizados
        cost_per_m: Custo por 1M tokens (padrao: regua US$ 1.00)

    Returns:
        String formatada tipo "1.2K tok ($0.0012)"
    """
    if tokens_saved <= 0:
        return "0 tok"

    cost_saved = (tokens_saved * cost_per_m) / 1_000_000

    if tokens_saved >= 1000:
        return f"{tokens_saved/1000:.1f}K tok (${cost_saved:.4f})"
    return f"{tokens_saved} tok (${cost_saved:.6f})"


# ═══════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════

def doctor() -> dict:
    """Verifica se o compressor Ollama esta funcional."""
    status = {
        "ollama": HAS_OLLAMA,
        "model": OLLAMA_MODEL,
        "engine": "ollama",
        "compress_ok": False,
    }

    if HAS_OLLAMA and HAS_REQUESTS:
        try:
            test_msgs = [{"role": "user", "content": "teste " * 1000}]
            result = compress_messages(test_msgs)
            status["compress_ok"] = result.get("tokens_saved", 0) > 0
            status["economia"] = result.get("tokens_saved", 0)
            status["ratio"] = result.get("compression_ratio", 0)
        except Exception as e:
            status["error"] = str(e)

    return status


def main() -> int:
    """CLI: testa compressao."""
    import sys

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "teste " * 2000

    print(f"Comprimindo {len(text)} chars com {OLLAMA_MODEL}...")
    result = compress_messages([{"role": "user", "content": text}])
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nEconomia: {format_savings(result.get('tokens_saved', 0))}")

    return 0


if __name__ == "__main__":
    main()
