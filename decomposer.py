"""Hermes Task Decomposer — Automatic task breakdown.
Breaks complex tasks into smaller, executable subtasks.
Like Claude Code's automatic multi-step planning.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class SubTask:
    """A single subtask in a decomposed plan."""
    id: str
    description: str
    type: str  # code | research | test | verify | document | config
    dependencies: List[str] = field(default_factory=list)
    estimated_effort: str = "medium"  # small | medium | large
    status: str = "pending"  # pending | running | done | failed
    result: str = ""
    max_retries: int = 2
    retries: int = 0

    def can_run(self, done_ids: set) -> bool:
        """Check if all dependencies are met."""
        return all(dep in done_ids for dep in self.dependencies)


@dataclass
class TaskPlan:
    """A complete task decomposition plan."""
    original: str
    subtasks: List[SubTask] = field(default_factory=list)
    created_at: str = ""
    parallel_groups: List[List[str]] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class TaskDecomposer:
    """Automatically breaks complex tasks into executable subtasks.

    Analyzes the task, identifies the key steps,
    creates dependency-aware execution plan.
    """

    def __init__(self):
        self.plans: List[TaskPlan] = []

    def decompose(self, task: str) -> TaskPlan:
        """Break a complex task into subtasks."""
        task_lower = task.lower()

        # Analyze task type
        if self._is_coding_task(task_lower):
            plan = self._decompose_code_task(task)
        elif self._is_research_task(task_lower):
            plan = self._decompose_research_task(task)
        elif self._is_setup_task(task_lower):
            plan = self._decompose_setup_task(task)
        elif self._is_analysis_task(task_lower):
            plan = self._decompose_analysis_task(task)
        else:
            plan = self._decompose_general_task(task)

        # Identify parallel groups
        plan.parallel_groups = self._find_parallel_groups(plan.subtasks)

        self.plans.append(plan)
        logger.info(f"Decomposed: {task[:50]} -> {len(plan.subtasks)} subtasks")
        return plan

    def _is_coding_task(self, task: str) -> bool:
        return any(w in task for w in ["criar", "create", "build", "implement",
                                        "function", "class", "api", "endpoint",
                                        "refactor", "fix", "debug", "bug"])

    def _is_research_task(self, task: str) -> bool:
        return any(w in task for w in ["pesquisar", "research", "find",
                                        "search", "study", "learn", "understand"])

    def _is_setup_task(self, task: str) -> bool:
        return any(w in task for w in ["setup", "install", "configure", "init",
                                        "start", "create project", "new project"])

    def _is_analysis_task(self, task: str) -> bool:
        return any(w in task for w in ["analyze", "review", "audit", "check",
                                        "verify", "validate", "test"])

    def _decompose_code_task(self, task: str) -> TaskPlan:
        return TaskPlan(
            original=task,
            subtasks=[
                SubTask("S1", "Analyze requirements and constraints", "analyze"),
                SubTask("S2", "Plan implementation approach", "document", dependencies=["S1"]),
                SubTask("S3", "Write implementation", "code", dependencies=["S2"]),
                SubTask("S4", "Add type hints and documentation", "document", dependencies=["S3"]),
                SubTask("S5", "Write tests", "test", dependencies=["S3"]),
                SubTask("S6", "Verify and validate", "verify", dependencies=["S4", "S5"]),
            ]
        )

    def _decompose_research_task(self, task: str) -> TaskPlan:
        return TaskPlan(
            original=task,
            subtasks=[
                SubTask("S1", "Define research scope and questions", "analyze"),
                SubTask("S2", "Search for relevant information", "research", dependencies=["S1"]),
                SubTask("S3", "Analyze and synthesize findings", "analyze", dependencies=["S2"]),
                SubTask("S4", "Document conclusions", "document", dependencies=["S3"]),
            ]
        )

    def _decompose_setup_task(self, task: str) -> TaskPlan:
        return TaskPlan(
            original=task,
            subtasks=[
                SubTask("S1", "Check prerequisites", "analyze"),
                SubTask("S2", "Create project structure", "config", dependencies=["S1"]),
                SubTask("S3", "Install dependencies", "config", dependencies=["S2"]),
                SubTask("S4", "Configure tools", "config", dependencies=["S3"]),
                SubTask("S5", "Verify setup works", "verify", dependencies=["S4"]),
            ]
        )

    def _decompose_analysis_task(self, task: str) -> TaskPlan:
        return TaskPlan(
            original=task,
            subtasks=[
                SubTask("S1", "Identify what to analyze", "analyze"),
                SubTask("S2", "Run analysis checks", "research", dependencies=["S1"]),
                SubTask("S3", "Compile findings", "document", dependencies=["S2"]),
                SubTask("S4", "Generate recommendations", "document", dependencies=["S3"]),
            ]
        )

    def _decompose_general_task(self, task: str) -> TaskPlan:
        return TaskPlan(
            original=task,
            subtasks=[
                SubTask("S1", "Understand the request", "analyze"),
                SubTask("S2", "Plan the approach", "document", dependencies=["S1"]),
                SubTask("S3", "Execute the plan", "code", dependencies=["S2"]),
                SubTask("S4", "Verify the result", "verify", dependencies=["S3"]),
            ]
        )

    def _find_parallel_groups(self, subtasks: List[SubTask]) -> List[List[str]]:
        """Find subtasks that can run in parallel."""
        done = set()
        groups = []
        remaining = {s.id for s in subtasks}

        while remaining:
            # Find tasks whose deps are all satisfied
            ready = [s for s in subtasks if s.id in remaining and
                     all(d in done for d in s.dependencies)]
            if not ready:
                # Break dependency cycles
                ready = [subtasks[0]]

            group = [s.id for s in ready]
            groups.append(group)
            for r in ready:
                done.add(r.id)
                remaining.discard(r.id)

        return groups

    def get_plan_summary(self, plan: TaskPlan) -> str:
        """Get a human-readable plan summary."""
        lines = [
            f"Task: {plan.original[:80]}",
            f"Subtasks: {len(plan.subtasks)}",
            f"Parallel groups: {len(plan.parallel_groups)}",
            "",
        ]

        for i, group in enumerate(plan.parallel_groups):
            lines.append(f"Group {i+1}:")
            for subtask_id in group:
                st = next(s for s in plan.subtasks if s.id == subtask_id)
                icon = {"analyze": "🔍", "code": "💻", "test": "🧪",
                       "verify": "✅", "document": "📝", "research": "📚",
                       "config": "⚙️"}.get(st.type, "•")
                lines.append(f"  {icon} {st.id}: {st.description} [{st.estimated_effort}]")

        return "\n".join(lines)

    def get_stats(self) -> dict:
        return {
            "total_plans": len(self.plans),
            "total_subtasks": sum(len(p.subtasks) for p in self.plans),
        }
