"""Testes das melhorias inspiradas no ECC (223K stars)."""
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from agent_shield import verify_pre_tool, verify_post_tool, doctor as shield_doctor
from memory_hooks import hook_pre_tool, hook_post_tool, get_memory_feed


def test_shield_blocks_destructive():
    """Agent Shield deve bloquear rm -rf /."""
    result = verify_pre_tool("Terminal", {"command": "rm -rf /"})
    assert result["allowed"] == False
    assert "DESTRUTIVO" in result["reason"]


def test_shield_allows_safe():
    """Agent Shield deve permitir comandos seguros."""
    result = verify_pre_tool("Terminal", {"command": "ls -la"})
    assert result["allowed"] == True


def test_shield_blocks_env_write():
    """Agent Shield deve bloquear escrita em .env."""
    result = verify_pre_tool("Write", {"path": "/path/to/.env"})
    assert result["allowed"] == False
    assert "SENSIVEL" in result["reason"]


def test_shield_allows_normal_write():
    """Agent Shield deve permitir escrita em arquivos normais."""
    result = verify_pre_tool("Write", {"path": "/path/to/main.py"})
    assert result["allowed"] == True


def test_shield_detects_secrets():
    """Agent Shield deve detectar secrets no output."""
    result = verify_post_tool("Terminal", {"output": "API_KEY=sk-abc123def456"})
    assert result["safe"] == False


def test_shield_clean_output():
    """Output limpo deve ser seguro."""
    result = verify_post_tool("Terminal", {"output": "hello world"})
    assert result["safe"] == True


def test_shield_blocks_format():
    """Agent Shield deve bloquear format C:."""
    result = verify_pre_tool("Terminal", {"command": "format C: /FS:NTFS"})
    assert result["allowed"] == False


def test_shield_doctor():
    """doctor() deve retornar status."""
    d = shield_doctor()
    assert d["status"] == "active"
    assert d["destructive_patterns"] > 0


def test_memory_hooks_pre():
    """Pre-hook nao deve modificar args para ferramentas seguras."""
    result = hook_pre_tool("Terminal", {"command": "ls"})
    assert "modified_args" in result


def test_memory_hooks_post():
    """Post-hook deve executar sem erro."""
    try:
        hook_post_tool("Terminal", {"success": True}, {"summary": "teste"})
        assert True
    except Exception as e:
        assert False, f"Post-hook falhou: {e}"


def test_memory_feed():
    """get_memory_feed deve retornar lista."""
    feed = get_memory_feed(limit=5)
    assert isinstance(feed, list)


def test_memory_hooks_write_pre():
    """Pre-hook de Write deve logar o path."""
    result = hook_pre_tool("Write", {"path": "/tmp/test.py"})
    assert result["modified_args"]["path"] == "/tmp/test.py"
