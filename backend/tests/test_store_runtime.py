import pytest
from app.config.settings import settings

def test_store_runtime_security_settings():
    assert settings.APP_NAME == "Saarthi"
    assert "127.0.0.1" in settings.OLLAMA_BASE_URL
