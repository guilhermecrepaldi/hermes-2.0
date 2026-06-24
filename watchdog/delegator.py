#!/usr/bin/env python3
"""Hermes Delegator — Delegacao inteligente de tarefas.
S1_local (Ollama/gratis) para tarefas simples.
S2_cheap (DeepSeek) apenas para analise complexa.
Toda delegacao registrada na telemetria.
"""
from __future__ import annotations
import json
import os
import time
from typing import Optional, Dict, Any
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


# Complexidade estimada baseada no input
def estimate_complexity(user_input: str) -> int:
    """Estima complexidade de 1 (simples) a 10 (complexo).
    
    Regras:
    - < 50 chars: simples (1-3)
    - 50-200 chars: medio (4-6)
    - > 200 chars: complexo (7-10)
    - Palavras-chave de analise: +2
    - Palavras-chave de codigo: +1
    """
    length = len(user_input)
    
    if length < 50:
        base = 2
    elif length < 100:
        base = 4
    elif length < 200:
        base = 6
    else:
        base = 8
    
    # Palavras que indicam complexidade
    complex_keywords = [
        "analisar", "analise", "analise", "comparar", "comparacao",
        "relatorio", "report", "dashboard", "grafico", "chart",
        "arquitetura", "architecture", "design", "projetar",
        "otimizar", "optimize", "refatorar", "refactor",
        "deploy", "publicar", "release",
        "seguranca", "security", "vulnerabilidade",
    ]
    simple_keywords = [
        "listar", "ls", "cat", "echo", "print",
        "hello", "oi", "ola", "bom dia", "boa tarde",
        "como", "onde", "quem", "what", "who",
    ]
    
    lower = user_input.lower()
    for kw in complex_keywords:
        if kw in lower:
            base += 2
    
    for kw in simple_keywords:
        if kw in lower:
            base -= 1
    
    return max(1, min(10, base))


@dataclass
class DelegationDecision:
    shell: str  # S1_local | S2_cheap | S3_premium
    model: str
    provider: str
    reason: str
    complexity: int = 1
    cost_per_1m: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "shell": self.shell,
            "model": self.model,
            "provider": self.provider,
            "reason": self.reason,
            "complexity": self.complexity,
            "cost_per_1m": self.cost_per_1m,
        }


class Delegator:
    """Delegador inteligente que decide onde executar cada tarefa.
    
    Regras:
    - Complexity 1-5: S1_local (Ollama, $0)
    - Complexity 6-8: S2_cheap (DeepSeek, ~$0.30/M)
    - Complexity 9-10: S3_premium (GPT/Claude, ~$12/M)
    """
    
    # Modelos disponiveis por shell
    SHELLS = {
        "S1_local": {
            "model": "qwen2.5-coder:7b",
            "provider": "ollama",
            "cost_per_1m": 0.0,
            "max_complexity": 5,
        },
        "S2_cheap": {
            "model": "deepseek-v4-flash",
            "provider": "deepseek",
            "cost_per_1m": 0.30,
            "max_complexity": 8,
        },
        "S3_premium": {
            "model": "claude-sonnet-4",
            "provider": "anthropic",
            "cost_per_1m": 12.0,
            "max_complexity": 10,
        },
    }
    
    def __init__(self):
        self._stats = {
            "total_delegations": 0,
            "by_shell": {"S1_local": 0, "S2_cheap": 0, "S3_premium": 0},
            "total_tokens": 0,
            "total_cost": 0.0,
        }
    
    def decide(self, user_input: str) -> DelegationDecision:
        """Decide qual shell usar para esta tarefa."""
        complexity = estimate_complexity(user_input)
        
        if complexity <= 5:
            shell = "S1_local"
            reason = f"Tarefa simples (complexidade {complexity}/10)"
        elif complexity <= 8:
            shell = "S2_cheap"
            reason = f"Tarefa media (complexidade {complexity}/10)"
        else:
            shell = "S3_premium"
            reason = f"Tarefa complexa (complexidade {complexity}/10)"
        
        cfg = self.SHELLS[shell]
        
        return DelegationDecision(
            shell=shell,
            model=cfg["model"],
            provider=cfg["provider"],
            reason=reason,
            complexity=complexity,
            cost_per_1m=cfg["cost_per_1m"],
        )
    
    def delegar(self, user_input: str, funcao: str = "processar",
                tokens_input: int = 0, tokens_output: int = 0) -> DelegationDecision:
        """Delega uma tarefa e registra na telemetria.
        
        Args:
            user_input: O input do usuario
            funcao: Nome da funcao sendo executada
            tokens_input: Tokens de entrada (opcional, para calculo de custo)
            tokens_output: Tokens de saida (opcional, para calculo de custo)
        
        Returns:
            DelegationDecision com shell escolhido
        """
        decision = self.decide(user_input)
        
        # Calcula custo estimado
        cost = estimate_cost(decision.provider, tokens_input, tokens_output)
        
        # Registra na telemetria
        if HAS_TELEMETRY:
            telemetry.record(
                user_input=user_input,
                action_taken=f"delegar:{funcao}",
                shell_used=decision.shell,
                model_used=decision.model,
                provider=decision.provider,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                total_tokens=tokens_input + tokens_output,
                cost=cost,
                complexity=decision.complexity,
            )
        
        # Atualiza estatisticas
        self._stats["total_delegations"] += 1
        self._stats["by_shell"][decision.shell] =             self._stats["by_shell"].get(decision.shell, 0) + 1
        self._stats["total_tokens"] += tokens_input + tokens_output
        self._stats["total_cost"] += cost
        
        logger.info(f"Delegado para {decision.shell} ({decision.model}): "
                     f"{decision.reason} | custo ${cost:.6f}")
        
        return decision
    
    def get_stats(self) -> dict:
        """Estatisticas de delegacao."""
        return dict(self._stats)
    
    def reset_stats(self):
        """Reseta contadores."""
        self._stats = {
            "total_delegations": 0,
            "by_shell": {"S1_local": 0, "S2_cheap": 0, "S3_premium": 0},
            "total_tokens": 0,
            "total_cost": 0.0,
        }


# Instancia global
delegator = Delegator()
