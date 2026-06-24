#!/usr/bin/env python3
"""Hermes Delegator — Shellz: S3 (DeepSeek) delega para S1 (Ollama).
S3 = cerebro principal. Recebe a task, processa, delega subtarefas.
S1 = trabalhador local. Compilacoes, LoC, execucao de codigo.
Toda delegacao registrada na telemetria com custo real.
"""
from __future__ import annotations
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

try:
    from telemetry import telemetry, estimate_cost
    HAS_TELEMETRY = True
except ImportError:
    HAS_TELEMETRY = False

try:
    from logger_pro import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# ─── TIPOS DE TAREFA QUE S1 PODE EXECUTAR ─────

S1_CAPABILITIES = [
    "compilar", "compilation", "build",
    "executar", "run", "rodar",
    "linha de comando", "shell", "terminal",
    "loc", "lines of code", "contar linhas",
    "teste unitario", "pytest", "unit test",
    "formatar", "format", "lint",
    "listar diretorio", "ls", "dir",
    "git status", "git diff", "git log",
    "git add", "git commit", "git push", "git pull",
    "git clone", "git checkout", "git branch",
    "instalar pacote", "pip install", "npm install",
    "cpu", "memoria", "disk", "processo",
]


def tarefa_para_s1(user_input: str) -> bool:
    """Verifica se a tarefa pode ser delegada para S1 (Ollama local)."""
    lower = user_input.lower()
    for kw in S1_CAPABILITIES:
        if kw in lower:
            return True
    return False


@dataclass
class DelegationDecision:
    shell: str       # S3 (DeepSeek) ou S1 (Ollama)
    role: str        # "main" (S3 recebeu a task) | "worker" (S1 executa)
    model: str
    provider: str
    reason: str
    token_estimate: int = 0  # Tokens estimados para esta subtarefa
    cost_per_1m: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "shell": self.shell,
            "role": self.role,
            "model": self.model,
            "provider": self.provider,
            "reason": self.reason,
            "cost_per_1m": self.cost_per_1m,
        }


S3 = {"model": "deepseek-v4-flash", "provider": "deepseek", "cost_per_1m": 0.30}
S1 = {"model": "qwen2.5-coder:7b", "provider": "ollama", "cost_per_1m": 0.0}


class Delegator:
    """Shellz: S3 (DeepSeek) como main. S1 (Ollama) como worker.
    
    Fluxo:
    1. S3 recebe a task do usuario (main intelligence)
    2. S3 identifica subtarefas compilaveis/loc
    3. S1 executa as subtarefas (worker local, $0)
    4. Telemetria registra consumo de ambos
    
    Uso:
        d = Delegator()
        
        # Task principal vai para S3 (DeepSeek)
        dec = d.delegar("criar API", funcao="main")
        # dec.shell = "S3", dec.role = "main"
        
        # Subtarefa vai para S1 (Ollama)
        dec = d.delegar("compilar projeto", funcao="worker")
        # dec.shell = "S1", dec.role = "worker"
    """
    
    def __init__(self):
        self._stats = {
            "sessoes_s3": 0,      # Sessoes no DeepSeek (main)
            "delegacoes_s1": 0,   # Delegacoes para Ollama (worker)
            "total_tokens_s3": 0,
            "total_tokens_s1": 0,
            "total_cost_s3": 0.0,
            "total_cost_s1": 0.0,
            "total_cost": 0.0,
        }
    
    def delegar(self, user_input: str, funcao: str = "main",
                tokens: int = 0) -> DelegationDecision:
        """Delega uma tarefa.
        
        Args:
            user_input: A tarefa a ser delegada
            funcao: "main" (S3 recebeu do usuario) | "worker" (S1 executa)
            tokens: Tokens estimados para calculo de custo
        
        Returns:
            DelegationDecision com shell escolhido
        """
        if funcao == "worker" or tarefa_para_s1(user_input):
            # Vai para S1 (Ollama local, $0)
            decision = DelegationDecision(
                shell="S1",
                role="worker",
                model=S1["model"],
                provider=S1["provider"],
                reason="Tarefa compativel com S1 (worker local)",
                cost_per_1m=S1["cost_per_1m"],
            )
            self._stats["delegacoes_s1"] += 1
            self._stats["total_tokens_s1"] += tokens
        else:
            # Vai para S3 (DeepSeek, main)
            decision = DelegationDecision(
                shell="S3",
                role="main",
                model=S3["model"],
                provider=S3["provider"],
                reason="Task principal (S3, inteligencia principal)",
                cost_per_1m=S3["cost_per_1m"],
            )
            self._stats["sessoes_s3"] += 1
            self._stats["total_tokens_s3"] += tokens
        
        cost = estimate_cost(decision.provider, tokens, tokens // 2)
        self._stats["total_cost"] += cost
        if decision.provider == "ollama":
            self._stats["total_cost_s1"] += cost
        else:
            self._stats["total_cost_s3"] += cost
        
        # Registra na telemetria
        if HAS_TELEMETRY:
            telemetry.record(
                user_input=user_input,
                action_taken=f"delegar:{funcao}",
                shell_used=decision.shell,
                model_used=decision.model,
                provider=decision.provider,
                total_tokens=tokens,
                cost=cost,
            )
        
        logger.info(f"[{decision.shell}] {funcao}: {user_input[:60]}... | "
                     f"modelo={decision.model} custo=${cost:.6f}")
        
        return decision
    
    def get_stats(self) -> dict:
        """Estatisticas de delegacao."""
        return dict(self._stats)
    
    def reset_stats(self):
        """Reseta contadores."""
        self._stats = {
            "sessoes_s3": 0,
            "delegacoes_s1": 0,
            "total_tokens_s3": 0,
            "total_tokens_s1": 0,
            "total_cost_s3": 0.0,
            "total_cost_s1": 0.0,
            "total_cost": 0.0,
        }


# Instancia global
delegator = Delegator()
