"""Testes da Telemetria Obrigatoria."""
from pathlib import Path
import sys, json, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from telemetry import Telemetry, telemetry, TELEMETRY_FILE, TELEMETRY_DIR


def test_telemetry_singleton():
    """Telemetry deve ser singleton."""
    t1 = Telemetry()
    t2 = Telemetry()
    assert t1 is t2


def test_telemetry_record():
    """record() deve salvar entrada."""
    t = Telemetry()
    t.record(user_input="test input", action_taken="test_action")
    assert t._entry_count >= 1


def test_telemetry_file_exists():
    """Arquivo de telemetria deve existir apos primeiro record."""
    t = Telemetry()
    t.record(user_input="file test", action_taken="check")
    assert TELEMETRY_FILE.exists()


def test_telemetry_file_content():
    """Conteudo do arquivo deve ser JSON valido."""
    t = Telemetry()
    t.record(user_input="json test", action_taken="verify")
    assert TELEMETRY_FILE.exists()
    with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
        lines = [l for l in f if l.strip()]
    if lines:
        last = json.loads(lines[-1])
        assert "user_input" in last
        assert "timestamp" in last
        assert "session_id" in last


def test_telemetry_get_stats():
    """get_stats() deve retornar dict com campos essenciais."""
    t = Telemetry()
    t.record(user_input="stats test", action_taken="check")
    stats = t.get_stats()
    assert "session_id" in stats
    assert "entries" in stats
    assert "file" in stats


def test_telemetry_get_session_entries():
    """get_session_entries() deve retornar entradas da sessao."""
    t = Telemetry()
    entries = t.get_session_entries()
    # Pega a ultima entrada (a mais recente)
    last_input = entries[-1]["user_input"]
    assert len(entries) >= 1
    assert "test" in last_input


def test_telemetry_get_all_entries():
    """get_all_entries() deve retornar entradas."""
    t = Telemetry()
    entries = t.get_all_entries(limit=100)
    assert isinstance(entries, list)


def test_telemetry_fields():
    """Todos os campos obrigatorios devem ser registrados."""
    t = Telemetry()
    t.record(
        user_input="full test",
        action_taken="full_action",
        tools_used=["terminal", "file"],
        result_summary="success",
        duration_ms=150.0,
        success=True,
        model_used="gpt-4",
        provider="openai",
        tokens_input=200,
        tokens_output=300,
        total_tokens=500,
        cost=0.01,
        shell_used="S2_cheap",
        api_endpoint="https://api.openai.com/v1/chat",
        model_selected_by_shell="gpt-4-mini",
        complexity=5,
    )
    entries = t.get_session_entries()
    last = entries[-1]
    assert last["user_input"] == "full test"
    assert last["action_taken"] == "full_action"
    assert last["tools_used"] == ["terminal", "file"]
    assert last["success"] is True
    assert last["model_used"] == "gpt-4"
    assert last["provider"] == "openai"
    assert last["tokens_input"] == 200
    assert last["tokens_output"] == 300
    assert last["total_tokens"] == 500
    assert last["cost"] == 0.01
    assert last["shell_used"] == "S2_cheap"
    assert last["api_endpoint"] == "https://api.openai.com/v1/chat"
    assert last["model_selected_by_shell"] == "gpt-4-mini"
    assert last["complexity"] == 5


def test_telemetry_summary():
    """summary() deve produzir texto."""
    t = Telemetry()
    t.record(user_input="summary test", action_taken="check")
    s = t.summary()
    assert "Hermes Telemetry" in s
    assert "Session:" in s
    assert "Entries:" in s


def test_telemetry_never_fails():
    """Telemetria NUNCA pode lancar excecao."""
    t = Telemetry()
    try:
        t.record(user_input="fail test", action_taken="verify")
        assert True
    except Exception:
        assert False, "Telemetria nunca deve falhar"


def test_record_interaction():
    """record_interaction deve funcionar."""
    from telemetry import record_interaction
    try:
        record_interaction(user_input="convenience test", action_taken="check")
        assert True
    except Exception as e:
        assert False, f"record_interaction falhou: {e}"


def test_mini_report_produces_text():
    """mini_report() deve produzir texto com breakdown."""
    from telemetry import telemetry
    report = telemetry.mini_report()
    assert "telemetria" in report


def test_estimate_cost_deepseek():
    """estimate_cost deve calcular DeepSeek corretamente."""
    from telemetry import estimate_cost
    # 200 tokens input ($0.14/M) + 300 output ($0.42/M)
    cost = estimate_cost("deepseek", 200, 300)
    expected = (200 * 0.14 + 300 * 0.42) / 1_000_000
    assert abs(cost - expected) < 0.000001


def test_estimate_cost_zero_local():
    """estimate_cost para local deve ser 0."""
    from telemetry import estimate_cost
    cost = estimate_cost("ollama", 5000, 1000)
    assert cost == 0.0


def test_estimate_cost_unknown_provider():
    """estimate_cost para provider desconhecido usa fallback."""
    from telemetry import estimate_cost
    cost = estimate_cost("desconhecido", 1000, 500)
    assert cost > 0  # Fallback rate deve > 0


def test_get_tier_local():
    """get_tier para S1_local deve retornar 'local'."""
    from telemetry import get_tier
    assert get_tier("S1_local") == "local"
    assert get_tier("S1") == "local"


def test_get_tier_cloud():
    """get_tier para S2_cheap deve retornar 'cloud'."""
    from telemetry import get_tier
    assert get_tier("S2_cheap") == "cloud"
    assert get_tier("S3_premium") == "cloud"
    assert get_tier("S1_nuvem") == "cloud"
    assert get_tier("S3") == "cloud"
