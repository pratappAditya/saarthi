import sys
import os
import json
import pytest
from fastapi.testclient import TestClient

# Ensure both backend/app and backend are in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app"))

from app.main import app
from app.config.settings import settings
from app.memory.sqlite_store import SQLiteMemoryStore
from app.memory.manager import MemoryManager

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_env(tmp_path):
    # Set up temp database for testing isolation
    original_db = settings.DATABASE_PATH
    db_file = os.path.join(tmp_path, "test_saarthi_integration.db")
    settings.DATABASE_PATH = db_file
    
    yield
    
    settings.DATABASE_PATH = original_db

def test_saarthi_status_endpoint():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["backend"] == "Saarthi API"
    assert data["model_provider"] == settings.MODEL_PROVIDER
    assert data["model_name"] == settings.MODEL_NAME

def test_saarthi_chat_and_history_workflow():
    session_id = "test_saarthi_workflow_sess"
    
    # 1. Clear session history
    client.delete(f"/api/history/{session_id}")
    
    # 2. Check empty history
    response = client.get(f"/api/history/{session_id}")
    assert response.status_code == 200
    assert response.json()["messages"] == []
    
    # 3. Post a message
    response = client.post("/api/chat", json={"message": "What is the capital of India?", "session_id": session_id})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["session_id"] == session_id
    assert data["status"] == "success"
    
    # 4. Fetch history and verify chronological order
    response = client.get(f"/api/history/{session_id}")
    assert response.status_code == 200
    messages = response.json()["messages"]
    assert len(messages) == 2
    assert messages[0]["sender"] == "user"
    assert messages[1]["sender"] == "assistant"

def test_saarthi_reasoning_cleaning():
    from app.models.ollama import clean_reasoning
    
    leaked_text = "<think>Calculating options...</think>The answer is 42."
    cleaned = clean_reasoning(leaked_text)
    assert cleaned == "The answer is 42."

def test_saarthi_permissions_lifecycle():
    # Verify permission request returns pending list empty by default
    response = client.get("/api/permissions/pending")
    assert response.status_code == 200
    assert response.json() == []
