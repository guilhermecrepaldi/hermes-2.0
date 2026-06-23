#!/usr/bin/env python3
"""Hermes Launcher -- inspired by free-claude-code fcc-claude/fcc-codex.
Wraps external AI coding tools with Hermes config.

Usage:
  python cli/hermes-launcher.py claude -- "write a function"
  python cli/hermes-launcher.py codex -- "generate a test"
  python cli/hermes-launcher.py list
  python cli/hermes-launcher.py doctor
"""
from __future__ import annotations
import sys
import os
import subprocess
from pathlib import Path
from typing import Optional, List

HERMES_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = os.path.expanduser("~/AppData/Local/hermes/config.yaml")

def check_tool(name: str, cmd: List[str]) -> bool:
    try:
        subprocess.run(cmd + ["--version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def doctor() -> int:
    print("=== Hermes Doctor ===")
    print(f"Python: {sys.version.split()[0]}")
    
    config_found = os.path.exists(CONFIG_PATH)
    print(f"Config: {'found' if config_found else 'not found'}")
    
    tools = {
        "ollama": (["ollama"], check_tool("ollama", ["ollama"])),
        "claude": (["claude"], check_tool("claude", ["claude"])),
        "codex": (["codex"], check_tool("codex", ["codex"])),
        "git": (["git"], check_tool("git", ["git"])),
    }
    
    print(f"\nTools:")
    for name, (cmd, found) in tools.items():
        icon = "+" if found else "x"
        status = "OK" if found else "MISSING"
        print(f"  [{icon}] {name}: {status}")
    
    print(f"Tests:", end=" ")
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "--timeout=10"],
                          capture_output=True, timeout=15, cwd=str(HERMES_ROOT))
        if r.returncode == 0:
            print("PASS")
        else:
            print(f"FAIL ({r.returncode} failed)")
    except Exception as e:
        print(f"ERROR: {e}")
    
    return 0

def list_tools() -> int:
    print("=== Hermes Tools ===")
    tools = [
        ("claude", "Claude Code CLI", ["claude"]),
        ("codex", "OpenAI Codex CLI", ["codex"]),
        ("ollama", "Local LLM", ["ollama"]),
        ("git", "Version control", ["git"]),
        ("python", "Python runtime", [sys.executable]),
    ]
    
    for name, desc, cmd in tools:
        found = check_tool(name, cmd) if name != "python" else True
        icon = "+" if found else "x"
        print(f"  [{icon}] {name}: {desc}")
    
    print(f"\nRoot: {HERMES_ROOT}")
    print(f"Config: {CONFIG_PATH}")
    return 0

def launch_claude(args: List[str]) -> int:
    print("Launching Claude Code with Hermes config...")
    env = os.environ.copy()
    env["HERMES_ACTIVE"] = "1"
    env["HERMES_ROOT"] = str(HERMES_ROOT)
    
    try:
        cmd = ["claude"] + (args if args else [])
        proc = subprocess.run(cmd, env=env, cwd=str(HERMES_ROOT))
        return proc.returncode
    except FileNotFoundError:
        print("Error: 'claude' not found.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

def launch_codex(args: List[str]) -> int:
    print("Launching Codex CLI with Hermes config...")
    env = os.environ.copy()
    env["HERMES_ACTIVE"] = "1"
    env["HERMES_ROOT"] = str(HERMES_ROOT)
    
    try:
        cmd = ["codex"] + (args if args else [])
        proc = subprocess.run(cmd, env=env, cwd=str(HERMES_ROOT))
        return proc.returncode
    except FileNotFoundError:
        print("Error: 'codex' not found.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python cli/hermes-launcher.py <tool> [args...]")
        print("Tools: claude, codex, list, doctor")
        return 1
    
    tool = sys.argv[1].lower()
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if tool in ("list", "ls", "--list"):
        return list_tools()
    elif tool in ("doctor", "check", "status"):
        return doctor()
    elif tool in ("claude", "cc"):
        return launch_claude(args)
    elif tool in ("codex", "cx"):
        return launch_codex(args)
    else:
        print(f"Unknown tool: {tool}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
