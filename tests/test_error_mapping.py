"""Testes do Error Mapping (inspirado free-claude-code)."""
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from error_mapping import (
    map_error, format_error, HermesError, ERROR_CATALOG
)


def test_error_catalog_has_entries():
    """Catalogo de erros deve ter entradas."""
    assert len(ERROR_CATALOG) >= 10


def test_map_connection_refused():
    """connection refused deve mapear para CONNECTION_REFUSED."""
    e = map_error("Connection refused: couldn't connect to server")
    assert e.code == "CONNECTION_REFUSED"
    assert e.recoverable


def test_map_timeout():
    """timeout deve mapear para TIMEOUT."""
    e = map_error("timed out after 30 seconds")
    assert e.code == "TIMEOUT"


def test_map_auth_failed():
    """401 deve mapear para AUTH_FAILED."""
    e = map_error("HTTP 401: Unauthorized")
    assert e.code == "AUTH_FAILED"
    assert not e.recoverable


def test_map_rate_limited():
    """429 deve mapear para RATE_LIMITED."""
    e = map_error("429 Too Many Requests")
    assert e.code == "RATE_LIMITED"
    assert e.recoverable


def test_map_model_not_found():
    """model not found deve mapear para MODEL_NOT_FOUND."""
    e = map_error("Model 'xyz' not found")
    assert e.code == "MODEL_NOT_FOUND"


def test_map_context_too_long():
    """context too long deve mapear para CONTEXT_TOO_LONG."""
    e = map_error("This exceeds the maximum context length")
    assert e.code == "CONTEXT_TOO_LONG"


def test_map_ollama():
    """Ollama connect error deve mapear para OLLAMA_NOT_RUNNING."""
    e = map_error("Failed to connect to Ollama")
    assert e.code == "OLLAMA_NOT_RUNNING"


def test_map_unknown():
    """Erro desconhecido deve cair em UNKNOWN."""
    e = map_error("Some weird error that doesn't match anything")
    assert e.code == "UNKNOWN"


def test_map_with_provider():
    """Erro deve carregar nome do provider."""
    e = map_error("Connection refused", provider="ollama")
    assert e.provider == "ollama"
    assert "ollama" in str(e)


def test_format_error():
    """format_error deve produzir string legivel."""
    e = map_error("timeout", "deepseek")
    formatted = format_error(e)
    assert "TIMEOUT" in formatted
    assert "deepseek" in formatted
    assert "Suggestion" in formatted


def test_error_catalog_all_codes():
    """Todos os codigos do catalogo devem ser mapeaveis."""
    expected_codes = [
        "CONNECTION_REFUSED", "TIMEOUT", "DNS_FAILURE",
        "AUTH_FAILED", "RATE_LIMITED", "QUOTA_EXCEEDED",
        "MODEL_NOT_FOUND", "MODEL_OVERLOADED", "CONTEXT_TOO_LONG",
        "OLLAMA_NOT_RUNNING", "MODEL_NOT_PULLED",
        "INTERNAL_ERROR", "UNKNOWN",
    ]
    for code in expected_codes:
        assert code in [e.code for e in ERROR_CATALOG.values()], f"Missing code: {code}"
