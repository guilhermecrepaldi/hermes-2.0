"""Hermes Model Catalog - inspired by free-claude-code config/catalog.py.
/v1/models endpoint support with native model picker integration.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

try:
    from providers import CATALOG
    PROVIDERS_AVAILABLE = True
except ImportError:
    PROVIDERS_AVAILABLE = False


@dataclass
class ModelInfo:
    """Information about a model in the catalog."""
    id: str
    provider: str
    display_name: str
    tier: str
    cost_per_million: float
    context_window: int = 128000
    supports_vision: bool = False
    supports_tools: bool = True
    supports_streaming: bool = True
    is_local: bool = False
    enabled: bool = True


def build_catalog() -> Dict[str, ModelInfo]:
    """Build model catalog from provider registry."""
    catalog = {}
    if not PROVIDERS_AVAILABLE:
        return catalog

    for provider_name, provider in CATALOG.items():
        if not provider.enabled:
            continue
        for model_name in provider.models:
            model_id = f"{provider_name}/{model_name}"
            catalog[model_id] = ModelInfo(
                id=model_id,
                provider=provider_name,
                display_name=f"{provider.display_name} - {model_name}",
                tier=provider.tier.value,
                cost_per_million=provider.cost_per_million,
                supports_vision=provider.supports_vision,
                supports_tools=provider.supports_tools,
                supports_streaming=provider.supports_streaming,
                is_local=provider.is_local,
                enabled=True,
            )
    return catalog


def get_models_json() -> List[Dict[str, Any]]:
    """Return models in /v1/models compatible format."""
    catalog = build_catalog()
    return [
        {
            "id": model.id,
            "object": "model",
            "created": 1700000000,
            "owned_by": model.provider,
            "permission": [],
            "root": model.id,
            "parent": None,
            "description": model.display_name,
            "tier": model.tier,
            "cost": model.cost_per_million,
            "context_window": model.context_window,
            "capabilities": {
                "vision": model.supports_vision,
                "tools": model.supports_tools,
                "streaming": model.supports_streaming,
            },
            "local": model.is_local,
        }
        for model in catalog.values()
        if model.enabled
    ]


def suggested_model(task: str = "") -> str:
    """Suggest best model for a task type."""
    catalog = build_catalog()
    if not catalog:
        return ""

    task_lower = task.lower()

    if any(w in task_lower for w in ["code", "debug", "python", "js", "function"]):
        for mid, m in catalog.items():
            if "qwen2.5-coder" in mid and m.is_local:
                return mid

    if any(w in task_lower for w in ["image", "screenshot", "vision", "photo"]):
        for mid, m in catalog.items():
            if m.supports_vision and not m.is_local:
                return mid

    for mid, m in catalog.items():
        if m.is_local:
            return mid
    for mid, m in catalog.items():
        if m.tier == "cheap":
            return mid
    for mid in catalog:
        return mid
    return ""


def list_by_tier(tier: str) -> List[str]:
    """List model IDs by tier."""
    return [
        mid for mid, m in build_catalog().items()
        if m.tier == tier and m.enabled
    ]
