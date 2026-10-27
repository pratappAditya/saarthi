import sys
import os
# Ensure both backend/app and backend are in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    response = client.post("/api/chat", json={"message": "hello test", "session_id": "test_sess"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["session_id"] == "test_sess"
    assert any(kw in data["response"].lower() for kw in ["mock", "response", "default"])
