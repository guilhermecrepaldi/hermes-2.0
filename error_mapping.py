"""Hermes Error Mapping — inspired by free-claude-code error_mapping.py.
Maps provider-specific errors to standardized Hermes error types.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class HermesError:
    """Standardized error type."""
    code: str
    message: str
    provider: str = ""
    original_error: str = ""
    recoverable: bool = False
    suggestion: str = ""
    severity: str = "error"  # error | warning | info


# Error catalog
ERROR_CATALOG: Dict[str, HermesError] = {
    # Connection errors
    "connection_refused": HermesError(
        code="CONNECTION_REFUSED",
        message="Provider connection refused",
        recoverable=True,
        suggestion="Check if the provider service is running and the port is correct",
    ),
    "timeout": HermesError(
        code="TIMEOUT",
        message="Provider request timed out",
        recoverable=True,
        suggestion="Increase timeout or check network connectivity",
    ),
    "dns_failure": HermesError(
        code="DNS_FAILURE",
        message="Could not resolve provider hostname",
        recoverable=False,
        suggestion="Check your DNS settings and internet connection",
    ),

    # Auth errors
    "auth_failed": HermesError(
        code="AUTH_FAILED",
        message="Provider authentication failed",
        recoverable=False,
        suggestion="Check your API key in environment variables",
    ),
    "rate_limited": HermesError(
        code="RATE_LIMITED",
        message="Provider rate limit exceeded",
        recoverable=True,
        suggestion="Wait before retrying or reduce request frequency",
    ),
    "quota_exceeded": HermesError(
        code="QUOTA_EXCEEDED",
        message="Provider quota exceeded",
        recoverable=False,
        suggestion="Check your provider billing or wait for quota reset",
    ),

    # Model errors
    "model_not_found": HermesError(
        code="MODEL_NOT_FOUND",
        message="Model not found on provider",
        recoverable=True,
        suggestion="Check available models with /models endpoint",
    ),
    "model_overloaded": HermesError(
        code="MODEL_OVERLOADED",
        message="Model is currently overloaded",
        recoverable=True,
        suggestion="Try a different model or provider tier",
    ),
    "context_too_long": HermesError(
        code="CONTEXT_TOO_LONG",
        message="Input exceeds model's context window",
        recoverable=True,
        suggestion="Reduce input size or switch to a model with larger context",
    ),

    # Local errors
    "ollama_not_running": HermesError(
        code="OLLAMA_NOT_RUNNING",
        message="Ollama is not running",
        recoverable=True,
        suggestion="Run 'ollama serve' in the background",
        severity="warning",
    ),
    "model_not_pulled": HermesError(
        code="MODEL_NOT_PULLED",
        message="Local model not downloaded",
        recoverable=True,
        suggestion="Run 'ollama pull <model>' first",
        severity="warning",
    ),

    # Generic
    "internal_error": HermesError(
        code="INTERNAL_ERROR",
        message="Internal error in provider processing",
        recoverable=False,
        suggestion="Check logs for details",
    ),
    "unknown": HermesError(
        code="UNKNOWN",
        message="Unknown provider error",
        recoverable=False,
        suggestion="Check provider status and logs",
    ),
}


def map_error(error: str, provider: str = "") -> HermesError:
    """Map an error string to a standardized HermesError.

    Uses keyword matching against known error patterns.
    Falls back to 'unknown' if no pattern matches.
    """
    error_lower = error.lower()

    # Connection errors
    if any(w in error_lower for w in ["refused", "connection refused", "econnrefused"]):
        return _copy("connection_refused", provider, error)
    if any(w in error_lower for w in ["timeout", "timed out", "time out"]):
        return _copy("timeout", provider, error)
    if any(w in error_lower for w in ["dns", "name or service not known", "resolve"]):
        return _copy("dns_failure", provider, error)

    # Auth errors
    if any(w in error_lower for w in ["auth", "unauthorized", "401", "403", "api key"]):
        return _copy("auth_failed", provider, error)
    if any(w in error_lower for w in ["rate limit", "429", "too many requests"]):
        return _copy("rate_limited", provider, error)
    if any(w in error_lower for w in ["quota", "exceeded", "insufficient"]):
        return _copy("quota_exceeded", provider, error)

    # Model errors
    if any(w in error_lower for w in ["model not found", "not found", "does not exist"]):
        return _copy("model_not_found", provider, error)
    if any(w in error_lower for w in ["overloaded", "capacity", "unavailable"]):
        return _copy("model_overloaded", provider, error)
    if any(w in error_lower for w in ["context", "token limit", "too long", "max tokens"]):
        return _copy("context_too_long", provider, error)

    # Local errors
    if any(w in error_lower for w in ["ollama", "connect"]):
        return _copy("ollama_not_running", provider, error)
    if any(w in error_lower for w in ["pull", "download", "not found"]):
        return _copy("model_not_pulled", provider, error)

    return _copy("unknown", provider, error)


def _copy(code: str, provider: str, original: str) -> HermesError:
    """Create a copy of a catalog error with provider context."""
    base = ERROR_CATALOG.get(code, ERROR_CATALOG["unknown"])
    return HermesError(
        code=base.code,
        message=base.message,
        provider=provider,
        original_error=original,
        recoverable=base.recoverable,
        suggestion=base.suggestion,
        severity=base.severity,
    )


def format_error(err: HermesError) -> str:
    """Format a HermesError for display."""
    icon = "?" if err.recoverable else "X"
    msg = f"[{icon} {err.code}] {err.message}"
    if err.provider:
        msg += f" (provider: {err.provider})"
    if err.suggestion:
        msg += f"\n  Suggestion: {err.suggestion}"
    return msg
