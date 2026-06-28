"""Testes do Headroom Bridge — integracao com headroom.ai."""
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from headroom_bridge import compress_messages, compress_text, doctor, get_version, format_savings


def test_headroom_installed():
    """headroom deve estar instalado."""
    from headroom_bridge import HAS_HEADROOM
    assert HAS_HEADROOM, "headroom-ai precisa estar instalado: pip install headroom-ai"


def test_get_version():
    """get_version deve retornar string."""
    v = get_version()
    assert isinstance(v, str)
    assert len(v) > 0


def test_compress_messages():
    """compress_messages deve processar mensagens."""
    msgs = [
        {"role": "user", "content": "teste de compressao do contexto do Hermes Agent"},
        {"role": "assistant", "content": "resposta do assistente para compressao"},
    ]
    result = compress_messages(msgs)
    assert "messages" in result
    assert "tokens_before" in result
    assert "tokens_saved" in result


def test_compress_messages_empty():
    """compress_messages com lista vazia."""
    result = compress_messages([])
    assert "messages" in result


def test_compress_text():
    """compress_text deve comprimir string."""
    text = "analisar o codigo fonte do Hermes Agent para identificar padroes"
    compressed = compress_text(text)
    assert isinstance(compressed, str)
    assert len(compressed) > 0


def test_compress_text_with_context():
    """compress_text com contexto."""
    compressed = compress_text("faca um teste", context="voce e um assistente util")
    assert isinstance(compressed, str)


def test_format_savings():
    """format_savings deve formatar corretamente."""
    assert "0 tok" in format_savings(0)
    assert "K" in format_savings(5000)


def test_doctor():
    """doctor deve retornar status."""
    status = doctor()
    assert "installed" in status
    assert "version" in status


def test_doctor_check():
    """doctor deve testar compressao."""
    status = doctor()
    assert status["installed"] is True
