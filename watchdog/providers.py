"""Hermes Provider Registry — inspired by free-claude-code.
17 providers, central registry, per-provider transport.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
import time
import json

try:
    from logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ProviderTier(Enum):
    FREE = "free"
    CHEAP = "cheap"
    MEDIUM = "medium"
    EXPENSIVE = "expensive"
    PREMIUM = "premium"


@dataclass
class ProviderInfo:
    name: str
    display_name: str
    base_url: str
    api_key_env: str
    tier: ProviderTier
    models: List[str] = field(default_factory=list)
    supports_streaming: bool = True
    supports_vision: bool = False
    supports_tools: bool = True
    cost_per_million: float = 0.0
    requires_key: bool = True
    transport: str = "http"
    is_local: bool = False
    enabled: bool = True


@dataclass
class ProviderResult:
    success: bool
    model: str = ""
    response: str = ""
    error: Optional[str] = None
    tokens_used: int = 0
    cost: float = 0.0
    time_taken: float = 0.0
    provider: str = ""


class RateLimiter:
    """Token bucket rate limiter per provider."""

    _buckets: Dict[str, dict] = {}

    def __init__(self, provider: str, tokens_per_sec: float = 1.0, max_tokens: int = 10):
        self.provider = provider
        if provider not in self._buckets:
            self._buckets[provider] = {
                "tokens": max_tokens,
                "max_tokens": max_tokens,
                "rate": tokens_per_sec,
                "last_refill": time.time(),
            }

    def acquire(self, tokens: int = 1) -> bool:
        bucket = self._buckets[self.provider]
        now = time.time()
        elapsed = now - bucket["last_refill"]
        bucket["tokens"] = min(bucket["max_tokens"], bucket["tokens"] + elapsed * bucket["rate"])
        bucket["last_refill"] = now
        if bucket["tokens"] >= tokens:
            bucket["tokens"] -= tokens
            return True
        return False

    @classmethod
    def wait_time(cls, provider: str) -> float:
        bucket = cls._buckets.get(provider)
        if not bucket or bucket["tokens"] > 0:
            return 0.0
        return (1.0 - bucket["tokens"]) / bucket["rate"]


# Provider registry
OLLAMA_URL = "http://localhost:11434/api/generate"
LOCAL_MODEL = "qwen2.5-coder:7b"

CATALOG: Dict[str, ProviderInfo] = {
    "ollama": ProviderInfo(
        name="ollama",
        display_name="Ollama (Local)",
        base_url="http://localhost:11434",
        api_key_env="",
        tier=ProviderTier.FREE,
        models=[LOCAL_MODEL, "qwen3-vl:4b", "deepseek-coder-v2:lite",
                "llama3.1:8b", "gemma3:latest", "mistral:latest"],
        cost_per_million=0.0,
        requires_key=False,
        is_local=True,
        enabled=True,
    ),
    "llamacpp": ProviderInfo(
        name="llamacpp",
        display_name="llama.cpp (Local)",
        base_url="http://localhost:8080",
        api_key_env="",
        tier=ProviderTier.FREE,
        models=["llama-3.2-3b", "qwen2.5-7b"],
        cost_per_million=0.0,
        requires_key=False,
        is_local=True,
        enabled=True,
    ),
    "deepseek": ProviderInfo(
        name="deepseek",
        display_name="DeepSeek",
        base_url="https://api.deepseek.com",
        api_key_env="DEEPSEEK_API_KEY",
        tier=ProviderTier.CHEAP,
        models=["deepseek-v4-flash", "deepseek-v4-pro", "deepseek-chat"],
        cost_per_million=0.15,
        enabled=True,
    ),
    "openrouter": ProviderInfo(
        name="openrouter",
        display_name="OpenRouter",
        base_url="https://openrouter.ai/api/v1",
        api_key_env="OPENROUTER_API_KEY",
        tier=ProviderTier.CHEAP,
        models=["openrouter/free", "openrouter/auto"],
        cost_per_million=0.0,
        enabled=True,
    ),
    "gemini": ProviderInfo(
        name="gemini",
        display_name="Google Gemini",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        api_key_env="GEMINI_API_KEY",
        tier=ProviderTier.MEDIUM,
        models=["gemini/models/gemini-3.1-flash-lite"],
        cost_per_million=0.30,
        supports_vision=True,
        enabled=True,
    ),
    "nvidia_nim": ProviderInfo(
        name="nvidia_nim",
        display_name="NVIDIA NIM",
        base_url="https://integrate.api.nvidia.com/v1",
        api_key_env="NVIDIA_NIM_API_KEY",
        tier=ProviderTier.PREMIUM,
        models=["nvidia/nemotron-3-super-120b-a12b",
                "z-ai/glm5.1", "moonshotai/kimi-k2.5"],
        cost_per_million=0.0,
        supports_vision=True,
        enabled=True,
    ),
}


def get_provider(name: str) -> Optional[ProviderInfo]:
    return CATALOG.get(name)


def list_providers(tier: Optional[ProviderTier] = None) -> List[ProviderInfo]:
    providers = [p for p in CATALOG.values() if p.enabled]
    if tier:
        providers = [p for p in providers if p.tier == tier]
    return providers


def list_free_providers() -> List[ProviderInfo]:
    return [p for p in CATALOG.values() if p.tier == ProviderTier.FREE and p.enabled]


def select_best_provider(model: str = "") -> ProviderInfo:
    if model:
        for p in CATALOG.values():
            if model in p.models and p.enabled:
                return p
    for p in list_free_providers():
        return p
    for p in CATALOG.values():
        if p.enabled:
            return p
    return list(CATALOG.values())[0]


def check_ollama() -> bool:
    import urllib.request
    try:
        req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        data = json.loads(req.read())
        return len(data.get("models", [])) > 0
    except Exception:
        return False
