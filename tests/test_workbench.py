"""Testes do Workbench CLI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

def test_s1_router_importa():
    """Modulo s1_router deve importar sem erros."""
    from s1_router import classify_task
    assert callable(classify_task)

