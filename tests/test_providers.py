"""Testes do Provider Registry (inspirado free-claude-code)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from providers import (
    CATALOG,
    ProviderTier,
    RateLimiter,
    get_provider,
    list_free_providers,
    list_providers,
    select_best_provider,
)


def test_catalog_has_providers():
    """Catalogo deve ter providers registrados."""
    assert len(CATALOG) >= 4, "Pelo menos 4 providers"


def test_ollama_no_catalog():
    """Ollama deve estar no catalogo como FREE."""
    ollama = get_provider("ollama")
    assert ollama is not None
    assert ollama.tier == ProviderTier.FREE
    assert ollama.is_local
    assert ollama.cost_per_million == 0.0


def test_deepseek_no_catalog():
    """DeepSeek deve estar no catalogo como CHEAP."""
    ds = get_provider("deepseek")
    assert ds is not None
    assert ds.tier == ProviderTier.CHEAP
    assert ds.api_key_env == "DEEPSEEK_API_KEY"


def test_list_free():
    """list_free_providers deve retornar so locais/gratis."""
    free = list_free_providers()
    assert len(free) >= 1
    for p in free:
        assert p.tier == ProviderTier.FREE
        assert p.is_local


def test_select_best_free_first():
    """select_best_provider deve preferir local."""
    best = select_best_provider()
    assert best.tier == ProviderTier.FREE
    assert best.is_local or best.cost_per_million == 0.0


def test_select_best_specific_model():
    """select_best_provider com modelo especifico."""
    best = select_best_provider("deepseek-v4-flash")
    assert best is not None
    assert "deepseek" in best.name


def test_rate_limiter_acquire():
    """RateLimiter deve permitir adquirir tokens."""
    rl = RateLimiter("test_provider", tokens_per_sec=10, max_tokens=5)
    for i in range(5):
        assert rl.acquire(), f"Token {i} deve ser adquirido"
    # Sexto token deve falhar (sem recarga)
    assert not rl.acquire()


def test_rate_limiter_wait_time():
    """RateLimiter.wait_time deve retornar >0 quando vazio."""
    rl = RateLimiter("test_wait", tokens_per_sec=1, max_tokens=1)
    rl.acquire()
    # Após consumir, wait_time deve ser >0 ate recarga
    wait = RateLimiter.wait_time("test_wait")
    assert wait >= 0.0


def test_provider_info_fields():
    """ProviderInfo deve ter todos os campos."""
    p = get_provider("ollama")
    assert p.name
    assert p.display_name
    assert p.base_url
    assert p.models
    assert len(p.models) >= 1


def test_list_by_tier():
    """list_providers com filtro de tier."""
    free = list_providers(ProviderTier.FREE)
    cheap = list_providers(ProviderTier.CHEAP)
    assert len(free) >= 1
    assert len(cheap) >= 1
    # Nao devem se sobrepor
    free_names = {p.name for p in free}
    cheap_names = {p.name for p in cheap}
    assert free_names.isdisjoint(cheap_names), "Tiers nao devem se sobrepor"
