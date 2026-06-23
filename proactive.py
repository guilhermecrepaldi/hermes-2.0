"""Hermes Proactive Analyzer — Suggests improvements without being asked."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class Suggestion:
    type: str
    severity: str
    title: str
    description: str
    file: str = ""
    line: int = 0
    fix: str = ""


class ProactiveAnalyzer:
    def __init__(self, root: Optional[str] = None):
        self.root = Path(root or os.getcwd()).resolve()
        self.suggestions: List[Suggestion] = []
        self._last_scan: dict = {}

    def scan_all(self) -> List[Suggestion]:
        self.suggestions = []
        logger.info(f"Proactive scan: {self.root.name}")
        self._check_test_coverage()
        self._check_code_quality()
        self._check_security()
        self._check_documentation()
        self._last_scan = {
            "time": datetime.now().isoformat(),
            "total": len(self.suggestions),
            "by_severity": {
                "high": sum(1 for s in self.suggestions if s.severity == "high"),
                "medium": sum(1 for s in self.suggestions if s.severity == "medium"),
                "low": sum(1 for s in self.suggestions if s.severity == "low"),
                "info": sum(1 for s in self.suggestions if s.severity == "info"),
            }
        }
        return self.suggestions

    def _check_test_coverage(self):
        for cd in ["watchdog", "tests"]:
            code_dir = self.root / cd
            if not code_dir.exists():
                continue
            for f in code_dir.glob("*.py"):
                if f.name.startswith("test_") or f.name == "__init__.py":
                    continue
                test_name = f"test_{f.name}"
                if not (self.root / "tests" / test_name).exists():
                    self.suggestions.append(Suggestion(
                        type="test", severity="medium",
                        title=f"Missing test: {f.name}",
                        description=f"No test file for {cd}/{f.name}",
                        file=str(f.relative_to(self.root)),
                        fix=f"Create tests/{test_name}",
                    ))

    def _check_code_quality(self):
        SECRET_PATTERN = re.compile(r"(api_key|password|secret|token)\s*=\s*[\"']", re.I)
        for py_file in self.root.rglob("*.py"):
            if any(p.name == "__pycache__" for p in py_file.parents):
                continue
            relative = py_file.relative_to(self.root)
            try:
                text = py_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                stripped = line.strip()
                if re.search(r"except\s*:", stripped) and "Exception" not in stripped:
                    self.suggestions.append(Suggestion(
                        type="code_quality", severity="high",
                        title="Bare except clause", description="Use except Exception:",
                        file=str(relative), line=i, fix="except Exception:",
                    ))
                m = SECRET_PATTERN.search(stripped)
                if m and "os.environ" not in stripped and "os.getenv" not in stripped:
                    self.suggestions.append(Suggestion(
                        type="security", severity="high",
                        title="Possible hardcoded secret",
                        description=f"Secret at line {i}",
                        file=str(relative), line=i,
                        fix="Use env variable or config file",
                    ))

    def _check_security(self):
        for f in self.root.glob(".env*"):
            if f.name != ".env.example":
                self.suggestions.append(Suggestion(
                    type="security", severity="high",
                    title=f"Sensitive file: {f.name}",
                    description="Env files with secrets should be in .gitignore",
                    file=f.name, fix="Ensure .env is in .gitignore",
                ))
        for py_file in self.root.rglob("*.py"):
            if any(p.name == "__pycache__" for p in py_file.parents):
                continue
            try:
                text = py_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if "eval(" in line or "exec(" in line:
                    self.suggestions.append(Suggestion(
                        type="security", severity="high",
                        title="Unsafe eval/exec usage",
                        description="Can execute arbitrary code",
                        file=str(py_file.relative_to(self.root)), line=i,
                        fix="Use ast.literal_eval()",
                    ))

    def _check_documentation(self):
        if not (self.root / "README.md").exists():
            self.suggestions.append(Suggestion(
                type="documentation", severity="medium",
                title="Missing README.md",
                description="Project has no README",
                fix="Create README.md",
            ))
        pyproject = self.root / "pyproject.toml"
        if pyproject.exists():
            text = pyproject.read_text()
            if 'description = ""' in text or 'description = " "' in text:
                self.suggestions.append(Suggestion(
                    type="documentation", severity="low",
                    title="Empty project description",
                    description="pyproject.toml has no description",
                    file="pyproject.toml", fix="Add a description",
                ))

    def get_summary(self) -> str:
        if not self.suggestions:
            return "No suggestions found. Clean."
        sev = self._last_scan.get("by_severity", {})
        lines = [
            "Proactive Scan:",
            f"  {len(self.suggestions)} suggestions",
            f"  High: {sev.get('high',0)} | Medium: {sev.get('medium',0)} | Low: {sev.get('low',0)}",
            "",
        ]
        for s in self.suggestions[:5]:
            icons = {"high": "!", "medium": "-", "low": ".", "info": "i"}
            lines.append(f"  [{icons.get(s.severity,'?')}] {s.title}")
        if len(self.suggestions) > 5:
            lines.append(f"  ... +{len(self.suggestions)-5} more")
        return "\n".join(lines)

    def get_stats(self) -> dict:
        return self._last_scan
