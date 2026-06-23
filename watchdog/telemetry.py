#!/usr/bin/env python3
"""Hermes Telemetry — Registro OBRIGATORIO de toda interacao.
NUNCA desligar. NUNCA modificar. Persiste em disco.
Registra: input do usuario, acao, resultado, erro, duracao.
"""
from __future__ import annotations
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field, asdict

# Caminho absoluto — NUNCA muda
TELEMETRY_DIR = Path.home() / ".hermes" / "telemetry"
TELEMETRY_FILE = TELEMETRY_DIR / "telemetry.jsonl"


@dataclass
class TelemetryEntry:
    """Uma entrada de telemetria. Imutavel apos escrita."""
    timestamp: str
    session_id: str
    user_input: str
    action_taken: str
    tools_used: list = field(default_factory=list)
    result_summary: str = ""
    duration_ms: float = 0.0
    success: bool = True
    error: Optional[str] = None
    model_used: str = ""
    provider: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    shell_used: str = ""  # S1_local | S2_cheap | S3_premium | S1_nuvem
    api_endpoint: str = ""  # URL da API chamada
    model_selected_by_shell: str = ""  # Modelo escolhido pelo shell
    complexity: int = 0  # Complexidade da tarefa (1-10)


class Telemetry:
    """Sistema de telemetria obrigatorio.
    
    Singleton — instancia unica, sempre ativa.
    NUNCA desativar. NUNCA modificar comportamento.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._session_id = self._generate_session_id()
        self._entry_count = 0
        self._setup_storage()
    
    def _setup_storage(self):
        """Garante que o diretorio de telemetria existe."""
        TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
        # Touch no arquivo
        if not TELEMETRY_FILE.exists():
            TELEMETRY_FILE.touch()
    
    def _generate_session_id(self) -> str:
        """Gera ID unico para esta sessao."""
        return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + f"_{os.getpid()}"
    
    def record(self,
               user_input: str,
               action_taken: str = "",
               tools_used: Optional[list] = None,
               result_summary: str = "",
               duration_ms: float = 0.0,
               success: bool = True,
               error: Optional[str] = None,
               model_used: str = "",
               provider: str = "",
               tokens_input: int = 0,
               tokens_output: int = 0,
               total_tokens: int = 0,
               cost: float = 0.0,
               shell_used: str = "",
               api_endpoint: str = "",
               model_selected_by_shell: str = "",
               complexity: int = 0,
               ) -> None:
        """Registra uma interacao. NUNCA falha.
        
        Esta funcao e chamada em CADA interacao do usuario.
        NUNCA desativar. NUNCA modificar a assinatura.
        """
        self._entry_count += 1
        
        entry = TelemetryEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            session_id=self._session_id,
            user_input=str(user_input)[:500],
            action_taken=str(action_taken)[:200],
            tools_used=tools_used or [],
            result_summary=str(result_summary)[:300],
            duration_ms=duration_ms,
            success=success,
            error=str(error)[:500] if error else None,
            model_used=str(model_used)[:100],
            provider=str(provider)[:100],
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            total_tokens=total_tokens,
            cost=cost,
            shell_used=str(shell_used)[:30],
            api_endpoint=str(api_endpoint)[:200],
            model_selected_by_shell=str(model_selected_by_shell)[:100],
            complexity=complexity,
        )
        
        # Escreve no arquivo — NUNCA falha
        try:
            with open(TELEMETRY_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
        except Exception:
            # Telemetria NUNCA pode quebrar o sistema
            pass
    
    def get_stats(self) -> dict:
        """Estatisticas da sessao atual."""
        return {
            "session_id": self._session_id,
            "entries": self._entry_count,
            "file": str(TELEMETRY_FILE),
            "file_size": TELEMETRY_FILE.stat().st_size if TELEMETRY_FILE.exists() else 0,
        }
    
    def get_session_entries(self, session_id: Optional[str] = None) -> list:
        """Recupera entradas de uma sessao."""
        sid = session_id or self._session_id
        entries = []
        try:
            if TELEMETRY_FILE.exists():
                with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                            if entry.get("session_id") == sid:
                                entries.append(entry)
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass
        return entries
    
    def get_all_entries(self, limit: int = 1000) -> list:
        """Todas as entradas de telemetria."""
        entries = []
        try:
            if TELEMETRY_FILE.exists():
                with open(TELEMETRY_FILE, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i >= limit:
                            break
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass
        return entries
    
    def mini_report(self) -> str:
        """Mini-telemetria para exibir ao final de cada resposta.
        Mostra: cloud vs local tokens, custo, shell.
        Formato: uma linha compacta.
        """
        entries = self.get_all_entries(limit=100)
        
        total_tokens = sum(e.get("total_tokens", 0) for e in entries)
        total_cost = sum(e.get("cost", 0) for e in entries)
        
        # Separa cloud vs local
        cloud_shells = {"S2_cheap", "S3_premium", "S1_nuvem"}
        cloud_tokens = sum(e.get("total_tokens", 0) for e in entries 
                          if e.get("shell_used", "") in cloud_shells)
        local_tokens = sum(e.get("total_tokens", 0) for e in entries 
                          if e.get("shell_used", "") in {"S1_local"})
        
        cloud_cost = sum(e.get("cost", 0) for e in entries 
                        if e.get("shell_used", "") in cloud_shells)
        
        lines = [
            "── telemetria ─────────────────────",
        ]
        
        if total_tokens:
            lines.append(f"  Tokens: {total_tokens} total")
            if cloud_tokens:
                lines.append(f"  Cloud:  {cloud_tokens} tok ${cloud_cost:.4f}")
            if local_tokens:
                lines.append(f"  Local:  {local_tokens} tok $0.0000")
        
        lines.append(f"  Custo:  ${total_cost:.4f}")
        lines.append("────────────────────────────────────")
        
        return "\\n".join(lines)

    def summary(self) -> str:
        """Resumo legivel da telemetria."""
        stats = self.get_stats()
        entries = self.get_all_entries(limit=10)
        
        lines = [
            "=== Hermes Telemetry ===",
            f"Session: {stats['session_id']}",
            f"Entries: {stats['entries']}",
            f"File: {stats['file']} ({stats['file_size']} bytes)",
            "",
        ]
        
        if entries:
            lines.append(f"Last {min(5, len(entries))} entries:")
            for e in entries[-5:]:
                ts = e.get("timestamp", "?")[11:19]
                inp = e.get("user_input", "")[:60]
                act = e.get("action_taken", "")[:30]
                ok = "OK" if e.get("success", True) else "FAIL"
                shell = e.get("shell_used", "")
                tokens = e.get("total_tokens", 0)
                cost = e.get("cost", 0)
                detail = f"[{shell}]" if shell else ""
                detail += f" {tokens}tok" if tokens else ""
                detail += f" ${cost:.4f}" if cost else ""
                lines.append(f"  [{ts}] {ok} {act}: {inp} {detail}")
        
        return "\n".join(lines)


# ═══════════════════════════════════════════════════
# INSTANCIA UNICA — sempre disponivel
# ═══════════════════════════════════════════════════

telemetry = Telemetry()


def record_interaction(**kwargs):
    """Funcao de conveniencia para registrar interacao.
    Uso: from telemetry import record_interaction
         record_interaction(user_input="...", action_taken="...")
    """
    telemetry.record(**kwargs)
