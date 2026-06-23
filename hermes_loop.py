#!/usr/bin/env python3
"""Hermes Agent Loop v1.0 — Fully autonomous end-to-end.
Integrates all intelligence modules: reasoning, orchestrator,
auto-healer, proactive scanner, semantic memory, self-reflection.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "watchdog"))

from compactor import compact_conversation, get_compact_stats
from core import HermesHarness
from engine import CheckpointManager, HookManager, salvar_progresso
from healer import AutoHealer
from intelligence import ProjectScanner
from logger_pro import setup_hermes_logging
from logger import get_logger
from orchestrator import Orchestrator
from proactive import ProactiveAnalyzer
from reasoning import ReasoningEngine
from reflector import Reflector
from smemory import SemanticMemory

logger = get_logger(__name__)


class HermesLoop:
    """Agent loop with full intelligence integration."""

    def __init__(self):
        self.harness = HermesHarness()
        self.reasoning = ReasoningEngine()
        self.healer = AutoHealer()
        self.memory = SemanticMemory()
        self.reflector = Reflector()
        self.scanner = ProjectScanner(str(Path(__file__).resolve().parent))
        self.proactive = ProactiveAnalyzer(str(Path(__file__).resolve().parent))
        self.orch = Orchestrator()
        self.running = True
        self.task_count = 0
        self.conversation = []

        HookManager.setup_default()
        setup_hermes_logging()
        CheckpointManager.auto_compact()

        self._auto_init()
        logger.info("Hermes v1.0 — fully autonomous")

    def _auto_init(self):
        """Auto-initialize: scan project, load context, check health."""
        # Scan project autonomously
        self.scanner.scan()
        ctx = self.scanner.get_summary()
        logger.info(f"Project: {ctx[:80]}")

        # Check past reflections for improvement suggestions
        suggestions = self.reflector.suggest_improvements()
        if suggestions:
            logger.info(f"Self-improvement: {suggestions[0]}")

        # Proactive scan for issues
        issues = self.proactive.scan_all()
        if issues:
            logger.info(f"Proactive: {len(issues)} suggestions found")

        # Load semantic memory for context
        mem = self.memory.recall("context task help", max_results=3)
        if mem:
            logger.info(f"Memory: {len(mem)} relevant past learnings")

    def run(self) -> None:
        print("Hermes v1.0 — Autonomous Agent")
        print(f"  Project: {self.scanner.root.name}")
        print(f"  Memory: {self.memory.get_stats()['total']} entries")

        while self.running:
            try:
                user_input = self._get_input()
                if not user_input or user_input.strip().lower() in ("exit", "quit"):
                    self._handle_exit()
                    break
                if not user_input.strip():
                    continue

                self.task_count += 1
                self.conversation.append({"role": "user", "content": user_input})

                # 1. Context engineering
                self.harness.update_context(user_input)
                salvar_progresso("INPUT", user_input[:40])

                # 2. Check semantic memory for past learnings
                past = self.memory.recall(user_input[:50], max_results=2)
                if past:
                    logger.info(f"Memory recall: {past[0].content[:60]}...")

                # 3. Use reasoning engine for complex tasks
                self.reasoning.think(f"Task: {user_input[:80]}")

                # 4. Choose and execute action (with auto-healing)
                action = self.harness.choose_action(user_input)
                result = self.harness.execute_action(action, user_input)

                # 5. Auto-heal if failed
                if hasattr(result, 'success') and not result.success:
                    healed = self.healer.heal(
                        getattr(result, 'error', '') or str(result),
                        {"input": user_input}
                    )
                    if healed.get("healed"):
                        logger.info(f"Auto-healed: {healed.get('strategy')}")
                        result = self.harness.execute_action(action, user_input + " [retry]")
                    else:
                        self.memory.remember_error(
                            getattr(result, 'error', 'unknown'),
                            healed.get("suggestion", "try different approach")
                        )

                self.harness.update_progress(result)
                salvar_progresso(action.name, str(getattr(result, 'summary', ''))[:80])
                self._display_result(result)

                # 6. Store outcome in semantic memory
                if hasattr(result, 'success') and result.success:
                    self.memory.remember_success(action.name, str(getattr(result, 'summary', ''))[:60])

                # 7. Auto-checkpoint
                if self.task_count % 5 == 0:
                    CheckpointManager.save()
                    # Self-reflection every 5 tasks
                    self.reflector.reflect(
                        task=user_input[:60],
                        outcome="success" if getattr(result, 'success', True) else "failed",
                        steps_taken=self.task_count,
                    )

                self.conversation.append({"role": "assistant", "content": str(getattr(result, 'summary', ''))})

                # 8. Auto-compaction if needed
                if self.task_count > 3 and self.task_count % 5 == 0:
                    " ".join(m.get("content", "") for m in self.conversation)
                    if get_compact_stats().get("total_compactions", 0) < len(self.conversation):
                        self.conversation = compact_conversation(self.conversation)
                        logger.info("Conversation compacted")

            except KeyboardInterrupt:
                self._handle_exit()
                break
            except Exception as e:
                logger.error(f"Loop: {e}", exc_info=True)
                # Try auto-heal for loop errors
                healed = self.healer.heal(str(e), {"error": str(e)})
                if not healed.get("healed"):
                    print(f"Error: {e}")

    def _get_input(self) -> str:
        try:
            if not sys.stdin.isatty():
                return sys.stdin.read()
            return input("hermes> ")
        except EOFError:
            return ""

    def _handle_exit(self) -> None:
        self.running = False
        CheckpointManager.save("exit")
        # Final reflection
        stats = self.reflector.get_stats()
        print(f"\nSessions: {stats.get('total', 0)} | Success: {stats.get('success_rate', 'N/A')}")
        print("Bye!")

    def _display_result(self, result) -> None:
        if hasattr(result, 'summary'):
            print(f"  {result.summary}")
        elif isinstance(result, dict):
            print(f"  {result.get('summary', str(result))}")
        elif result:
            print(f"  {result}")


def main() -> None:
    HermesLoop().run()


if __name__ == "__main__":
    main()
