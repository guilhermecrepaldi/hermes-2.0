"""Testes do Delegator — delegacao inteligente + telemetria."""
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from delegator import Delegator, DelegationDecision, estimate_complexity


def test_delegator_creates():
    """Delegator deve ser criado."""
    d = Delegator()
    assert d is not None


def test_estimate_simple():
    """Tarefas curtas devem ter baixa complexidade."""
    c = estimate_complexity("hello world")
    assert 1 <= c <= 5


def test_estimate_complex():
    """Tarefas longas com keywords complexas devem ter alta complexidade."""
    c = estimate_complexity(
        "analisar arquitetura do sistema e comparar com padroes de seguranca")
    assert c >= 5


def test_decide_simple():
    """Tarefa simples vai para S1_local."""
    d = Delegator()
    dec = d.decide("listar arquivos")
    assert dec.shell == "S1_local"
    assert dec.provider == "ollama"


def test_decide_complex():
    """Tarefa complexa vai para S2_cheap."""
    d = Delegator()
    dec = d.decide("analisar relatorio de vendas comparando trimestres")
    assert dec.shell == "S2_cheap"


def test_decide_muito_complexo():
    """Tarefa muito complexa vai para S3_premium."""
    d = Delegator()
    dec = d.decide(
        "analisar arquitetura de seguranca do sistema de autenticacao "
        "e comparar com padroes OWASP identificando vulnerabilidades "
        "em todos os endpoints da API")
    assert dec.shell == "S3_premium"


def test_delegar_registra():
    """delegar() deve retornar decision e contar na estatistica."""
    d = Delegator()
    dec = d.delegar("teste simples", funcao="test")
    assert dec.shell == "S1_local"
    assert d.get_stats()["total_delegations"] >= 1


def test_get_stats():
    """get_stats() deve ter estrutura correta."""
    d = Delegator()
    stats = d.get_stats()
    assert "total_delegations" in stats
    assert "by_shell" in stats
    assert "total_cost" in stats


def test_reset_stats():
    """reset_stats() deve zerar contadores."""
    d = Delegator()
    d.delegar("test", funcao="test")
    d.reset_stats()
    assert d.get_stats()["total_delegations"] == 0


def test_decision_fields():
    """DelegationDecision deve ter todos os campos."""
    dec = DelegationDecision(
        shell="S1_local",
        model="qwen2.5-coder:7b",
        provider="ollama",
        reason="teste",
        complexity=3,
    )
    assert dec.to_dict()["shell"] == "S1_local"
    assert dec.to_dict()["model"] == "qwen2.5-coder:7b"


def test_delegator_com_telemetria():
    """Delegator deve funcionar com telemetria."""
    d = Delegator()
    dec = d.delegar("listar diretorio", funcao="terminal", tokens_input=50, tokens_output=10)
    assert dec.cost_per_1m == 0.0  # Ollama = gratis
