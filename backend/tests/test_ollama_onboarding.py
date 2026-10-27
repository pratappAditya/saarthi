import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ollama_diagnostics_endpoint():
    res = client.get("/api/ollama/diagnostics")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "state_code" in data
    assert data["state_code"] in [
        "READY", "OLLAMA_NOT_INSTALLED", "MODEL_NOT_DOWNLOADED",
        "OLLAMA_OFFLINE", "INSUFFICIENT_HARDWARE", "MODEL_CORRUPTED",
        "NETWORK_DOWNLOAD_FAILURE", "TECHNICAL_PROBLEM"
    ]
