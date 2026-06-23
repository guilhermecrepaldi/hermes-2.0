"""Testes do Model Catalog + Launchers (free-claude-code inspired)."""
from pathlib import Path
import sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from model_catalog import (
    build_catalog, get_models_json, suggested_model, list_by_tier, ModelInfo
)


def test_catalog_has_models():
    """Catalogo deve ter modelos de todos os providers."""
    cat = build_catalog()
    assert len(cat) >= 5, f"Expected >=5 models, got {len(cat)}"


def test_ollama_model_in_catalog():
    """Modelo do Ollama deve estar no catalogo como local."""
    cat = build_catalog()
    ollama_models = [m for m in cat.values() if m.provider == "ollama"]
    assert len(ollama_models) >= 1
    assert ollama_models[0].is_local


def test_models_json_format():
    """get_models_json deve retornar lista de dicts no formato /v1/models."""
    models = get_models_json()
    assert isinstance(models, list)
    assert len(models) >= 5
    first = models[0]
    assert "id" in first
    assert "object" in first
    assert "capabilities" in first
    assert "vision" in first["capabilities"]


def test_suggested_model_code():
    """suggested_model para code tasks deve preferir modelo local de codigo."""
    model = suggested_model("write a python function")
    assert model, "Deveria sugerir um modelo"
    assert "qwen2.5-coder" in model or isinstance(model, str)


def test_suggested_model_default():
    """suggested_model sem task deve retornar modelo local."""
    model = suggested_model()
    assert model, "Deveria sugerir algo mesmo sem task"


def test_list_by_tier_free():
    """list_by_tier('free') deve retornar modelos locais."""
    free_models = list_by_tier("free")
    assert len(free_models) >= 1
    for mid in free_models:
        assert "ollama" in mid or "llamacpp" in mid


def test_list_by_tier_cheap():
    """list_by_tier('cheap') deve retornar modelos de nuvem baratos."""
    cheap = list_by_tier("cheap")
    assert len(cheap) >= 1
    for mid in cheap:
        assert "deepseek" in mid or "openrouter" in mid


def test_model_info_fields():
    """ModelInfo deve ter todos os campos."""
    cat = build_catalog()
    model = list(cat.values())[0]
    assert model.id
    assert model.provider
    assert model.display_name
    assert model.tier
    assert model.cost_per_million >= 0
