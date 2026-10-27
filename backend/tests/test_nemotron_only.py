import pytest
from app.config.nemotron_config import NemotronConfig
from app.models.nemotron_service import NemotronService, NemotronModelMismatchException
from app.models.factory import ModelFactory
from app.models.ollama import NemotronProvider

def test_nemotron_config_exact_model():
    assert NemotronConfig.EXACT_NEMOTRON_MODEL == "nemotron-3-nano:4b"
    assert NemotronConfig.OLLAMA_BASE_URL == "http://127.0.0.1:11434"

def test_nemotron_service_approved_model_validation():
    assert NemotronService.is_approved_nemotron_model("nemotron-3-nano:4b") is True
    assert NemotronService.is_approved_nemotron_model("nemotron-7b") is True
    assert NemotronService.is_approved_nemotron_model("mock-model") is True
    assert NemotronService.is_approved_nemotron_model("gpt-4o") is False
    assert NemotronService.is_approved_nemotron_model("claude-3-5-sonnet") is False

def test_nemotron_service_mismatch_exception():
    with pytest.raises(NemotronModelMismatchException) as exc_info:
        NemotronService(model_name="unapproved-llama-model")
    assert "nemotron" in str(exc_info.value).lower()
    assert exc_info.value.requested_model == "unapproved-llama-model"

def test_model_factory_returns_nemotron_provider():
    provider = ModelFactory.get_provider()
    assert provider is not None
