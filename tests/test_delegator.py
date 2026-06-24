"""Testes do Delegator Shellz: S3 (DeepSeek) + S1 (Ollama)."""
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from delegator import Delegator, DelegationDecision, tarefa_para_s1


def test_tarefa_main_vai_s3():
    """Task principal (funcao='main') vai para S3 (DeepSeek)."""
    d = Delegator()
    dec = d.delegar("criar API REST", funcao="main")
    assert dec.shell == "S3"
    assert dec.role == "main"
    assert dec.provider == "deepseek"


def test_tarefa_worker_vai_s1():
    """Task worker vai para S1 (Ollama)."""
    d = Delegator()
    dec = d.delegar("compilar projeto", funcao="worker")
    assert dec.shell == "S1"
    assert dec.role == "worker"
    assert dec.provider == "ollama"


def test_compilacao_detecta_s1():
    """'compilar' deve ser automaticamente detectado como S1."""
    d = Delegator()
    dec = d.delegar("compilar codigo fonte", funcao="main")
    assert dec.shell == "S1"


def test_ls_detecta_s1():
    """'ls' deve ir para S1."""
    d = Delegator()
    dec = d.delegar("listar diretorio com ls", funcao="main")
    assert dec.shell == "S1"


def test_loc_detecta_s1():
    """'loc' deve ir para S1."""
    d = Delegator()
    dec = d.delegar("contar loc do projeto", funcao="main")
    assert dec.shell == "S1"


def test_pytest_detecta_s1():
    """'pytest' deve ir para S1."""
    d = Delegator()
    dec = d.delegar("rodar pytest", funcao="main")
    assert dec.shell == "S1"


def test_git_detecta_s1():
    """'git status' deve ir para S1."""
    d = Delegator()
    dec = d.delegar("git status", funcao="main")
    assert dec.shell == "S1"


def test_tarefa_para_s1():
    """tarefa_para_s1() deve detectar keywords."""
    assert tarefa_para_s1("compilar projeto")
    assert tarefa_para_s1("rodar pytest")
    assert tarefa_para_s1("git diff")
    assert not tarefa_para_s1("criar uma API")
    assert not tarefa_para_s1("analisar dados")


def test_get_stats():
    """get_stats() deve ter estrutura Shellz."""
    d = Delegator()
    stats = d.get_stats()
    assert "sessoes_s3" in stats
    assert "delegacoes_s1" in stats
    assert "total_cost_s3" in stats
    assert "total_cost_s1" in stats


def test_stats_acumulam():
    """Estatisticas devem acumular multiplas delegacoes."""
    d = Delegator()
    d.delegar("criar API", funcao="main")
    d.delegar("compilar", funcao="main")
    d.delegar("git push", funcao="main")
    stats = d.get_stats()
    assert stats["sessoes_s3"] >= 1
    assert stats["delegacoes_s1"] >= 2


def test_reset_stats():
    """reset_stats() deve zerar."""
    d = Delegator()
    d.delegar("teste", funcao="main")
    d.reset_stats()
    assert d.get_stats()["sessoes_s3"] == 0


def test_custo_s1_zero():
    """S1 (Ollama) custa $0."""
    d = Delegator()
    dec = d.delegar("compilar", funcao="main", tokens=1000)
    assert dec.cost_per_1m == 0.0


def test_custo_s3_positivo():
    """S3 (DeepSeek) custa > $0."""
    d = Delegator()
    dec = d.delegar("criar API", funcao="main", tokens=1000)
    assert dec.cost_per_1m > 0.0


def test_decision_fields():
    """DelegationDecision deve ter todos os campos."""
    dec = DelegationDecision(
        shell="S3", role="main",
        model="deepseek-v4-flash", provider="deepseek",
        reason="teste",
    )
    d = dec.to_dict()
    assert d["shell"] == "S3"
    assert d["role"] == "main"
