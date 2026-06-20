"""Testes do roteamento economico com IA local."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "watchdog"))

from core import (
    ollama_disponivel, classificar_tarefa_local,
    LOCAL_MODEL, DEEPSEEK_FLASH, DEEPSEEK_PRO
)


def test_ollama_check():
    """Ollama deve estar disponivel (temos 14 modelos locais).
    Pula se nao estiver rodando (CI, ambiente limpo)."""
    import pytest
    disponivel = ollama_disponivel()
    if not disponivel:
        pytest.skip("Ollama nao esta rodando (pule em CI/ambiente limpo)")


def test_classificador_local_retorna_dict():
    """classificar_tarefa_local deve retornar um dict com shell, modelo, custo."""
    resultado = classificar_tarefa_local("criar uma funcao em python")
    assert isinstance(resultado, dict)
    assert "shell" in resultado
    assert "modelo" in resultado
    assert "custo" in resultado
    assert resultado["shell"] in ("S1", "S2", "S3")


def test_classificador_tarefa_simples_vai_local():
    """Tarefa simples de codigo deve ir para S1 (local, $0)."""
    resultado = classificar_tarefa_local("criar um site simples")
    assert resultado["shell"] == "S1", f"Esperado S1, obteve {resultado['shell']}"
    assert "0,00" in resultado["custo"]


def test_modelos_definidos():
    """Constantes de modelo devem estar definidas."""
    assert LOCAL_MODEL == "qwen2.5-coder:7b"
    assert DEEPSEEK_FLASH == "deepseek-v4-flash"
    assert DEEPSEEK_PRO == "deepseek-v4-pro"
