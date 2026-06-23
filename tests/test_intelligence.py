"""Testes do Intelligence Core — compactor, reasoning, scanner."""
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from compactor import (
    estimate_tokens, should_compact, compact_conversation,
    _compact_assistant_message, get_compact_stats
)
from reasoning import ReasoningEngine, ReasoningStep, Thought, Decision
from intelligence import ProjectScanner


# ═══════════════════════════════════════════════
# COMPACTOR TESTS
# ═══════════════════════════════════════════════

def test_estimate_tokens():
    """estimate_tokens deve calcular aproximadamente."""
    tokens = estimate_tokens("hello world")
    assert tokens == 2


def test_should_compact_small():
    """Texto pequeno nao deve precisar compactar."""
    assert not should_compact("hello world")


def test_compact_conversation_empty():
    """Conversa vazia nao deve quebrar."""
    result = compact_conversation([])
    assert result == []


def test_compact_conversation_small():
    """Conversa pequena nao deve ser compactada."""
    msgs = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    result = compact_conversation(msgs)
    assert len(result) == 2


def test_compact_assistant_short():
    """Mensagem curta nao deve ser compactada."""
    result = _compact_assistant_message("short msg")
    assert result == "short msg"


def test_get_compact_stats():
    """get_compact_stats deve retornar dict."""
    stats = get_compact_stats()
    assert "total_compactions" in stats
    assert "max_tokens" in stats


# ═══════════════════════════════════════════════
# REASONING ENGINE TESTS
# ═══════════════════════════════════════════════

def test_reasoning_engine_creates():
    """ReasoningEngine deve ser criado."""
    engine = ReasoningEngine()
    assert len(engine.steps) == 0


def test_reasoning_think():
    """think() deve adicionar passo."""
    engine = ReasoningEngine()
    step = engine.think("What is the best approach?")
    assert step.type == "think"
    assert len(engine.steps) == 1


def test_reasoning_analyze():
    """analyze() deve adicionar passo de analise."""
    engine = ReasoningEngine()
    step = engine.analyze("This code has 3 issues")
    assert step.type == "analyze"


def test_reasoning_plan():
    """plan() deve criar plano estruturado."""
    engine = ReasoningEngine()
    step = engine.plan(["Check imports", "Fix types", "Test"])
    assert step.type == "plan"
    assert "Check imports" in step.content


def test_reasoning_verify():
    """verify() deve checar criterios."""
    engine = ReasoningEngine()
    step = engine.verify({"passes": True, "fails": False})
    assert step.type == "verify"
    assert "1/2" in step.result


def test_reasoning_decide():
    """decide() deve registrar decisao."""
    engine = ReasoningEngine()
    decision = engine.decide(
        choice="use local model",
        alternatives=["local", "cloud"],
        reasoning="cost is zero",
        confidence=0.9
    )
    assert decision.choice == "use local model"
    assert len(engine.decisions) == 1


def test_reasoning_summarize():
    """summarize() deve produzir resumo."""
    engine = ReasoningEngine()
    engine.think("thinking...")
    engine.analyze("analyzing...")
    summary = engine.summarize()
    assert "Reasoning Chain" in summary
    assert "Step 1" in summary


# ═══════════════════════════════════════════════
# PROJECT SCANNER TESTS
# ═══════════════════════════════════════════════

def test_scanner_creates():
    """ProjectScanner deve ser criado."""
    scanner = ProjectScanner()
    assert scanner is not None


def test_scanner_scan_current():
    """Scanner deve escanear diretorio atual."""
    scanner = ProjectScanner(str(Path(__file__).resolve().parent.parent))
    ctx = scanner.scan()
    assert ctx["files"] > 0
    assert ctx["name"] == "hermes-2.0"


def test_scanner_key_files():
    """Scanner deve encontrar arquivos-chave."""
    scanner = ProjectScanner(str(Path(__file__).resolve().parent.parent))
    scanner.scan()
    assert "pyproject.toml" in scanner.key_files_found
    assert "README.md" in scanner.key_files_found


def test_scanner_project_type():
    """Scanner deve detectar tipo do projeto."""
    scanner = ProjectScanner(str(Path(__file__).resolve().parent.parent))
    ctx = scanner.scan()
    assert ctx["type"] == "python"


def test_scanner_get_summary():
    """get_summary deve produzir texto."""
    scanner = ProjectScanner(str(Path(__file__).resolve().parent.parent))
    summary = scanner.get_summary()
    assert "Project:" in summary
    assert "python" in summary


def test_scanner_find_by_content():
    """find_by_content deve encontrar padrao."""
    scanner = ProjectScanner(str(Path(__file__).resolve().parent.parent))
    scanner.scan()
    results = scanner.find_by_content("def test_", max_results=3)
    assert len(results) >= 1
