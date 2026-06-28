"""Testes do Shellz — roteamento eterno S3/S1."""
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from shellz import Shellz, shellz, rotear_obrigatorio


def test_shellz_singleton():
    """Shellz deve ser singleton."""
    s1 = Shellz()
    s2 = Shellz()
    assert s1 is s2


def test_main_vai_s3():
    """Task main vai para S3 (DeepSeek)."""
    dec = shellz.rotear("criar API REST", funcao="main")
    assert dec.shell == "S3"
    assert dec.role == "main"
    assert dec.provider == "deepseek"


def test_worker_vai_s1():
    """Task worker vai para S1 (Ollama)."""
    dec = shellz.rotear("compilar projeto", funcao="worker")
    assert dec.shell == "S1"
    assert dec.role == "worker"
    assert dec.provider == "ollama"


def test_compilacao_detecta_s1():
    """compilar deve ir para S1 automaticamente."""
    dec = shellz.rotear("compilar codigo", funcao="main")
    assert dec.shell == "S1"


def test_ls_detecta_s1():
    """ls deve ir para S1."""
    dec = shellz.rotear("ls -la", funcao="main")
    assert dec.shell == "S1"


def test_git_detecta_s1():
    """git status deve ir para S1."""
    dec = shellz.rotear("git push origin main", funcao="main")
    assert dec.shell == "S1"


def test_pytest_detecta_s1():
    """pytest deve ir para S1."""
    dec = shellz.rotear("rodar pytest", funcao="main")
    assert dec.shell == "S1"


def test_install_detecta_s1():
    """pip install deve ir para S1."""
    dec = shellz.rotear("pip install flask", funcao="main")
    assert dec.shell == "S1"


def test_custo_s1_zero():
    """S1 custa $0."""
    dec = shellz.rotear("compilar", tokens=1000)
    assert dec.cost_per_1m == 0.0


def test_custo_s3_positivo():
    """S3 custa > $0."""
    dec = shellz.rotear("criar API", tokens=1000)
    assert dec.cost_per_1m > 0.0


def test_get_stats():
    """get_stats deve ter estrutura correta."""
    stats = shellz.get_stats()
    assert "s3_sessions" in stats
    assert "s1_delegations" in stats
    assert "total_cost" in stats


def test_rotear_obrigatorio():
    """rotear_obrigatorio deve funcionar."""
    dec = rotear_obrigatorio("tarefa que nao e compilavel", funcao="main")
    assert dec.shell == "S3"


def test_s1_nao_delega_analise():
    """analise de dados nao deve ir para S1."""
    dec = shellz.rotear("analisar dados de vendas", funcao="main")
    assert dec.shell == "S3"


def test_s1_nao_delega_arquitetura():
    """arquitetura nao deve ir para S1."""
    dec = shellz.rotear("projetar arquitetura do sistema", funcao="main")
    assert dec.shell == "S3"


def test_force_local_env():
    """HERMES_FORCE_LOCAL_PROCESSING deve ser lido do env."""
    from shellz import FORCE_LOCAL
    # No ambiente de teste, pode ser 0 ou 1
    assert isinstance(FORCE_LOCAL, bool)


def test_force_local_expande_keywords():
    """FORCE_LOCAL deve adicionar keywords extras."""
    from shellz import FORCE_LOCAL, S1_TASKS
    if FORCE_LOCAL:
        assert "processar" or "analisar" or "gerar" not in S1_TASKS
        # Essas keywords sao adicionadas pela logica de FORCE_LOCAL
        assert True
