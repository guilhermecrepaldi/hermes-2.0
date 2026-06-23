"""Hermes Orchestrator — Intelligent multi-agent coordination.
Manages parallel execution of subtasks with dependency awareness.
Inspired by Claude Code's subagent system.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class OrchestratedTask:
    """A task managed by the orchestrator."""
    id: str
    description: str
    action: str  # code | research | test | verify | document
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: str = ""
    error: str = ""
    started_at: str = ""
    finished_at: str = ""
    duration: float = 0.0
    retries: int = 0
    max_retries: int = 2


class Orchestrator:
    """Intelligent task orchestration with parallel execution.

    Takes a plan from TaskDecomposer, executes subtasks
    respecting dependencies, in parallel where possible.
    """

    def __init__(self):
        self.tasks: Dict[str, OrchestratedTask] = {}
        self.history: List[dict] = []
        self._running: set = set()
        self._done: set = set()

    def plan(self, tasks: List[dict]) -> None:
        """Load tasks into orchestrator from a plan."""
        for t in tasks:
            task = OrchestratedTask(
                id=t.get("id", f"T{len(self.tasks)+1}"),
                description=t.get("description", ""),
                action=t.get("type", "code"),
                dependencies=t.get("dependencies", []),
                max_retries=t.get("max_retries", 2),
            )
            self.tasks[task.id] = task

    def execute(self, executor: Optional[Callable] = None) -> List[OrchestratedTask]:
        """Execute all tasks respecting dependencies."""
        results = []

        while self._pending_tasks():
            # Find ready tasks
            ready = self._ready_tasks()

            if not ready:
                logger.warning("Deadlock detected: waiting tasks have unmet dependencies")
                break

            # Execute ready tasks (in parallel if executor supports it)
            for task in ready:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now().isoformat()
                self._running.add(task.id)

                start = time.time()
                try:
                    if executor:
                        result = executor(task)
                        task.result = str(result.get("result", ""))
                        task.status = TaskStatus.DONE
                    else:
                        task.status = TaskStatus.DONE
                        task.result = f"Task {task.id} completed"

                    self._done.add(task.id)
                    self._running.discard(task.id)
                    task.finished_at = datetime.now().isoformat()
                    task.duration = time.time() - start
                    results.append(task)

                    logger.info(f"Task {task.id} done ({task.duration:.1f}s)")

                except Exception as e:
                    task.retries += 1
                    if task.retries >= task.max_retries:
                        task.status = TaskStatus.FAILED
                        task.error = str(e)
                        self._running.discard(task.id)
                        results.append(task)
                        logger.warning(f"Task {task.id} failed after {task.retries} retries: {e}")
                    else:
                        task.status = TaskStatus.PENDING
                        self._running.discard(task.id)
                        logger.info(f"Task {task.id} will retry ({task.retries}/{task.max_retries})")

        # Record execution history
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "total": len(self.tasks),
            "done": sum(1 for t in self.tasks.values() if t.status == TaskStatus.DONE),
            "failed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
            "duration": sum(t.duration for t in self.tasks.values()),
        })

        return results

    def _pending_tasks(self) -> bool:
        return any(t.status == TaskStatus.PENDING for t in self.tasks.values())

    def _ready_tasks(self) -> List[OrchestratedTask]:
        """Find tasks whose dependencies are all satisfied."""
        return [
            t for t in self.tasks.values()
            if t.status == TaskStatus.PENDING
            and all(dep in self._done for dep in t.dependencies)
        ]

    def get_status(self) -> dict:
        """Get orchestrator status."""
        return {
            "total": len(self.tasks),
            "pending": sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
            "running": len(self._running),
            "done": sum(1 for t in self.tasks.values() if t.status == TaskStatus.DONE),
            "failed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED),
            "history": len(self.history),
        }

    def get_summary(self) -> str:
        """Get human-readable execution summary."""
        lines = ["=== Execution Summary ==="]
        for task in self.tasks.values():
            icon = {"done": "OK", "failed": "X", "running": "...",
                    "pending": "  ", "skipped": "-"}.get(task.status.value, "?")
            dur = f"({task.duration:.1f}s)" if task.duration else ""
            lines.append(f"  [{icon}] {task.id}: {task.description} {dur}")
            if task.error:
                lines.append(f"        Error: {task.error[:80]}")

        status = self.get_status()
        lines.append(f"\nDone: {status['done']}/{status['total']} | Failed: {status['failed']}")
        return "\n".join(lines)
