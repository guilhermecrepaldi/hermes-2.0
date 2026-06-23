"""Testes do Auto-Healer, Task Decomposer, Semantic Memory."""
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from healer import AutoHealer
from decomposer import TaskDecomposer, SubTask
from smemory import SemanticMemory


# ═══════════════════════════════════════════════
# AUTO-HEALER TESTS
# ═══════════════════════════════════════════════

def test_healer_creates():
    """AutoHealer deve ser criado com estrategias."""
    h = AutoHealer()
    assert len(h.strategies) >= 3


def test_healer_classify_file_not_found():
    """Erro de arquivo deve ser classificado como file_not_found."""
    h = AutoHealer()
    result = h.heal("No such file or directory: test.py", {"path": "test.py"})
    assert result["healed"]


def test_healer_classify_command_not_found():
    """Erro de comando deve ser classificado como command_not_found."""
    h = AutoHealer()
    result = h.heal("command not found: python", {"cmd": "python"})
    assert result["healed"]


def test_healer_no_strategies():
    """Erro desconhecido deve usar fallback."""
    h = AutoHealer()
    result = h.heal("some weird error", {})
    assert "healed" in result


def test_healer_get_stats():
    """get_stats deve retornar dict."""
    h = AutoHealer()
    stats = h.get_stats()
    assert "strategies" in stats
    assert "error_types" in stats


# ═══════════════════════════════════════════════
# TASK DECOMPOSER TESTS
# ═══════════════════════════════════════════════

def test_decomposer_creates():
    """TaskDecomposer deve ser criado."""
    d = TaskDecomposer()
    assert d is not None


def test_decompose_code_task():
    """Tarefa de codigo deve gerar 6 subtasks."""
    d = TaskDecomposer()
    plan = d.decompose("Create a new API endpoint")
    assert len(plan.subtasks) == 6
    assert plan.subtasks[0].type == "analyze"


def test_decompose_research_task():
    """Tarefa de pesquisa deve gerar 4 subtasks."""
    d = TaskDecomposer()
    plan = d.decompose("Pesquisar concorrentes")
    assert len(plan.subtasks) == 4


def test_decompose_setup_task():
    """Tarefa de setup deve gerar 5 subtasks."""
    d = TaskDecomposer()
    plan = d.decompose("Setup new project")
    assert len(plan.subtasks) == 5


def test_decompose_analysis_task():
    """Tarefa de analise deve gerar 4 subtasks."""
    d = TaskDecomposer()
    plan = d.decompose("Audit the codebase")
    assert len(plan.subtasks) == 4


def test_decompose_general_task():
    """Tarefa generica deve gerar 4 subtasks."""
    d = TaskDecomposer()
    plan = d.decompose("Help me with something")
    assert len(plan.subtasks) == 4


def test_parallel_groups():
    """Planos devem ter grupos paralelos."""
    d = TaskDecomposer()
    plan = d.decompose("Create API endpoint")
    assert len(plan.parallel_groups) >= 2


def test_subtask_can_run():
    """SubTask verifica dependencias corretamente."""
    s = SubTask("S3", "test", "verify", dependencies=["S1", "S2"])
    assert not s.can_run(set())
    assert s.can_run({"S1", "S2"})


# ═══════════════════════════════════════════════
# SEMANTIC MEMORY TESTS
# ═══════════════════════════════════════════════

def test_memory_creates():
    """SemanticMemory deve ser criado."""
    m = SemanticMemory()
    assert m.memories is not None


def test_memory_remember():
    """remember() deve adicionar entrada."""
    m = SemanticMemory()
    entry = m.remember("test memory", "test", tags=["test"])
    assert entry.content == "test memory"
    assert entry.category == "test"


def test_memory_recall():
    """recall() deve encontrar por palavra-chave."""
    m = SemanticMemory()
    m.remember("Remember to use local models first", "decision", tags=["local", "model"])
    results = m.recall("local model")
    assert len(results) >= 1


def test_memory_recall_by_category():
    """recall_by_category() deve filtrar por categoria."""
    m = SemanticMemory()
    m.remember("test preference", "preference", tags=["preference"])
    results = m.recall_by_category("preference")
    assert len(results) >= 1


def test_memory_remember_error():
    """remember_error() deve criar entrada com categoria error."""
    m = SemanticMemory()
    entry = m.remember_error("File not found", "Create the file first")
    assert entry.category == "error"


def test_memory_remember_success():
    """remember_success() deve criar entrada com categoria success."""
    m = SemanticMemory()
    entry = m.remember_success("Use ollama", "Fast and free")
    assert entry.category == "success"


def test_memory_stats():
    """get_stats() deve retornar dict."""
    m = SemanticMemory()
    stats = m.get_stats()
    assert "total" in stats
    assert "categories" in stats
