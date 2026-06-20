#!/usr/bin/env python3
"""
Hermes Agent Loop - Inspired by Fable 5 (Claude Code)
Simple while loop that orchestrates everything through skills and harness.
Less than 50 lines of orchestration. All complexity in the harness.
"""
from __future__ import annotations
import sys
import os

# Ensure watchdog directory is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "watchdog"))

from core import HermesHarness
from logger import get_logger

logger = get_logger(__name__)


class HermesLoop:
    """Agent loop inspired by Fable 5. Loop is simple, harness is complex."""
    
    def __init__(self):
        self.harness = HermesHarness()
        self.running = True
        logger.info("Hermes Agent Loop initialized")
    
    def run(self) -> None:
        """Main agent loop - approximately 20 lines of pure orchestration."""
        print("\U0001f680 Hermes Agent Loop started (Fable 5 inspired)")
        print("   Type your request or 'exit' to quit")
        
        while self.running:
            try:
                # 1. Get input
                user_input = self._get_input()
                if not user_input or user_input.strip().lower() in ['exit', 'quit']:
                    self._handle_exit()
                    break
                if not user_input.strip():
                    continue
                
                # 2. Update context with input
                self.harness.update_context(user_input)
                
                # 3. Choose next action based on context and skills
                action = self.harness.choose_action(user_input)
                
                # 4. Validate and execute action through harness
                result = self.harness.execute_action(action, user_input)
                
                # 5. Update progress tracking
                self.harness.update_progress(result)
                self._display_result(result)
                
            except KeyboardInterrupt:
                self._handle_exit()
                break
            except Exception as e:
                logger.error(f"Agent loop error: {e}", exc_info=True)
                self.harness.handle_error(e)
                print(f"\u274c Erro: {e}")
    
    def _get_input(self) -> str:
        """Get input from user."""
        try:
            if not sys.stdin.isatty():
                return sys.stdin.read()
            return input("hermes> ")
        except EOFError:
            return ""
    
    def _handle_exit(self) -> None:
        self.running = False
        print("\n\U0001f44b Ate logo!")
        logger.info("Agent loop terminated")
    
    def _display_result(self, result) -> None:
        if hasattr(result, 'summary'):
            print(f"\u2705 {result.summary}")
        elif isinstance(result, dict) and 'summary' in result:
            print(f"\u2705 {result['summary']}")
        elif result:
            print(f"\u2705 {result}")


def main() -> None:
    loop = HermesLoop()
    loop.run()


if __name__ == "__main__":
    main()
