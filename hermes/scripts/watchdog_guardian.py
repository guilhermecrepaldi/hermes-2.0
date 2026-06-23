#!/usr/bin/env python3
"""Hermes 2.0 - Watchdog Guardian (Python = sem janela cmd)
Executado pelo cron a CADA MINUTO.
Nao abre nenhuma janela - Python puro.
Garante que watchdog + Ollama estao rodando 24/7.
"""

import os
import subprocess
from datetime import datetime

# ─── CONFIG ───
WATCHDOG_VBS = r"D:\projetos\hermes-watchdog\watchdog_invisible.vbs"
OLLAMA_VBS = r"D:\projetos\hermes-watchdog\ollama_invisible.vbs"
TRAY_VBS = r"D:\projetos\hermes-watchdog\shellz_tray_guardian.vbs"
PAUSE_FLAG = os.path.expanduser("~/.shellz_paused")
LOG_DIR = os.path.expanduser("~/hermes-watchdog/logs")
OLLAMA_EXE = r"C:\Users\Home\AppData\Local\Programs\Ollama\ollama.exe"


def log(msg):
    os.makedirs(LOG_DIR, exist_ok=True)
    logfile = os.path.join(LOG_DIR, f"guardian_{datetime.now().strftime('%Y%m%d')}.log")
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [GUARDIAN] {msg}\n")


def is_process_running(name):
    """Check if a process with the given name is running."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {name}", "/NH"],
            capture_output=True, text=True, timeout=10
        )
        return name.lower() in result.stdout.lower()
    except Exception:
        return False


def launch_vbs(vbs_path, name):
    """Launch a VBS script invisibly via wscript."""
    subprocess.Popen(
        ["wscript.exe", "/B", vbs_path],
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    log(f"{name} lancado via VBS")


def main():
    # ─── 1. WATCHDOG ───
    if not is_process_running("cmd.exe"):
        # Might not be running - check via wmic for the watchdog script
        try:
            result = subprocess.run(
                ["wmic", "process", "where", "name='cmd.exe' and commandline like '%watchdog%'", "get", "processid"],
                capture_output=True, text=True, timeout=10
            )
            if not any(line.strip().isdigit() for line in result.stdout.splitlines()):
                launch_vbs(WATCHDOG_VBS, "Watchdog")
        except Exception:
            launch_vbs(WATCHDOG_VBS, "Watchdog")
    else:
        # Check if the running cmd is actually our watchdog
        try:
            result = subprocess.run(
                ["wmic", "process", "where", "name='cmd.exe' and commandline like '%watchdog%'", "get", "processid"],
                capture_output=True, text=True, timeout=10
            )
            watchdog_pids = [line.strip() for line in result.stdout.splitlines() if line.strip().isdigit()]
            if not watchdog_pids:
                launch_vbs(WATCHDOG_VBS, "Watchdog")
        except Exception:
            pass

    # ─── 2. OLLAMA (só se NÃO estiver pausado) ───
    if not os.path.exists(PAUSE_FLAG):
        if not is_process_running("ollama.exe"):
            launch_vbs(OLLAMA_VBS, "Ollama")
            log("Ollama reiniciado (nao estava rodando)")

    # ─── 3. TRAY GUARDIAN ───
    if not is_process_running("wscript.exe"):
        # Could have multiple wscript, check via wmic for our tray
        try:
            result = subprocess.run(
                ["wmic", "process", "where", "name='wscript.exe'", "get", "CommandLine"],
                capture_output=True, text=True, timeout=10
            )
            if "shellz_tray" not in result.stdout.lower():
                launch_vbs(TRAY_VBS, "Shellz Tray Guardian")
        except Exception:
            launch_vbs(TRAY_VBS, "Shellz Tray Guardian")

    # ─── 4. STARTUP SHORTCUTS (recriar se deletados) ───
    startup_dir = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
    shortcuts = {
        "ShellzTray.lnk": ("wscript.exe", '/B "D:\\projetos\\hermes-watchdog\\shellz_tray_guardian.vbs"'),
        "HermesShellz_Ollama.lnk": ("wscript.exe", '/B "D:\\projetos\\hermes-watchdog\\ollama_invisible.vbs"'),
        "HermesWatchdog.lnk": ("wscript.exe", '/B "D:\\projetos\\hermes-watchdog\\watchdog_invisible.vbs"'),
    }

    for shortcut, (target, args) in shortcuts.items():
        shortcut_path = os.path.join(startup_dir, shortcut)
        if not os.path.exists(shortcut_path):
            try:
                ps_script = f"""
$wshell = New-Object -ComObject WScript.Shell
$s = $wshell.CreateShortcut('{shortcut_path}')
$s.TargetPath = '{target}'
$s.Arguments = '{args}'
$s.WorkingDirectory = 'D:\\projetos\\hermes-watchdog'
$s.WindowStyle = 7
$s.Save()
"""
                subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True, timeout=15, creationflags=subprocess.CREATE_NO_WINDOW
                )
                log(f"Startup shortcut recriado: {shortcut}")
            except Exception as e:
                log(f"Erro ao recriar {shortcut}: {e}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"ERRO: {e}")
