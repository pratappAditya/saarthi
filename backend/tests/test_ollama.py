import sys
import os
import pytest
from unittest.mock import AsyncMock, patch

# Ensure both backend/app and backend are in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from app.models.factory import ModelFactory
from app.models.ollama import NemotronProvider
from app.config.settings import settings
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_nemotron_provider_init():
    provider = NemotronProvider(
        model_name="test-model",
        base_url="http://localhost:11434",
        temperature=0.5,
        max_tokens=100
    )
    assert provider.model_name == "test-model"
    assert provider.base_url == "http://localhost:11434"
    assert provider.temperature == 0.5
    assert provider.max_tokens == 100

def test_model_factory_ollama():
    with patch.object(settings, "MODEL_PROVIDER", "ollama"):
        with patch.object(settings, "MODEL_NAME", "nemotron-3-nano:4b"):
            provider = ModelFactory.get_provider()
            assert isinstance(provider, NemotronProvider)
            assert provider.model_name == "nemotron-3-nano:4b"

@pytest.mark.anyio
async def test_nemotron_provider_generate_success():
    provider = NemotronProvider(model_name="nemotron-3-nano:4b")
    
    mock_response = {
        "message": {
            "content": "Hello! I am Saarthi, how can I help you today?"
        }
    }
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=200,
            json=lambda: mock_response
        )
        
        response = await provider.generate_response("hello saarthi")
        assert response == "Hello! I am Saarthi, how can I help you today?"
        
        # Verify call arguments
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "messages" in kwargs["json"]
        assert kwargs["json"]["messages"][0]["role"] == "system"
        assert "abilities that you do not yet have" in kwargs["json"]["messages"][0]["content"]

@pytest.mark.anyio
async def test_nemotron_provider_connect_error():
    import httpx
    provider = NemotronProvider(model_name="nemotron-3-nano:4b")
    
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        with pytest.raises(ConnectionError) as exc_info:
            await provider.generate_response("hello saarthi")
        assert "Cannot connect to Ollama service" in str(exc_info.value)

@pytest.mark.anyio
async def test_nemotron_provider_timeout_error():
    import httpx
    provider = NemotronProvider(model_name="nemotron-3-nano:4b")
    
    with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("Timeout")):
        with pytest.raises(TimeoutError) as exc_info:
            await provider.generate_response("hello saarthi")
        assert "timed out" in str(exc_info.value)

@pytest.mark.anyio
async def test_nemotron_provider_model_not_found():
    provider = NemotronProvider(model_name="non-existent-model")
    
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_post.return_value = AsyncMock(
            status_code=404
        )
        with pytest.raises(RuntimeError) as exc_info:
            await provider.generate_response("hello")
        assert "was not found" in str(exc_info.value)

def test_api_status_mock():
    with patch.object(settings, "MODEL_PROVIDER", "mock"):
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["backend_status"] == "online"
        assert data["model_provider"] == "mock"
        assert data["ollama_connected"] == "not_applicable"
        assert data["model_available"] is True

def test_api_status_ollama_online():
    mock_tags = {
        "models": [
            {"name": "nemotron-3-nano:4b"}
        ]
    }
    with patch.object(settings, "MODEL_PROVIDER", "ollama"):
        with patch.object(settings, "MODEL_NAME", "nemotron-3-nano:4b"):
            with patch("httpx.AsyncClient.get") as mock_get:
                mock_get.return_value = AsyncMock(
                    status_code=200,
                    json=lambda: mock_tags
                )
                response = client.get("/api/status")
                assert response.status_code == 200
                data = response.json()
                assert data["backend_status"] == "online"
                assert data["model_provider"] == "ollama"
                assert data["ollama_connected"] is True
                assert data["model_available"] is True

def test_api_status_ollama_offline():
    import httpx
    with patch.object(settings, "MODEL_PROVIDER", "ollama"):
        with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("Refused")):
            response = client.get("/api/status")
            assert response.status_code == 200
            data = response.json()
            assert data["ollama_connected"] is False
            assert data["model_available"] is False
            assert "Cannot connect" in data["error_message"]
