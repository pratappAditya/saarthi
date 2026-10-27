import pytest
from app.memory.manager import memory_manager
from app.agent.errors import SaarthiError, ErrorCategory

def test_secret_redaction_memory_rejection():
    # Passwords / API keys injected into memory creation must be rejected
    secret_payloads = [
        "sk-1234567890abcdef1234567890abcdef",
        "ghp_1234567890abcdef1234567890abcdef",
        "DATABASE_PASSWORD=super_secret_pass_123!"
    ]

    for secret in secret_payloads:
        with pytest.raises(ValueError) as exc_info:
            memory_manager.create_memory(
                category="PREFERENCE",
                key="test_secret",
                content=secret,
                source="user"
            )
        assert "Refusing to store potential secrets" in str(exc_info.value)

def test_secret_redaction_sanitized_errors():
    raw_error_detail = "Failed to connect using connection string postgresql://user:super_secret_password@db.local:5432/main"
    err = SaarthiError(category=ErrorCategory.MODEL_ERROR, message=raw_error_detail)
    
    # Sanitized user message must not leak connection string or password
    assert "super_secret_password" not in err.user_message
    assert "postgresql://" not in err.user_message
