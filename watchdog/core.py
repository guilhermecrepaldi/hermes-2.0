"""Hermes 2.0 — Dataclasses, tipos compartilhados e harness."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import os
from datetime import datetime

# Get logger after possible setup (lazy import to avoid circular)
def _get_logger():
    try:
        from logger import get_logger
        return get_logger(__name__)
    except ImportError:
        import logging
        return logging.getLogger(__name__)


@dataclass
class RouterDecision:
    """Decisao do roteador S1/S2/S3."""
    shell: str
    model: str
    cost: str
    reason: str
    score_s1: int = 0
    score_s2: int = 0
    score_s3: int = 0

    def to_dict(self) -> dict:
        return {
            "shell": self.shell,
            "model": self.model,
            "cost": self.cost,
            "reason": self.reason,
            "score": {"S1": self.score_s1, "S2": self.score_s2, "S3": self.score_s3},
        }


@dataclass
class ProjectInfo:
    """Informacoes de um projeto carregado via s3_headroom."""
    path: str = ""
    name: str = ""
    status: str = "pending"
    error: str = ""
    total_files: int = 0
    total_lines: int = 0
    languages: dict = field(default_factory=dict)
    key_files: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "name": self.name,
            "status": self.status,
            "error": self.error,
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "languages": self.languages,
            "key_files": self.key_files,
        }


@dataclass
class ShellCapability:
    """Capacidade de uma shell (S1/S2/S3) para roteamento."""
    name: str
    keywords: list
    max_tokens: int = 4096
    model: str = ""
    cost: str = ""
    priority: int = 0


@dataclass
class Action:
    """Represents an action that can be executed by the agent."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    required_permissions: List[str] = field(default_factory=list)
    required_context: List[str] = field(default_factory=list)


@dataclass
class Context:
    """Current context of the agent session."""
    user_input: str = ""
    hermes_progress: str = ""
    available_skills: List[str] = field(default_factory=list)
    recent_actions: List[str] = field(default_factory=list)
    token_budget: int = 0
    working_directory: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class HarnessResult:
    """Result of executing an action through the harness."""
    success: bool
    summary: str
    data: Optional[Any] = None
    error: Optional[str] = None
    actions_taken: List[str] = field(default_factory=list)
    tokens_used: int = 0
    time_taken: float = 0.0


class SkillLoader:
    """Loads and manages available skills."""

    def __init__(self):
        self.skills: Dict[str, Any] = {}
        self._load_skills()

    def _load_skills(self) -> None:
        self.skills = {}

    def get_skill(self, name: str) -> Optional[Any]:
        return self.skills.get(name)

    def list_skills(self) -> List[str]:
        return list(self.skills.keys())


class HermesHarness:
    """Main harness: permissions, context, memory, and tool execution.
    Complexity lives here (Fable 5 inspired)."""

    def __init__(self):
        self.logger = _get_logger()
        self.skill_loader = SkillLoader()
        self.context = Context()
        self.permissions = self._load_default_permissions()
        self.tools = self._load_available_tools()

    def _load_default_permissions(self) -> Dict[str, bool]:
        return {
            "file_read": True, "file_write": True,
            "shell_execute": True, "network_access": True,
            "skill_execution": True,
        }

    def _load_available_tools(self) -> Dict[str, Any]:
        return {
            "terminal": {"description": "Shell commands", "permissions": ["shell_execute"]},
            "file_read": {"description": "Read files", "permissions": ["file_read"]},
            "file_write": {"description": "Write files", "permissions": ["file_write"]},
        }

    def update_context(self, user_input: str) -> None:
        self.context.user_input = user_input
        self.logger.debug(f"Context updated: {user_input[:50]}...")

    def choose_action(self, user_input: str) -> Action:
        user_lower = user_input.lower()
        if any(w in user_lower for w in ["pesquisar", "search", "find", "buscar"]):
            return Action(name="research", description="Pesquisar",
                          parameters={"query": user_input},
                          required_permissions=["network_access"])
        elif any(w in user_lower for w in ["criar", "create", "build", "make"]):
            return Action(name="create", description="Criar projeto",
                          parameters={"desc": user_input},
                          required_permissions=["file_write", "shell_execute"])
        elif any(w in user_lower for w in ["explicar", "explain", "como"]):
            return Action(name="explain", description="Explicar",
                          parameters={"topic": user_input})
        else:
            return Action(name="reason", description="Raciocinar",
                          parameters={"topic": user_input})

    def execute_action(self, action: Action, user_input: str) -> HarnessResult:
        if not self._validate_permissions(action):
            return HarnessResult(False, "Permissoes insuficientes",
                                 error="Insufficient permissions")
        if not self._validate_context(action):
            return HarnessResult(False, "Contexto insuficiente",
                                 error="Missing context")
        try:
            result = f"Acao {action.name} executada"
            return HarnessResult(True, result, data=result,
                                 actions_taken=[action.name])
        except Exception as e:
            self.logger.error(f"Erro: {e}")
            return HarnessResult(False, f"Erro: {e}", error=str(e))

    def _validate_permissions(self, action: Action) -> bool:
        for p in action.required_permissions:
            if not self.permissions.get(p, False):
                return False
        return True

    def _validate_context(self, action: Action) -> bool:
        return len(self.context.user_input) > 0

    def update_progress(self, result: HarnessResult) -> None:
        self.context.recent_actions.append(
            f"{datetime.now().isoformat()}: {result.summary}")
        if len(self.context.recent_actions) > 10:
            self.context.recent_actions = self.context.recent_actions[-10:]

    def handle_error(self, error: Exception) -> None:
        self.logger.error(f"Agent error: {error}", exc_info=True)
