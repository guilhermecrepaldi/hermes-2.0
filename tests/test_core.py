"""Testes dos modulos: core, config, logger, monitor."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))
def test_core_importa():
    from core import ProjectInfo, RouterDecision, ShellCapability
    assert RouterDecision
    assert ProjectInfo
    assert ShellCapability


def test_router_decision_cria():
    from core import RouterDecision
    d = RouterDecision(shell="S1", model="x", cost="$0", reason="teste")
    assert d.shell == "S1"
    assert d.to_dict()["shell"] == "S1"


def test_project_info_cria():
    from core import ProjectInfo
    p = ProjectInfo(name="teste", status="cloned", total_files=10)
    assert p.name == "teste"
    assert p.to_dict()["total_files"] == 10


def test_config_importa():
    from config import AUTOMATED_SOURCES, RESEARCH_SOURCES
    assert RESEARCH_SOURCES
    assert "hn" in AUTOMATED_SOURCES
    assert "github" in AUTOMATED_SOURCES


def test_logger_importa():
    from logger import get_logger
    log = get_logger("test")
    assert log.name == "test"


def test_monitor_importa():
    from monitor import ensure_tools_exist, proc_check, status_report
    assert callable(proc_check)
    assert callable(status_report)
    assert callable(ensure_tools_exist)
