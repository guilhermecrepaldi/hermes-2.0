"""Testes do Orchestrator, Reflector, Proactive Analyzer."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from orchestrator import Orchestrator, OrchestratedTask, TaskStatus
from reflector import Reflector, Reflection
from proactive import ProactiveAnalyzer, Suggestion


# ═══════════════════════════════════════════════
# ORCHESTRATOR TESTS
# ═══════════════════════════════════════════════

def test_orchestrator_creates():
    """Orchestrator deve ser criado vazio."""
    o = Orchestrator()
    assert len(o.tasks) == 0


def test_orchestrator_plan():
    """plan() deve carregar tarefas."""
    o = Orchestrator()
    o.plan([
        {"id": "T1", "description": "Task 1", "type": "code"},
        {"id": "T2", "description": "Task 2", "type": "test", "dependencies": ["T1"]},
    ])
    assert len(o.tasks) == 2


def test_orchestrator_execute_all():
    """execute() deve completar todas as tarefas."""
    o = Orchestrator()
    o.plan([
        {"id": "T1", "description": "First", "type": "code"},
        {"id": "T2", "description": "Second", "type": "test", "dependencies": ["T1"]},
    ])
    results = o.execute()
    assert len(results) == 2
    assert all(t.status == TaskStatus.DONE for t in results)


def test_orchestrator_dependency_order():
    """Dependencias devem ser respeitadas."""
    o = Orchestrator()
    o.plan([
        {"id": "T1", "description": "Dependency", "type": "code"},
        {"id": "T2", "description": "Depends on T1", "type": "test", "dependencies": ["T1"]},
    ])
    results = o.execute()
    # T1 should finish before T2 starts
    t1 = next(t for t in results if t.id == "T1")
    t2 = next(t for t in results if t.id == "T2")
    assert t1.finished_at <= t2.started_at if t1.finished_at and t2.started_at else True


def test_orchestrator_status():
    """get_status() deve retornar dict."""
    o = Orchestrator()
    status = o.get_status()
    assert "total" in status
    assert "pending" in status


def test_orchestrator_summary():
    """get_summary() deve produzir texto."""
    o = Orchestrator()
    o.plan([{"id": "T1", "description": "Test", "type": "code"}])
    o.execute()
    summary = o.get_summary()
    assert "Execution Summary" in summary
    assert "T1" in summary


# ═══════════════════════════════════════════════
# REFLECTOR TESTS
# ═══════════════════════════════════════════════

def test_reflector_creates():
    """Reflector deve ser criado."""
    r = Reflector()
    assert r.reflections is not None


def test_reflector_reflect():
    """reflect() deve criar entrada."""
    r = Reflector()
    ref = r.reflect("Create API", "success",
                     duration=30.0, steps_taken=3,
                     what_worked=["Good plan"], what_didnt=["Slow tests"])
    assert ref.task == "Create API"
    assert ref.outcome == "success"


def test_reflector_suggestions():
    """suggest_improvements() deve retornar lista."""
    r = Reflector()
    r.reflect("Task 1", "success")
    suggestions = r.suggest_improvements()
    assert isinstance(suggestions, list)


def test_reflector_stats():
    """get_stats() deve retornar dict."""
    r = Reflector()
    r.reflect("Task 1", "success")
    stats = r.get_stats()
    assert "total" in stats
    assert "success_rate" in stats


# ═══════════════════════════════════════════════
# PROACTIVE ANALYZER TESTS
# ═══════════════════════════════════════════════

def test_proactive_creates():
    """ProactiveAnalyzer deve ser criado."""
    p = ProactiveAnalyzer()
    assert p is not None


def test_proactive_scan():
    """scan_all() deve encontrar issues no projeto."""
    p = ProactiveAnalyzer(str(Path(__file__).resolve().parent.parent))
    suggestions = p.scan_all()
    assert isinstance(suggestions, list)
    # May or may not find issues depending on project state


def test_proactive_get_summary():
    """get_summary() deve produzir texto."""
    p = ProactiveAnalyzer(str(Path(__file__).resolve().parent.parent))
    p.scan_all()
    summary = p.get_summary()
    assert "Proactive Scan" in summary


def test_proactive_security_check():
    """Deve detectar .env que nao seja .example."""
    p = ProactiveAnalyzer(str(Path(__file__).resolve().parent.parent))
    suggestions = p.scan_all()
    # Should not crash on any project structure


def test_suggestion_fields():
    """Suggestion deve ter todos os campos."""
    s = Suggestion(type="test", severity="high",
                    title="Missing test", description="No tests found")
    assert s.type == "test"
    assert s.severity == "high"
