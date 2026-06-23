"""Hermes Reasoning Engine — Structured thinking for complex tasks.
Inspired by Claude's chain-of-thought and reasoning capabilities.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class ReasoningStep:
    """A single step in the reasoning chain."""
    id: int
    type: str  # think | analyze | plan | execute | verify
    content: str
    result: str = ""
    confidence: float = 0.0
    duration: float = 0.0


@dataclass
class Thought:
    """A reasoning thought or insight."""
    content: str
    type: str = "insight"  # insight | question | assumption | decision
    confidence: float = 0.5
    source: str = ""


@dataclass
class Decision:
    """A decision made during reasoning."""
    choice: str
    alternatives: List[str] = field(default_factory=list)
    reasoning: str = ""
    confidence: float = 0.0
    timestamp: str = ""


class ReasoningEngine:
    """Structured reasoning for complex tasks."""

    def __init__(self):
        self.steps: List[ReasoningStep] = []
        self.thoughts: List[Thought] = []
        self.decisions: List[Decision] = []
        self._start_time = datetime.now()

    def think(self, content: str) -> ReasoningStep:
        """Add a thinking step."""
        step = ReasoningStep(
            id=len(self.steps) + 1,
            type="think",
            content=content
        )
        self.steps.append(step)
        return step

    def analyze(self, content: str) -> ReasoningStep:
        """Analyze a problem or situation."""
        step = ReasoningStep(
            id=len(self.steps) + 1,
            type="analyze",
            content=content
        )
        self.steps.append(step)
        return step

    def plan(self, steps: List[str]) -> ReasoningStep:
        """Create a structured plan."""
        content = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
        step = ReasoningStep(
            id=len(self.steps) + 1,
            type="plan",
            content=content
        )
        self.steps.append(step)
        return step

    def verify(self, criteria: Dict[str, bool]) -> ReasoningStep:
        """Verify results against criteria."""
        passed = sum(1 for v in criteria.values() if v)
        total = len(criteria)
        content = "\n".join(f"[{'OK' if v else 'X'}] {k}" for k, v in criteria.items())
        step = ReasoningStep(
            id=len(self.steps) + 1,
            type="verify",
            content=content,
            result=f"{passed}/{total} checks passed",
            confidence=passed / max(total, 1)
        )
        self.steps.append(step)
        return step

    def decide(self, choice: str, alternatives: List[str],
               reasoning: str, confidence: float = 0.0) -> Decision:
        """Make a reasoned decision."""
        decision = Decision(
            choice=choice,
            alternatives=alternatives,
            reasoning=reasoning,
            confidence=confidence or (1.0 / max(len(alternatives) + 1, 1)),
            timestamp=datetime.now().isoformat()
        )
        self.decisions.append(decision)

        step = ReasoningStep(
            id=len(self.steps) + 1,
            type="decide",
            content=f"Chose: {choice}\nReason: {reasoning}\nConfidence: {decision.confidence:.0%}"
        )
        self.steps.append(step)
        return decision

    def add_insight(self, content: str, confidence: float = 0.5) -> Thought:
        """Add an insight."""
        thought = Thought(content=content, type="insight", confidence=confidence)
        self.thoughts.append(thought)
        return thought

    def summarize(self) -> str:
        """Summarize the reasoning chain."""
        if not self.steps:
            return "No reasoning steps."

        lines = ["=== Reasoning Chain ==="]
        for step in self.steps:
            icon = {"think": "🧠", "analyze": "🔍",
                    "plan": "📋", "verify": "✅", "decide": "🎯"}
            icon_char = icon.get(step.type, "▶")
            lines.append(f"{icon_char} Step {step.id} ({step.type}): {step.content[:100]}")

        if self.decisions:
            lines.append(f"\n=== Decisions ({len(self.decisions)}) ===")
            for d in self.decisions:
                lines.append(f"  - {d.choice} (confidence: {d.confidence:.0%})")

        if self.thoughts:
            lines.append(f"\n=== Insights ({len(self.thoughts)}) ===")
            for t in self.thoughts[-3:]:  # Last 3
                lines.append(f"  - {t.content[:120]}")

        return "\n".join(lines)

    def get_stats(self) -> dict:
        return {
            "steps": len(self.steps),
            "thoughts": len(self.thoughts),
            "decisions": len(self.decisions),
            "duration": (datetime.now() - self._start_time).total_seconds(),
            "types": {t: sum(1 for s in self.steps if s.type == t) for t in ["think", "analyze", "plan", "verify", "decide"]}
        }
