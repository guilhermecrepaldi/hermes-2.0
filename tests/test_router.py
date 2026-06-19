"""Testes do Router S1/S2/S3."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "watchdog"))

from s1_router import classify_task


def test_router_s1_codigo():
    """Tarefa de codigo deve ir para S1."""
    result = classify_task("criar uma funcao em python")
    assert result["shell"] == "S1"


def test_router_s2_pesquisa():
    """Tarefa de pesquisa deve ir para S2."""
    result = classify_task("pesquisar sobre transformers")
    assert result["shell"] == "S2"


def test_router_s3_estrategia():
    """Tarefa de decisao deve ir para S3."""
    result = classify_task("decidir qual cloud usar")
    assert result["shell"] == "S3"


def test_router_nao_matcha_substring():
    """'cat' nao deve matchar 'catalogar' — o score S1 deve ser 0."""
    result = classify_task("catalogar produtos do estoque")
    assert result["score"]["S1"] == 0, f"'cat' contaminou score S1 (score={result['score']['S1']})"


def test_router_fallback_padrao_s1():
    """Quando nada matcha, fallback padrao e S1."""
    result = classify_task("catalogar produtos do estoque")
    assert result["shell"] == "S1"
    assert result["score"]["S1"] == 0
    assert result["score"]["S2"] == 0
    assert result["score"]["S3"] == 0
