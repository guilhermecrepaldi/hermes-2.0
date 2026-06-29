"""
headroom_watchdog.py — Cron script to keep Headroom proxy alive.
Checks every 5min if :8787 is responding, restarts if dead.

This runs as no_agent cron job — stdout is delivered verbatim when non-empty.
"""
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
# In Windows, HERMES_HOME is at C:\Users\Home\AppData\Local\hermes
# Use the actual path
if not os.path.isdir(HERMES_HOME):
    HERMES_HOME = os.path.expandvars(r"%LOCALAPPDATA%\hermes")
    if "~" in HERMES_HOME:
        HERMES_HOME = os.path.join(os.path.expanduser("~"), "AppData", "Local", "hermes")

# Also check relative to scripts/
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPTS_DIR)  # hermes/

PROXY_URL = "http://127.0.0.1:8787/health"

def _find_proxy_script():
    """Find headroom_proxy.py in likely locations."""
    candidates = [
        os.path.join(HERMES_HOME, "hermes-agent", "headroom_proxy.py"),
        os.path.join(PARENT_DIR, "hermes-agent", "headroom_proxy.py"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None

def _find_venv_python():
    """Find the venv python executable."""
    candidates = [
        os.path.join(HERMES_HOME, "hermes-agent", "venv", "Scripts", "python.exe"),
        os.path.join(PARENT_DIR, "hermes-agent", "venv", "Scripts", "python.exe"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    # Fallback to system python
    return sys.executable


def check_health():
    """Return True if proxy is healthy."""
    try:
        req = urllib.request.Request(PROXY_URL)
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status == 200
    except (urllib.error.URLError, ConnectionError, OSError):
        return False


def restart_proxy():
    """Start the headroom proxy."""
    proxy_path = _find_proxy_script()
    if not proxy_path:
        return "CRITICAL: headroom_proxy.py not found"

    python_exe = _find_venv_python()

    try:
        proc = subprocess.Popen(
            [python_exe, proxy_path, "--port", "8787", "--upstream", "https://api.deepseek.com"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        # Wait a moment and verify
        time.sleep(2)
        if check_health():
            return f"✅ Headroom proxy restarted (PID {proc.pid})"
        else:
            return f"⚠️  Proxy start attempted but not responding yet (PID {proc.pid})"
    except Exception as e:
        return f"❌ Failed to start proxy: {e}"


def main():
    if check_health():
        # Silent = nothing to report (watchdog pattern)
        return

    # Proxy is down — restart
    result = restart_proxy()
    print(result)


if __name__ == "__main__":
    main()
