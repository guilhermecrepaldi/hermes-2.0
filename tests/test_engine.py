"""Testes do Engine: progress, worktree, checkpoints, hooks, cache."""
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from engine import (
    carregar_progresso, salvar_progresso,
    HookManager, CheckpointManager, KVCache,
    InitializerAgent, CodingAgent
)


def test_progresso_salva_e_carrega():
    """Salvar progresso e carregar deve retornar os itens."""
    salvar_progresso("TEST", "testando progresso")
    estado = carregar_progresso()
    assert isinstance(estado, dict)
    assert "feito" in estado


def test_progresso_sem_arquivo():
    """Sem arquivo, deve retornar dict vazio."""
    backup = CheckpointManager.DIR.parent / "hermes-progress.md"
    if backup.exists():
        backup.rename(backup.parent / "hermes-progress.bak")
    estado = carregar_progresso()
    assert isinstance(estado, dict)
    assert estado.get("feito") == []


def test_hook_register_and_execute():
    """Registrar e executar hook deve funcionar."""
    HookManager._hooks = {"pre": {}, "post": {}}

    def my_hook(ctx):
        return {"status": "ok", "path": ctx.get("path")}

    HookManager.register("pre", "test_tool", my_hook)
    result = HookManager.execute("pre", "test_tool", {"path": "/test"})
    assert result["executed"] == 1
    assert result["results"][0]["status"] == "ok"


def test_hook_sem_registro():
    """Hook sem registro deve retornar executed=0."""
    result = HookManager.execute("pre", "inexistente", {})
    assert result["executed"] == 0


def test_kv_cache_set_get():
    """Set e get no cache KV."""
    KVCache._cache = {}
    KVCache.set("chave_teste", {"dado": 42}, ttl=60)
    result = KVCache.get("chave_teste")
    assert result == {"dado": 42}


def test_kv_cache_ttl_expired():
    """Cache expirado deve retornar None."""
    KVCache._cache = {}
    KVCache.set("chave_teste", "valor", ttl=-1)  # Already expired
    result = KVCache.get("chave_teste")
    assert result is None


def test_kv_cache_miss():
    """Chave inexistente deve retornar None."""
    KVCache._cache = {}
    result = KVCache.get("nao_existe")
    assert result is None


def test_checkpoint_save_and_list():
    """Checkpoint salva e lista."""
    result = CheckpointManager.save("test_unit")
    assert result["status"] == "ok"
    assert "hash" in result
    cps = CheckpointManager.list()
    assert any("test_unit" in cp for cp in cps)


def test_initializer_agent():
    """InitializerAgent.setup deve retornar setup_ok."""
    result = InitializerAgent.setup("testar initializer")
    assert result["status"] == "setup_ok"
    assert "rules" in result["context"]


def test_coding_agent_plan():
    """CodingAgent.plan deve retornar lista de passos."""
    setup = {
        "context": {
            "descricao": "criar funcao hello world",
            "rules": ["rule1"]
        }
    }
    plan = CodingAgent.plan_and_execute(setup)
    assert isinstance(plan, list)
    assert len(plan) >= 3
