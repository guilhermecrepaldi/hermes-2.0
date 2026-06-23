"""Hermes Intelligence Core — Autonomous project understanding.
Inspired by Claude Code's file awareness and project context building.
"""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ProjectScanner:
    """Autonomous project understanding on startup.

    Scans the project directory, identifies key files, builds context.
    Like Claude Code's automatic project awareness.
    """

    IGNORE_DIRS = {"__pycache__", ".git", ".github", "node_modules",
                   ".venv", "venv", "dist", "build", ".pytest_cache"}
    IGNORE_EXTS = {".pyc", ".pyo", ".exe", ".dll", ".so", ".o", ".obj"}

    KEY_FILES = {
        "pyproject.toml": "Python project config",
        "package.json": "Node project config",
        "README.md": "Documentation",
        "index.html": "Entry point",
        "main.py": "Main module",
        "app.py": "Application entry",
        "Dockerfile": "Container config",
        "docker-compose.yml": "Container orchestration",
        ".env.example": "Environment template",
    }

    def __init__(self, root: Optional[str] = None):
        self.root = Path(root or os.getcwd()).resolve()
        self.files: Dict[str, dict] = {}
        self.structure: Dict[str, Any] = {}
        self.key_files_found: Dict[str, str] = {}
        self.stats: Dict[str, int] = {}
        self._scanned = False

    def scan(self) -> dict:
        """Scan project and build context."""
        if self._scanned:
            return self._context()

        logger.info(f"Scanning project: {self.root}")

        # Scan all files recursively
        for path in self.root.rglob("*"):
            if path.is_file() and not self._should_ignore(path):
                rel_path = path.relative_to(self.root)
                ext = path.suffix
                size = path.stat().st_size

                self.files[str(rel_path)] = {
                    "name": path.name,
                    "ext": ext,
                    "size": size,
                    "lines": self._count_lines(path) if ext in (".py", ".js", ".ts", ".html", ".css", ".md", ".json", ".yaml", ".yml", ".toml") else 0,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                }

                # Track key files
                if path.name in self.KEY_FILES:
                    self.key_files_found[path.name] = str(rel_path)

        # Build stats
        exts = {}
        total_lines = 0
        for info in self.files.values():
            ext = info["ext"]
            exts[ext] = exts.get(ext, 0) + 1
            total_lines += info["lines"]

        self.stats = {
            "total_files": len(self.files),
            "total_lines": total_lines,
            "languages": exts,
            "key_files": len(self.key_files_found),
        }

        self._scanned = True
        logger.info(f"Scanned {len(self.files)} files, {total_lines} lines")
        return self._context()

    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored."""
        if path.suffix in self.IGNORE_EXTS:
            return True
        for part in path.parts:
            if part in self.IGNORE_DIRS:
                return True
        return False

    def _count_lines(self, path: Path) -> int:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
            return len(text.splitlines())
        except Exception:
            return 0

    def _context(self) -> dict:
        """Build project context."""
        return {
            "root": str(self.root),
            "name": self.root.name,
            "files": self.stats.get("total_files", 0),
            "lines": self.stats.get("total_lines", 0),
            "languages": self.stats.get("languages", {}),
            "key_files": self.key_files_found,
            "type": self._detect_project_type(),
            "scanned_at": datetime.now().isoformat(),
        }

    def _detect_project_type(self) -> str:
        """Detect project type from key files."""
        if "pyproject.toml" in self.key_files_found:
            return "python"
        if "package.json" in self.key_files_found:
            return "javascript"
        if "index.html" in self.key_files_found:
            return "web"
        if "Dockerfile" in self.key_files_found:
            return "docker"
        return "unknown"

    def find_by_content(self, pattern: str, max_results: int = 5) -> List[dict]:
        """Find files by content pattern (like Claude's file search)."""
        results = []
        for rel_path, info in self.files.items():
            if len(results) >= max_results:
                break
            if info["ext"] in (".py", ".js", ".ts", ".html", ".css", ".md"):
                try:
                    full_path = self.root / rel_path
                    text = full_path.read_text(encoding="utf-8", errors="ignore")
                    if pattern in text:
                        results.append({"path": rel_path, "lines": info["lines"]})
                except Exception:
                    pass
        return results

    def get_summary(self) -> str:
        """Get a human-readable project summary."""
        if not self._scanned:
            self.scan()

        ctx = self._context()
        lines = [
            f"Project: {ctx['name']}",
            f"Type: {ctx['type']}",
            f"Files: {ctx['files']} ({ctx['lines']} lines)",
        ]

        if ctx["key_files"]:
            lines.append(f"Key files: {', '.join(ctx['key_files'].keys())}")

        if ctx["languages"]:
            top_langs = sorted(ctx["languages"].items(),
                              key=lambda x: x[1], reverse=True)[:5]
            lines.append(f"Languages: {', '.join(f'{ext} ({n})' for ext, n in top_langs)}")

        return "\n".join(lines)
