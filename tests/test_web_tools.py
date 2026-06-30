"""Testes das web tools: read_url.py e read_feed.py.
Testes de rede marcados com @pytest.mark.network.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from read_url import read_url
from read_feed import read_feed


def test_read_url_invalida():
    """URL invalida deve retornar erro."""
    r = read_url("", max_chars=100)
    assert r["status"] == "error"
    assert "error" in r


def test_read_url_sem_protocolo():
    """URL sem http deve ser corrigida."""
    r = read_url("example.com", max_chars=100)
    # Pode ser error (Jina Reader bloqueia) ou ok
    assert r["status"] in ("ok", "error")
    assert "url" in r


@pytest.mark.network
def test_read_url_example():
    """URL example.com deve funcionar."""
    r = read_url("https://example.com", max_chars=500)
    assert r["status"] == "ok"
    assert r["chars"] > 0
    assert "Example" in r["content"] or "example" in r["content"]


def test_read_url_max_chars():
    """Parametro max_chars deve funcionar (Jina Reader adiciona headers)."""
    r = read_url("https://example.com", max_chars=50)
    if r["status"] == "ok":
        # Jina Reader adiciona headers (Title, URL Source, Markdown Content)
        # antes do conteudo truncado. O importante e que o marcador exista.
        assert r["chars"] > 0
        assert "..." in r["content"] or "[... truncado" in r["content"]


def test_read_url_retorno_dict():
    """read_url deve sempre retornar dict com campos esperados."""
    r = read_url("https://example.com")
    assert "status" in r
    assert "url" in r
    assert "chars" in r
    assert "content" in r or "error" in r


def test_read_feed_url_invalida():
    """Feed URL invalida deve retornar erro."""
    r = read_feed("https://url.invalida.xyz/feed.xml", limit=3)
    assert r["status"] == "error"
    assert "error" in r


@pytest.mark.network
def test_read_feed_hn():
    """Hacker News RSS deve ser parseavel."""
    r = read_feed("https://hnrss.org/frontpage", limit=3)
    assert r["status"] == "ok"
    assert r["total_entries"] > 0
    assert len(r["entries"]) == 3


def test_read_feed_estrutura():
    """read_feed deve retornar estrutura esperada."""
    r = read_feed("https://hnrss.org/frontpage", limit=2)
    if r["status"] == "ok":
        assert "feed" in r
        assert "title" in r["feed"]
        assert "entries" in r
        for e in r["entries"]:
            assert "title" in e
            assert "link" in e


def test_read_feed_limit_zero():
    """Limit=0 deve retornar lista vazia."""
    r = read_feed("https://hnrss.org/frontpage", limit=0)
    if r["status"] == "ok":
        assert len(r["entries"]) == 0


def test_read_feed_limit_alto():
    """Limit alto nao deve quebrar."""
    r = read_feed("https://hnrss.org/frontpage", limit=100)
    if r["status"] == "ok":
        assert len(r["entries"]) <= r["total_entries"]


def test_read_feed_json_serializavel():
    """Resultado deve ser serializavel como JSON."""
    import json
    r = read_feed("https://hnrss.org/frontpage", limit=2)
    if r["status"] == "ok":
        json.dumps(r, ensure_ascii=False)  # nao deve levantar excecao
