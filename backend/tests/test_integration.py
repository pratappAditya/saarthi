import os
import sys
import httpx
import pytest

# Ensure both backend/app and backend are in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

def is_ollama_running() -> bool:
    try:
        response = httpx.get("http://127.0.0.1:11434/api/tags", timeout=1.0)
        if response.status_code == 200:
            models = [m.get("name", "") for m in response.json().get("models", [])]
            return any("nemotron" in m for m in models)
        return False
    except Exception:
        return False

# Skip this entire module if Ollama is not running with required model
pytestmark = pytest.mark.skipif(
    not is_ollama_running(),
    reason="Ollama service is not running with required nemotron model on localhost:11434"
)

@pytest.fixture(autouse=True)
def setup_integration_env():
    from app.config.settings import settings
    from app.api import routes
    from app.agent.core import AgentCore
    
    original_provider = settings.MODEL_PROVIDER
    original_model = settings.MODEL_NAME
    settings.MODEL_PROVIDER = "ollama"
    settings.MODEL_NAME = "nemotron-3-nano:4b"
    
    # Re-initialize routes.agent with the live provider
    routes.agent = AgentCore()
    
    yield
    
    # Restore original state
    settings.MODEL_PROVIDER = original_provider
    settings.MODEL_NAME = original_model
    routes.agent = AgentCore()

def test_ollama_status_integration():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["backend"] == "Saarthi API"
    assert data["Ollama"] == "connected"
    assert data["model_available"] is True
    assert data["model"] == "nemotron-3-nano:4b"

@pytest.mark.anyio
async def test_nemotron_provider_generation_integration():
    from app.models.ollama import NemotronProvider
    provider = NemotronProvider(model_name="nemotron-3-nano:4b")
    
    # Generate response
    response = await provider.generate_response("Say hello in one sentence.")
    assert len(response) > 0
    assert any(word in response.lower() for word in ["hello", "hi", "assist", "greet", "welcome", "saarthi"])

def test_api_chat_integration():
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    
    response = client.post("/api/chat", json={"message": "Say hello in one sentence.", "session_id": "integration_sess"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["session_id"] == "integration_sess"
    assert len(data["response"]) > 0
