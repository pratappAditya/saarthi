import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.models.ollama import NemotronProvider, clean_reasoning

def test_clean_reasoning_strips_think_tags():
    raw = "<think>internal reasoning details</think>Hello world"
    cleaned = clean_reasoning(raw)
    assert cleaned == "Hello world"

def test_clean_reasoning_strips_unclosed_tags():
    raw = "Hello world<think>unclosed internal thoughts"
    cleaned = clean_reasoning(raw)
    assert cleaned == "Hello world"

@pytest.mark.anyio
async def test_nemotron_provider_connect_error_handling():
    provider = NemotronProvider(base_url="http://invalid-local-url:99999")
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection failed")):
        with pytest.raises(ConnectionError) as exc_info:
            await provider.generate_response("Test prompt")
        assert "Cannot connect to Ollama service" in str(exc_info.value)

@pytest.mark.anyio
async def test_nemotron_provider_timeout_error_handling():
    provider = NemotronProvider()
    with patch("httpx.AsyncClient.post", side_effect=httpx.ReadTimeout("Timeout reached")):
        with pytest.raises(TimeoutError) as exc_info:
            await provider.generate_response("Test prompt")
        assert "Ollama request timed out" in str(exc_info.value)
