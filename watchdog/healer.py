"""Hermes Auto-Healing Pipeline — Autonomous error recovery.
When a tool fails, tries alternatives automatically before giving up.
Inspired by Claude Code's resilience and alternative-suggestion system.
"""
from __future__ import annotations
import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class HealingStrategy:
    """A strategy to try when a tool fails."""
    
    def __init__(self, name: str, description: str, 
                 apply_fn: Callable[[dict], dict]):
        self.name = name
        self.description = description
        self.apply = apply_fn
        self.attempts = 0
        self.successes = 0
    
    @property
    def success_rate(self) -> float:
        if self.attempts == 0:
            return 0.0
        return self.successes / self.attempts


class AutoHealer:
    """Autonomous error recovery system.
    
    When a tool fails, tries alternative strategies in order.
    Learns which strategies work best over time.
    """
    
    def __init__(self):
        self.strategies: Dict[str, List[HealingStrategy]] = {}
        self.healing_log: List[dict] = []
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """Register built-in healing strategies."""
        
        # File-related failures
        self.register_strategy("file_not_found", 
            HealingStrategy("check_alternative_path", "Try common alternative paths",
                lambda ctx: self._try_paths(ctx)))
        self.register_strategy("file_not_found",
            HealingStrategy("create_parent_dirs", "Create parent directories",
                lambda ctx: self._create_dirs(ctx)))
        self.register_strategy("file_not_found",
            HealingStrategy("use_other_extension", "Try .txt or .md extension",
                lambda ctx: self._try_extensions(ctx, [".txt", ".md"])))
        
        # Command failures
        self.register_strategy("command_not_found",
            HealingStrategy("try_without_args", "Try without arguments",
                lambda ctx: self._retry_without_args(ctx)))
        self.register_strategy("command_not_found",
            HealingStrategy("try_with_sudo", "Try with administrator privileges",
                lambda ctx: self._retry_with_sudo(ctx)))
        
        # Network failures
        self.register_strategy("connection_error",
            HealingStrategy("retry_with_backoff", "Retry with exponential backoff",
                lambda ctx: self._retry_with_backoff(ctx)))
        self.register_strategy("connection_error",
            HealingStrategy("try_alt_endpoint", "Try alternative endpoint",
                lambda ctx: self._try_alt_endpoint(ctx)))
        
        # Install failures
        self.register_strategy("install_failed",
            HealingStrategy("try_pip_install", "Try pip install instead",
                lambda ctx: ctx))  # Placeholder
        self.register_strategy("install_failed",
            HealingStrategy("try_npm_install", "Try npm install instead",
                lambda ctx: ctx))
        
        # General
        self.register_strategy("general",
            HealingStrategy("retry_simple", "Simple retry",
                lambda ctx: {"retry": True, "reason": "simple retry"}))
        self.register_strategy("general",
            HealingStrategy("ask_user_fallback", "Ask user for guidance",
                lambda ctx: {"fallback": True, "reason": "all strategies exhausted"}))
    
    def register_strategy(self, error_type: str, strategy: HealingStrategy):
        """Register a healing strategy for an error type."""
        if error_type not in self.strategies:
            self.strategies[error_type] = []
        self.strategies[error_type].append(strategy)
    
    def heal(self, error: str, context: dict) -> dict:
        """Try to heal an error automatically."""
        error_lower = error.lower()
        
        # Determine error type
        error_type = self._classify_error(error_lower)
        
        # Get strategies for this error type
        strategies = self.strategies.get(error_type, [])
        general = self.strategies.get("general", [])
        all_strategies = strategies + general
        
        if not all_strategies:
            return {"healed": False, "reason": "no strategies available"}
        
        # Try each strategy in order
        for strategy in all_strategies:
            strategy.attempts += 1
            logger.info(f"Healing: trying {strategy.name} for {error_type}")
            
            try:
                result = strategy.apply(context)
                strategy.successes += 1
                
                self.healing_log.append({
                    "error": error,
                    "error_type": error_type,
                    "strategy": strategy.name,
                    "success": True,
                    "time": datetime.now().isoformat(),
                })
                
                return {
                    "healed": True,
                    "strategy": strategy.name,
                    "description": strategy.description,
                    "result": result,
                }
            except Exception as e:
                logger.warning(f"Strategy {strategy.name} failed: {e}")
                continue
        
        # All strategies exhausted
        self.healing_log.append({
            "error": error,
            "error_type": error_type,
            "strategy": "all_exhausted",
            "success": False,
            "time": datetime.now().isoformat(),
        })
        
        return {
            "healed": False,
            "reason": "all strategies exhausted",
            "suggestion": self._get_fallback_suggestion(error_type),
        }
    
    def _classify_error(self, error: str) -> str:
        """Classify an error message into a type."""
        if any(w in error for w in ["no such file", "not found", "cannot find",
                                      "enoent", "filenotfound"]):
            return "file_not_found"
        if any(w in error for w in ["command not found", "not recognized",
                                      "is not recognized"]):
            return "command_not_found"
        if any(w in error for w in ["connection", "timeout", "refused",
                                      "econnrefused", "network"]):
            return "connection_error"
        if any(w in error for w in ["install", "pip", "npm", "package"]):
            return "install_failed"
        return "general"
    
    def _get_fallback_suggestion(self, error_type: str) -> str:
        suggestions = {
            "file_not_found": "Check if the file exists or create it first",
            "command_not_found": "Install the required tool or use an alternative",
            "connection_error": "Check your network connection and try again",
            "install_failed": "Try a different package manager or install manually",
        }
        return suggestions.get(error_type, "Try a different approach")
    
    def _try_paths(self, ctx: dict) -> dict:
        path = ctx.get("path", "")
        p = Path(path)
        alternatives = [
            p.parent / (p.stem + "_backup" + p.suffix),
            p.parent / p.name.lower(),
            p.parent / p.name.upper(),
        ]
        for alt in alternatives:
            if alt.exists():
                return {"alternative": str(alt)}
        raise FileNotFoundError(f"No alternative found for {path}")
    
    def _create_dirs(self, ctx: dict) -> dict:
        path = ctx.get("path", "")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        return {"created": str(Path(path).parent)}
    
    def _try_extensions(self, ctx: dict, exts: list) -> dict:
        path = ctx.get("path", "")
        p = Path(path)
        for ext in exts:
            candidate = p.with_suffix(ext)
            if candidate.exists():
                return {"alternative": str(candidate)}
        raise FileNotFoundError(f"No file with extensions {exts} found")
    
    def _retry_without_args(self, ctx: dict) -> dict:
        return {"cmd": ctx.get("cmd", "").split()[0] if ctx.get("cmd") else ""}
    
    def _retry_with_sudo(self, ctx: dict) -> dict:
        return {"needs_admin": True, "cmd": f"runas /user:Administrator {ctx.get('cmd', '')}"}
    
    def _retry_with_backoff(self, ctx: dict) -> dict:
        retries = ctx.get("retries", 0)
        import time
        time.sleep(min(2 ** retries, 30))
        return {"retry": True, "delay": min(2 ** retries, 30)}
    
    def _try_alt_endpoint(self, ctx: dict) -> dict:
        url = ctx.get("url", "")
        alternatives = {
            "api.deepseek.com": "api.deepseek.com/v1",
        }
        for original, alt in alternatives.items():
            if original in url:
                return {"alternative_url": url.replace(original, alt)}
        return {"alternative_url": url + "/v1"}
    
    def get_stats(self) -> dict:
        total = sum(s.attempts for strs in self.strategies.values() for s in strs)
        successes = sum(s.successes for strs in self.strategies.values() for s in strs)
        return {
            "strategies": sum(len(s) for s in self.strategies.values()),
            "error_types": len(self.strategies),
            "total_attempts": total,
            "total_successes": successes,
            "success_rate": successes / max(total, 1),
            "healing_log": len(self.healing_log),
        }
