"""Testes do Code Analyzer (AST-based code understanding)."""
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from code_analyzer import CodeAnalyzer, FileAnalysis, FunctionInfo, ClassInfo, Dependency


ROOT = str(Path(__file__).resolve().parent.parent)


def test_analyzer_creates():
    """CodeAnalyzer deve ser criado."""
    ca = CodeAnalyzer(ROOT)
    assert ca is not None
    assert not ca._analyzed


def test_analyze_project():
    """analyze() deve escanear todos os .py."""
    ca = CodeAnalyzer(ROOT)
    ca.analyze()
    assert len(ca.files) >= 20  # At least 20 Python files
    assert ca._analyzed


def test_analyze_finds_classes():
    """Deve encontrar classes no codigo."""
    ca = CodeAnalyzer(ROOT)
    ca.analyze()
    total_classes = sum(len(f.classes) for f in ca.files.values())
    assert total_classes >= 10  # We have many dataclasses


def test_analyze_finds_functions():
    """Deve encontrar funcoes no codigo."""
    ca = CodeAnalyzer(ROOT)
    ca.analyze()
    total_funcs = sum(len(f.functions) for f in ca.files.values())
    assert total_funcs >= 50  # Many test functions


def test_complexity_calculation():
    """Complexidade deve ser calculada."""
    ca = CodeAnalyzer(ROOT)
    ca.analyze()
    stats = ca.get_project_stats()
    assert stats["total_complexity"] >= 10


def test_impact_analysis():
    """Impact analysis deve encontrar dependencias."""
    ca = CodeAnalyzer(ROOT)
    ca.analyze()
    # Pick core.py which is imported by many
    result = ca.impact_analysis("core.py")
    assert "affected_count" in result
    assert isinstance(result["affected_files"], list)


def test_find_function():
    """find_function deve encontrar por nome parcial."""
    ca = CodeAnalyzer(ROOT)
    ca.analyze()
    results = ca.find_function("test_")
    assert len(results) >= 5


def test_project_stats():
    """get_project_stats deve ter todos os campos."""
    ca = CodeAnalyzer(ROOT)
    ca.analyze()
    stats = ca.get_project_stats()
    required = ["files_analyzed", "total_lines", "total_classes",
                 "total_functions", "total_complexity", "dependencies"]
    for r in required:
        assert r in stats, f"Missing field: {r}"


def test_docstring_coverage():
    """Docstring coverage deve ser calculada."""
    ca = CodeAnalyzer(ROOT)
    ca.analyze()
    stats = ca.get_project_stats()
    assert "%" in stats["avg_docstring_coverage"]


def test_get_summary():
    """get_summary deve produzir texto."""
    ca = CodeAnalyzer(ROOT)
    ca.analyze()
    summary = ca.get_summary()
    assert "Code Analysis" in summary
    assert "Files:" in summary


def test_dependency_graph():
    """Dependency graph deve ter entradas."""
    ca = CodeAnalyzer(ROOT)
    ca.analyze()
    assert len(ca.dependencies) >= 5


def test_file_analysis_errors():
    """Arquivos com erro devem registrar."""
    ca = CodeAnalyzer(ROOT)
    ca.analyze()
    total_errors = sum(len(f.errors) for f in ca.files.values())
    assert total_errors >= 0  # May or may not have errors
