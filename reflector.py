"""Hermes Self-Reflection — Post-task analysis and improvement.
Analyzes what worked, what didn't, and stores learnings for next time.
Like Claude Code learning from its own execution.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

REFLECTIONS_DIR = Path.home() / ".hermes" / "reflections"


@dataclass
class Reflection:
    """A post-task reflection."""
    task: str
    outcome: str  # success | partial | failed
    duration: float = 0.0
    steps_taken: int = 0
    errors_encountered: List[str] = field(default_factory=list)
    what_worked: List[str] = field(default_factory=list)
    what_didnt: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    confidence_gained: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class Reflector:
    """Analyzes completed tasks and extracts learnings."""

    def __init__(self):
        REFLECTIONS_DIR.mkdir(parents=True, exist_ok=True)
        self.reflections: List[Reflection] = []
        self._load()

    def _load(self):
        path = REFLECTIONS_DIR / "reflections.json"
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                self.reflections = [Reflection(**item) for item in data]
                logger.info(f"Loaded {len(self.reflections)} reflections")
            except Exception:
                pass

    def _save(self):
        path = REFLECTIONS_DIR / "reflections.json"
        try:
            data = [{
                "task": r.task, "outcome": r.outcome, "duration": r.duration,
                "steps_taken": r.steps_taken, "errors_encountered": r.errors_encountered,
                "what_worked": r.what_worked, "what_didnt": r.what_didnt,
                "improvements": r.improvements, "confidence_gained": r.confidence_gained,
                "timestamp": r.timestamp,
            } for r in self.reflections]
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def reflect(self, task: str, outcome: str, **kwargs) -> Reflection:
        """Create a reflection after completing a task."""
        reflection = Reflection(task=task, outcome=outcome, **kwargs)
        self.reflections.append(reflection)
        self._save()
        logger.info(f"Reflected: {task[:40]} -> {outcome}")
        return reflection

    def suggest_improvements(self) -> List[str]:
        """Based on past reflections, suggest what to improve."""
        suggestions = []

        if not self.reflections:
            return ["Start by completing a task to get personalized suggestions"]

        # Analyze error patterns
        all_errors = []
        for r in self.reflections:
            all_errors.extend(r.errors_encountered)

        if all_errors:
            top_errors = set(all_errors[:5])
            suggestions.append(f"Watch out for: {', '.join(top_errors)}")

        # Analyze what works
        all_worked = []
        for r in self.reflections:
            if r.outcome == "success":
                all_worked.extend(r.what_worked)

        if all_worked:
            top_worked = set(all_worked[:3])
            suggestions.append(f"Keep doing: {', '.join(top_worked)}")

        # Overall stats
        successes = sum(1 for r in self.reflections if r.outcome == "success")
        total = len(self.reflections)
        if total > 0:
            suggestions.append(f"Success rate: {successes}/{total} ({successes*100//total}%)")

        # Improvements from past reflections
        all_improvements = []
        for r in self.reflections:
            all_improvements.extend(r.improvements)
        if all_improvements:
            suggestions.append(f"Try: {all_improvements[-1][:80]}")

        return suggestions

    def get_stats(self) -> dict:
        """Get reflection statistics."""
        if not self.reflections:
            return {"total": 0, "success_rate": 0}

        successes = sum(1 for r in self.reflections if r.outcome == "success")
        partials = sum(1 for r in self.reflections if r.outcome == "partial")
        failures = sum(1 for r in self.reflections if r.outcome == "failed")

        return {
            "total": len(self.reflections),
            "successes": successes,
            "partials": partials,
            "failures": failures,
            "success_rate": f"{successes * 100 // max(len(self.reflections), 1)}%",
            "avg_duration": sum(r.duration for r in self.reflections) / max(len(self.reflections), 1),
            "total_errors": sum(len(r.errors_encountered) for r in self.reflections),
        }

    def get_learning_curve(self) -> str:
        """Show how Hermes is improving over time."""
        if len(self.reflections) < 2:
            return "Not enough data for learning curve."

        # Split into first half and second half
        mid = len(self.reflections) // 2
        first_half = self.reflections[:mid]
        second_half = self.reflections[mid:]

        first_rate = sum(1 for r in first_half if r.outcome == "success") / max(len(first_half), 1)
        second_rate = sum(1 for r in second_half if r.outcome == "success") / max(len(second_half), 1)

        first_errors = sum(len(r.errors_encountered) for r in first_half)
        second_errors = sum(len(r.errors_encountered) for r in second_half)

        lines = [
            "=== Learning Curve ===",
            f"First {len(first_half)} tasks: {first_rate:.0%} success, {first_errors} errors",
            f"Last {len(second_half)} tasks: {second_rate:.0%} success, {second_errors} errors",
        ]

        if second_rate > first_rate:
            lines.append("Trend: Improving! 📈")
        elif second_rate < first_rate:
            lines.append("Trend: Declining 📉 - review what changed")
        else:
            lines.append("Trend: Stable")

        return "\n".join(lines)
