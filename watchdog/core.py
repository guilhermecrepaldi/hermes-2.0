"""Hermes 2.0 — Dataclasses e tipos compartilhados."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RouterDecision:
    """Decisao do roteador S1/S2/S3."""
    shell: str          # "S1" | "S2" | "S3"
    model: str          # Nome do modelo LLM
    cost: str           # Descricao de custo
    reason: str         # Justificativa textual
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
    status: str = "pending"  # cloned | error | pending
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
