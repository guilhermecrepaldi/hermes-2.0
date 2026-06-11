#!/usr/bin/env python3
"""
Hermes 2.0 - Watchdog Principal (Python = zero janelas)
Loop infinito a cada 5 minutos.
Monitora Hermes (node.exe), Ollama e recria shortcuts.
Executado via pythonw.exe - NUNCA abre console.
"""
import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# ─── CONFIG ───
USER_HOME = os.path.expanduser("~")
WATCH_DIR = os.path.join(USER_HOME, "hermes-watchdog")
LOG_DIR = os.path.join(WATCH_DIR, "logs")
HERMES_LOG = os.path.join(USER_HOME, "AppData", "Local", "hermes", "logs", "agent.log")
OLLAMA_EXE = r"C:\Users\Home\AppData\Local\Programs\Ollama\ollama.exe"
PAUSE_FLAG = os.path.join(USER_HOME, ".shellz_paused")
INTERVAL_SEC = 300  # 5 minutes
OLLAMA_VBS = r"D:\projetos\hermes-watchdog\ollama_invisible.vbs"
TRAY_VBS = r"D:\projetos\hermes-watchdog\shellz_tray_guardian.vbs"


def log(msg: str, category: str = "WATCHDOG"):
    os.makedirs(LOG_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    logfile = os.path.join(LOG_DIR, f"watchdog_{today}.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{category}] {msg}\n")


def save_state(status: str, action: str):
    state = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "action": action,
    }
    try:
        with open(os.path.join(WATCH_DIR, "watchdog_state.json"), "w") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass


def is_process_running(name: str) -> bool:
    """Check if a process with the given name is running."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {name}", "/NH"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return name.lower() in result.stdout.lower()
    except Exception:
        return False


def run_hidden(cmd: list, timeout: int = 10) -> subprocess.CompletedProcess:
    """Run a command with no window."""
    return subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=timeout,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def launch_vbs(vbs_path: str):
    """Launch a VBS script via wscript (invisible)."""
    subprocess.Popen(
        ["wscript.exe", "/B", vbs_path],
        creationflags=subprocess.CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def get_log_age_minutes() -> int:
    """Check how many minutes since the Hermes log was last modified."""
    try:
        log_path = Path(HERMES_LOG)
        if not log_path.exists():
            return -1
        mtime = log_path.stat().st_mtime
        age_sec = time.time() - mtime
        return int(age_sec // 60)
    except Exception:
        return -1


def recreate_startup_shortcut(name: str, target: str, args: str, description: str):
    """Recreate a startup shortcut if missing."""
    startup_dir = os.path.expandvars(
        r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
    )
    shortcut_path = os.path.join(startup_dir, name)
    if os.path.exists(shortcut_path):
        return

    ps_script = f"""
$wshell = New-Object -ComObject WScript.Shell
$s = $wshell.CreateShortcut('{shortcut_path}')
$s.TargetPath = '{target}'
$s.Arguments = '{args}'
$s.Description = '{description}'
$s.WorkingDirectory = 'D:\\projetos\\hermes-watchdog'
$s.WindowStyle = 7
$s.Save()
"""
    try:
        run_hidden([
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script
        ])
        log(f"Startup shortcut recriado: {name}", "SHORTCUT")
    except Exception as e:
        log(f"Erro ao recriar {name}: {e}", "SHORTCUT")


def main_loop():
    log("Hermes Watchdog iniciado (modo pythonw, zero janelas)", "INFO")
    
    while True:
        try:
            # ─── 1. HERMES HEALTH CHECK ───
            hermes_running = is_process_running("node.exe")
            
            if not hermes_running:
                save_state("idle", "hermes_not_running")
                log("Hermes (node.exe) nao esta rodando", "IDLE")
            else:
                # Check if log is stale
                log_age = get_log_age_minutes()
                if log_age > 25:
                    log(f"TRAVADO: Log nao atualizado ha {log_age}min", "WARN")
                    save_state("recovery", f"killed_log_stale_{log_age}min")
                    
                    # Kill frozen Hermes
                    run_hidden(["taskkill", "/F", "/IM", "node.exe"])
                    log("Hermes finalizado (taskkill /F node.exe)", "RECOVERY")
                else:
                    save_state("healthy", "monitoring")
            
            # ─── 2. OLLAMA CHECK ───
            if not os.path.exists(PAUSE_FLAG):
                if not is_process_running("ollama.exe"):
                    launch_vbs(OLLAMA_VBS)
                    log("Ollama reiniciado (nao estava rodando)", "OLLAMA")

            # ─── 3. STARTUP SHORTCUTS ───
            recreate_startup_shortcut(
                "HermesWatchdog.lnk",
                "wscript.exe",
                '/B "D:\\projetos\\hermes-watchdog\\watchdog_invisible.vbs"',
                "Hermes 2.0 - Watchdog 24/7",
            )
            recreate_startup_shortcut(
                "ShellzTray.lnk",
                "wscript.exe",
                '/B "D:\\projetos\\hermes-watchdog\\shellz_tray_guardian.vbs"',
                "Shellz Tray - Pausar/Retomar Ollama",
            )
            
            # ─── 4. WAIT ───
            time.sleep(INTERVAL_SEC)
            
        except Exception as e:
            log(f"ERRO no loop principal: {e}", "ERROR")
            time.sleep(30)


if __name__ == "__main__":
    main_loop()
