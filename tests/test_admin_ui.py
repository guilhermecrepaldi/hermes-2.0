"""Testes da Admin UI (inspirado free-claude-code)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from admin_ui import create_app


def test_app_creates():
    """create_app deve retornar uma instancia FastAPI."""
    app = create_app()
    assert app is not None
    assert app.title == "Hermes Admin UI"


def test_app_has_routes():
    """App deve ter rotas registradas."""
    app = create_app()
    routes = [r.path for r in app.routes]
    assert "/" in routes
    assert "/api/status" in routes
    assert "/api/providers" in routes
