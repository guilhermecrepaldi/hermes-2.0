"""Testes dos Launchers CLI."""
from pathlib import Path
import sys

CLI_DIR = str(Path(__file__).resolve().parent.parent / "cli")
WD_DIR = str(Path(__file__).resolve().parent.parent / "watchdog")

if CLI_DIR not in sys.path:
    sys.path.insert(0, CLI_DIR)
if WD_DIR not in sys.path:
    sys.path.insert(0, WD_DIR)

# Import the launcher module directly
import importlib.util
spec = importlib.util.spec_from_file_location("launcher", 
    Path(__file__).resolve().parent.parent / "cli" / "hermes-launcher.py")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


def test_list_tools_runs():
    """list_tools deve executar sem erros."""
    result = launcher.list_tools()
    assert result == 0


def test_doctor_runs():
    """doctor deve executar sem erros."""
    result = launcher.doctor()
    assert result == 0
