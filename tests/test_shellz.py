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
    """Task main sem keywords S1 vai para S3 (DeepSeek)."""
    d = Shellz()
    dec = d.rotear("qual o sentido da vida", funcao="main")
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
    dec = shellz.rotear("responda esta pergunta filosofica", tokens=1000)
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
    """analise de dados SEM FORCE_LOCAL nao vai para S1."""
    # Com FORCE_LOCAL=1 ativado no env, 'analisar' vai para S1
    # Teste apenas com funcao='worker' forcando comportamento
    from shellz import FORCE_LOCAL
    if not FORCE_LOCAL:
        dec = shellz.rotear("analisar dados de vendas", funcao="main")
        assert dec.shell == "S3"


def test_s1_nao_delega_arquitetura():
    """arquitetura SEM FORCE_LOCAL nao vai para S1."""
    from shellz import FORCE_LOCAL
    if not FORCE_LOCAL:
        dec = shellz.rotear("projetar arquitetura do sistema", funcao="main")
        assert dec.shell == "S3"


def test_force_local_env():
    """HERMES_FORCE_LOCAL_PROCESSING deve ser lido do env."""
    from shellz import FORCE_LOCAL
    assert isinstance(FORCE_LOCAL, bool)


def test_force_local_expande_keywords():
    """FORCE_LOCAL deve adicionar keywords extras."""
    from shellz import FORCE_LOCAL
    if FORCE_LOCAL:
        # 'analisar' agora vai para S1 com FORCE_LOCAL ativo
        dec = shellz.rotear("analisar dados de vendas", funcao="main")
        assert dec.shell == "S1", "FORCE_LOCAL=1: analisar deve ir para S1"
    else:
        assert True


def test_stats_sem_headroom():
    """get_stats NAO deve conter 'headroom'."""
    stats = shellz.get_stats()
    assert "headroom" not in stats, "headroom ainda nas stats!"
    assert "compressor" in stats


def test_stats_compressor_bool():
    """compressor deve ser bool."""
    stats = shellz.get_stats()
    assert isinstance(stats["compressor"], bool)


def test_rotear_com_tokens_calcula_custo():
    """Tokens passados devem gerar custo em S3."""
    dec = shellz.rotear("pergunta complexa sobre IA", tokens=10000)
    if dec.shell == "S3":
        assert dec.cost_per_1m > 0


def test_git_push_detecta_s1():
    """git push deve ir para S1."""
    dec = shellz.rotear("git push origin feature-branch")
    assert dec.shell == "S1"


def test_download_detecta_s1():
    """download/pip install deve ir para S1."""
    dec = shellz.rotear("pip install fastapi")
    assert dec.shell == "S1"


def test_arquitetura_vai_s3():
    """arquitetura do sistema deve ir para S3 (nao e S1)."""
    from shellz import FORCE_LOCAL
    if not FORCE_LOCAL:
        dec = shellz.rotear("projetar arquitetura do sistema")
        assert dec.shell == "S3"


def test_pesquisa_vai_s3():
    """pesquisa profunda deve ir para S3."""
    from shellz import FORCE_LOCAL
    if not FORCE_LOCAL:
        dec = shellz.rotear("faca uma analise comparativa entre frameworks")
        assert dec.shell == "S3"


def test_comprimir_contexto_sem_compressor():
    """comprimir_contexto sem compressor retorna original."""
    from shellz import HAS_COMPRESSOR
    if not HAS_COMPRESSOR:
        msgs = [{"role": "user", "content": "teste"}]
        result = shellz.comprimir_contexto(msgs)
        assert result["tokens_saved"] == 0
        assert result["messages"] == msgs


def test_rotear_obrigatorio_s1():
    """rotear_obrigatorio com task S1."""
    d = rotear_obrigatorio("rodar pytest", funcao="main")
    assert d.shell == "S1"


def test_rotear_obrigatorio_s3():
    """rotear_obrigatorio com task S3."""
    d = rotear_obrigatorio("explique teoria da relatividade")
    assert d.shell == "S3"


def test_decision_todos_campos():
    """ShellzDecision deve ter todos os campos."""
    d = shellz.rotear("teste")
    assert d.shell in ("S1", "S3")
    assert d.role in ("main", "worker")
    assert d.model
    assert d.provider
    assert isinstance(d.cost_per_1m, (int, float))
    assert d.reason
