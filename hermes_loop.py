#!/usr/bin/env python3
"""
Hermes Agent Loop — Fable 5 inspired.
<20 linhas de orquestracao pura. >80% da complexidade no harness e engine.
"""
from __future__ import annotations
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "watchdog"))

from core import HermesHarness
from engine import (
    carregar_progresso, salvar_progresso, HookManager,
    CheckpointManager, InitializerAgent, CodingAgent
)
from logger import get_logger

logger = get_logger(__name__)


class HermesLoop:
    """Agent loop (<20 linhas de logica)."""

    def __init__(self):
        self.harness = HermesHarness()
        self.running = True
        HookManager.setup_default()
        CheckpointManager.auto_compact()
        logger.info("Hermes Agent Loop + Engine OK")

    def run(self) -> None:
        print("\U0001f680 Hermes Agent Loop v0.2 (Fable 5)")
        while self.running:
            try:
                user_input = self._get_input()
                if not user_input or user_input.strip().lower() in ('exit', 'quit'):
                    self._handle_exit()
                    break
                if not user_input.strip():
                    continue

                self.harness.update_context(user_input)
                salvar_progresso("INPUT", user_input[:40])

                # Context Engineering: load progress primeiro
                ctx = carregar_progresso()
                self.harness.context.hermes_progress = str(ctx.get("feito", []))

                # Choose + execute via harness
                action = self.harness.choose_action(user_input)
                result = self.harness.execute_action(action, user_input)
                self.harness.update_progress(result)

                salvar_progresso(action.name, result.summary[:80])
                self._display_result(result)

                # Auto-checkpoint a cada 5 acoes
                if len(self.harness.context.recent_actions) % 5 == 0:
                    CheckpointManager.save()

            except KeyboardInterrupt:
                self._handle_exit()
                break
            except Exception as e:
                logger.error(f"Loop error: {e}", exc_info=True)
                self.harness.handle_error(e)
                print(f"\u274c Erro: {e}")

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
        print(f"\n\U0001f44b Ate logo!")

    def _display_result(self, result) -> None:
        if hasattr(result, 'summary'):
            print(f"\u2705 {result.summary}")
        elif isinstance(result, dict):
            print(f"\u2705 {result.get('summary', str(result))}")
        elif result:
            print(f"\u2705 {result}")


def main() -> None:
    HermesLoop().run()


if __name__ == "__main__":
    main()
