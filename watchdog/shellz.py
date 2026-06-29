#!/usr/bin/env python3
"""Shellz — Sistema PERMANENTE de delegacao S3 + S1.
AUTOMATICO. OBRIGATORIO. ETERNO. Na raiz, no core.
NUNCA desligar. NUNCA modificar comportamento.

Arquitetura:
  S3 (DeepSeek) = cerebro principal, recebe a task
  S1 (Ollama)   = trabalhador local, compilacoes/LoC/exec

Toda interacao passa por aqui. Tudo registrado na telemetria.
"""
from __future__ import annotations
import sys
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass

# ─── ENV OBRIGATORIA — IA local SEMPRE que possivel
FORCE_LOCAL = os.environ.get("HERMES_FORCE_LOCAL_PROCESSING", "0") == "1"
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5-coder:7b")

# ─── IMPORTS OBRIGATORIOS — NUNCA falham ────────

HAS_TELEMETRY = False
HAS_LOGGER = False
HAS_HEADROOM = False

try:
    from telemetry import telemetry, estimate_cost
    HAS_TELEMETRY = True
except ImportError:
    pass

try:
    from headroom_bridge import compress_messages, doctor as headroom_doctor
    HAS_HEADROOM = True
except ImportError:
    pass

try:
    from logger_pro import get_logger
    logger = get_logger(__name__)
    HAS_LOGGER = True
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


# ─── S1 CAPABILITIES — expandir conforme necessario ──────

S1_TASKS = {
    "compilar", "compilation", "build",
    "executar", "run", "rodar",
    "shell", "terminal", "comando",
    "loc", "lines of code", "contar linhas",
    "pytest", "unit test", "teste",
    "formatar", "format", "lint",
    "ls", "dir", "listar",
    "git status", "git diff", "git log",
    "git add", "git commit", "git push", "git pull",
    "git clone", "git checkout", "git branch",
    "pip install", "npm install",
    "cpu", "memoria", "disk", "processo",
    "instalar", "install",
    "baixar", "download",
}


@dataclass
class ShellzDecision:
    """Decisao imutavel de roteamento."""
    shell: str       # S3 | S1
    role: str        # main | worker
    model: str
    provider: str
    cost_per_1m: float
    reason: str


# ════════════════════════════════════════════════════════
# CORE — NUNCA desligar
# ════════════════════════════════════════════════════════

class Shellz:
    """Shellz — Roteador eterno S3/S1.
    
    Singleton. Auto-inicializa no import.
    Toda interacao PERDE se nao passar por aqui.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if Shellz._initialized:
            return
        Shellz._initialized = True
        
        # Estado eterno
        self._s3_sessions = 0
        self._s1_delegations = 0
        self._tokens_s3 = 0
        self._tokens_s1 = 0
        self._cost_s3 = 0.0
        self._cost_s1 = 0.0
        
        logger.info("Shellz ativo: S3 (DeepSeek) + S1 (Ollama)")
    
    def rotear(self, user_input: str, funcao: str = "main",
               tokens: int = 0) -> ShellzDecision:
        """ROTEAMENTO OBRIGATORIO de toda interacao.
        
        Args:
            user_input: O input do usuario
            funcao: "main" (S3) | "worker" (S1)
            tokens: Tokens estimados para calculo de custo
        
        Returns:
            ShellzDecision com shell, modelo, custo
        """
        lower = user_input.lower()
        
        # FORCE LOCAL PROCESSING: se HERMES_FORCE_LOCAL_PROCESSING=1,
        # toda tarefa com processamento vai para S1 (Ollama)
        if FORCE_LOCAL:
            # Qualquer tarefa que envolva processamento ativo
            process_keywords = S1_TASKS | {
                "processar", "process", "analisar", "analyze",
                "extrair", "extract", "converter", "transform",
                "gerar", "generate", "criar", "create",
                "compilar", "build", "executar", "run",
                "testar", "test", "validar", "validate",
                "baixar", "download", "importar", "import",
                "formatar", "format", "limpar", "clean",
                "calcular", "calculate", "simular", "simulate",
            }
        else:
            process_keywords = S1_TASKS
        
        # Decide se vai para S1
        vai_s1 = False
        for kw in process_keywords:
            if kw in lower:
                vai_s1 = True
                break
        
        if funcao == "worker" or vai_s1:
            decision = ShellzDecision(
                shell="S1",
                role="worker",
                model="qwen2.5-coder:7b",
                provider="ollama",
                cost_per_1m=0.0,
                reason="S1 worker: tarefa local compativel",
            )
            self._s1_delegations += 1
            self._tokens_s1 += tokens
        else:
            decision = ShellzDecision(
                shell="S3",
                role="main",
                model="deepseek-v4-flash",
                provider="deepseek",
                cost_per_1m=0.30,
                reason="S3 main: inteligencia principal",
            )
            self._s3_sessions += 1
            self._tokens_s3 += tokens
        
        # Calcula custo
        if decision.provider == "ollama":
            cost = 0.0
            self._cost_s1 += cost
        else:
            cost = estimate_cost(decision.provider, tokens, tokens // 2)
            self._cost_s3 += cost
        
        # TELEMETRIA OBRIGATORIA
        if HAS_TELEMETRY:
            telemetry.record(
                user_input=str(user_input)[:500],
                action_taken=f"shellz:{funcao}",
                shell_used=decision.shell,
                model_used=decision.model,
                provider=decision.provider,
                total_tokens=tokens,
                cost=cost,
            )
        
        # HEADROOM: se for S3, comprime contexto automaticamente
        if decision.shell == "S3" and HAS_HEADROOM and tokens > 500:
            logger.info("headroom disponivel: comprimir contexto antes de S3")
        
        return decision
    
    def get_stats(self) -> dict:
        """Estado atual do Shellz."""
        return {
            "s3_sessions": self._s3_sessions,
            "s1_delegations": self._s1_delegations,
            "tokens_s3": self._tokens_s3,
            "tokens_s1": self._tokens_s1,
            "cost_s3": self._cost_s3,
            "cost_s1": self._cost_s1,
            "total_cost": self._cost_s3 + self._cost_s1,
            "headroom": HAS_HEADROOM,
        }
    
    def comprimir_contexto(self, messages: list) -> dict:
        """Comprime contexto automaticamente com headroom.ai.
        
        Chamar ANTES de enviar para S3 (DeepSeek).
        Se headroom nao estiver instalado, retorna original.
        
        Args:
            messages: Lista de mensagens no formato LLM
        
        Returns:
            Dict com messages comprimidas + metricas
        """
        if not HAS_HEADROOM:
            return {"messages": messages, "tokens_saved": 0}
        
        try:
            result = compress_messages(messages)
            if result.get("tokens_saved", 0) > 0:
                logger.info(
                    f"headroom: {result['tokens_saved']} tok economizados "
                    f"({result.get('compression_ratio', 0)*100:.0f}%)"
                )
            return result
        except Exception as e:
            logger.warning(f"headroom compress falhou: {e}")
            return {"messages": messages, "tokens_saved": 0}


# ════════════════════════════════════════════════════════
# INSTANCIA UNICA — sempre disponivel no import
# ════════════════════════════════════════════════════════

shellz = Shellz()


def rotear_obrigatorio(user_input: str, funcao: str = "main",
                        tokens: int = 0) -> ShellzDecision:
    """Funcao de conveniencia. Uso: from shellz import rotear_obrigatorio"""
    return shellz.rotear(user_input, funcao, tokens)
