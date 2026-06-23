"""Testes do Logger Profissional — JSON + Data Masking."""
from pathlib import Path
import sys, json
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "watchdog"))

from logger_pro import (
    get_logger, mask_data, mask_dict,
    HermesJSONFormatter, setup_hermes_logging,
    SENSITIVE_FIELDS,
)
import logging


def test_get_logger():
    """get_logger deve criar logger."""
    logger = get_logger(__name__)
    assert logger is not None
    assert logger.name == __name__


def test_get_logger_cache():
    """get_logger deve retornar mesmo logger para mesmo nome."""
    l1 = get_logger("test_cache")
    l2 = get_logger("test_cache")
    assert l1 is l2


def test_mask_password():
    """password deve ser mascarado."""
    result = mask_dict({"password": "minhasenha123"})
    assert result["password"] == "***MASKED***"


def test_mask_token():
    """token deve ser mascarado."""
    result = mask_dict({"token": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0In0.dGVzdA"})
    assert result["token"] == "***MASKED***"
    assert "MASKED" in result["token"]


def test_mask_api_key():
    """api_key deve ser mascarado."""
    result = mask_dict({"api_key": "sk-abc123def456"})
    assert result["api_key"] == "***MASKED***"


def test_mask_cpf():
    """CPF deve ser mascarado."""
    result = mask_data("123.456.789-00")
    assert "MASKED" in str(result) or result == "***MASKED***"


def test_mask_email():
    """Email deve ser mascarado."""
    result = mask_data("usuario@example.com")
    assert "MASKED" in str(result)


def test_preserve_safe_fields():
    """userId, action, event nao devem ser mascarados."""
    result = mask_dict({
        "userId": 42,
        "action": "login",
        "event": "user_login",
        "requestId": "req-123",
    })
    assert result["userId"] == 42
    assert result["action"] == "login"
    assert result["event"] == "user_login"


def test_nested_dict_masking():
    """Mascaramento recursivo em dicts aninhados."""
    result = mask_dict({
        "user": {"email": "teste@test.com", "name": "Joao"},
        "credentials": {"password": "secret123"},
    })
    assert "MASKED" in str(result["credentials"]["password"])
    assert "MASKED" in str(result["user"]["email"])


def test_long_string_truncation():
    """Strings longas devem ser truncadas."""
    long_str = "x" * 1000
    result = mask_data(long_str)
    assert len(result) <= 250  # 200 + "..."


def test_mask_list():
    """Listas devem ser mascaradas recursivamente."""
    result = mask_data([
        {"password": "secret"},
        {"email": "test@test.com"},
    ])
    assert len(result) == 2
    assert "MASKED" in str(result[0]["password"])


def test_sensitive_fields_set():
    """SENSITIVE_FIELDS deve conter campos criticos."""
    assert "password" in SENSITIVE_FIELDS
    assert "token" in SENSITIVE_FIELDS
    assert "api_key" in SENSITIVE_FIELDS
    assert "cpf" in SENSITIVE_FIELDS
    assert "email" in SENSITIVE_FIELDS


def test_context_log():
    """context_log deve registrar com contexto."""
    logger = get_logger("test_context")
    # Nao deve lancar excecao
    try:
        logger.context_log("info", "test_event", userId=42, action="test")
        assert True
    except Exception as e:
        assert False, f"context_log raised: {e}"


def test_json_formatter():
    """JSON formatter deve produzir JSON valido."""
    logger = get_logger("test_json_formatter")
    handler = logger.handlers[0]
    formatter = handler.formatter
    
    record = logger.makeRecord(
        "test", logging.INFO, "test.py", 42,
        "test message", (), None
    )
    
    formatted = formatter.format(record)
    parsed = json.loads(formatted)
    assert parsed["level"] == "INFO"
    assert parsed["module"] == "test"
    assert "timestamp" in parsed


def test_log_levels():
    """Niveis de log devem funcionar."""
    logger = get_logger("test_levels")
    try:
        logger.info("info test")
        logger.warn("warn test")
        logger.error("error test")
        assert True
    except Exception as e:
        assert False, f"Log levels raised: {e}"
