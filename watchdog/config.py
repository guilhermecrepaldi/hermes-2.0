"""Hermes 2.0 — Configuração centralizada.
Todos os paths, constantes e defaults em um único lugar.
"""
from __future__ import annotations

import os
from pathlib import Path


def _project_root() -> Path:
    """Raiz do projeto (onde este arquivo está)."""
    return Path(os.path.dirname(os.path.abspath(__file__)))


# --- Paths ---
PROJECT_ROOT: Path = _project_root()
WATCHDOG_DIR: Path = PROJECT_ROOT
THIRD_PARTY_NOTICES: Path = PROJECT_ROOT.parent / "THIRD_PARTY_NOTICES.md"
HERMES_PROGRESS: Path = PROJECT_ROOT.parent / "hermes-progress.md"

# --- Shells ---
SHELL_NAMES = {"S1": "local/Ollama", "S2": "DeepSeek Flash", "S3": "deepseek-pro"}
SHELL_COSTS = {"S1": "$0,00 🆓", "S2": "~$0.15/M ☁️", "S3": "~$0.50/M 🧠"}

# --- Watchdog ---
WATCHDOG_FILES = [
    ("s3_grep.py", "🔍 S3 Grep"),
    ("s1_router.py", "🧭 S1 Router"),
    ("watchdog_hermes.py", "⚙️ Watchdog"),
    ("shellz_menu.bat", "🖥️ Shellz Menu"),
]

# --- Pesquisa ---
RESEARCH_SOURCES = {
    "hn": ("Hacker News", "https://hn.algolia.com/api/v1/search?query={q}"),
    "github": ("GitHub", "https://api.github.com/search/repositories?q={q}"),
    "reddit": ("Reddit", "https://www.reddit.com/search/?q={q}"),
    "x": ("X/Twitter", "https://x.com/search?q={q}&src=typed_query"),
    "youtube": ("YouTube", "https://www.youtube.com/results?search_query={q}"),
    "web": ("Web (DuckDuckGo)", "https://html.duckduckgo.com/html/?q={q}"),
    "polymarket": ("Polymarket", "https://polymarket.com/search?query={q}"),
    "bluesky": ("Bluesky", "https://bsky.app/search?q={q}"),
}

# Fontes com API automatizada (as demais exigem browser_navigate manual)
AUTOMATED_SOURCES = {"hn", "github"}
