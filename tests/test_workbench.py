"""Testes do Workbench CLI."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

def test_s1_router_importa():
    """Modulo s1_router deve importar sem erros."""
    from s1_router import classify_task
    assert callable(classify_task)


def test_s3_headroom_importa():
    """Modulo s3_headroom deve importar sem erros."""
    from s3_headroom import project_load
    assert callable(project_load)
