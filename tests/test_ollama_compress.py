"""Testes de compressao via Ollama (ollama_compress.py).
Cobre: compress_messages, compress_text, doctor, format_savings.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from ollama_compress import (
    compress_messages,
    compress_text,
    format_savings,
    doctor,
    HAS_OLLAMA,
)


def test_doctor_ollama():
    """Doctor deve detectar Ollama."""
    d = doctor()
    assert "ollama" in d
    assert "model" in d
    assert d["engine"] == "ollama"


def test_doctor_compress_ok():
    """Doctor deve conseguir comprimir texto de teste."""
    d = doctor()
    if HAS_OLLAMA:
        assert d["compress_ok"] is True
        assert d.get("economia", 0) > 0


def test_compress_pequeno_passthrough():
    """Texto pequeno (<2000 chars) nao deve ser comprimido."""
    msg = [{"role": "user", "content": "texto pequeno"}]
    result = compress_messages(msg)
    assert result["engine"] == "passthrough"
    assert result["tokens_saved"] == 0


def test_compress_vazio_mantem():
    """Lista vazia de mensagens nao quebra."""
    result = compress_messages([])
    assert result["engine"] == "passthrough"


def test_compress_sem_content():
    """Mensagem sem content nao quebra."""
    result = compress_messages([{"role": "user"}])
    assert result["engine"] == "passthrough"


def test_format_savings_zero():
    """format_savings(0) deve retornar '0 tok'."""
    assert format_savings(0) == "0 tok"


def test_format_savings_pequeno():
    """format_savings com valores pequenos."""
    s = format_savings(500)
    assert "500" in s
    assert "tok" in s


def test_format_savings_grande():
    """format_savings com valores grandes (K)."""
    s = format_savings(15000)
    assert "15.0K" in s
    assert "tok" in s


def test_format_savings_custom_rate():
    """format_savings com taxa personalizada."""
    s = format_savings(10000, cost_per_m=0.30)
    assert "10.0K" in s
    assert "$0.003" in s


def test_compress_text_small():
    """compress_text com texto pequeno retorna original."""
    texto = "texto curto"
    result = compress_text(texto)
    assert result == texto


def test_compress_text_large_ollama():
    """compress_text com texto grande usa Ollama."""
    texto = "teste de compressao " * 1500  # > 2000 chars
    result = compress_text(texto)
    if HAS_OLLAMA:
        # Ollama deve reduzir o texto
        assert len(result) < len(texto), f"Ollama nao reduziu: {len(result)} >= {len(texto)}"
    else:
        # Sem Ollama, retorna original
        assert result == texto
