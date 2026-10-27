import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health_endpoint_contract():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "healthy"]
    assert data["service"] == "saarthi"

def test_api_status_endpoint_contract():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "backend_status" in data
    assert data["backend_status"] == "online"

def test_api_tools_endpoint_contract():
    response = client.get("/api/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert "file_list" in data["tools"]

def test_api_chat_endpoint_contract():
    response = client.post("/api/chat", json={"message": "Hello", "session_id": "test_api_sess"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "session_id" in data
    assert data["session_id"] == "test_api_sess"

def test_api_cancel_endpoint_contract():
    response = client.post("/api/chat/cancel/test_api_sess")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test_api_sess"
    assert "cancelled" in data

def test_api_permissions_endpoints_contract():
    # Pending permissions endpoint
    response = client.get("/api/permissions/pending")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    # Approve invalid request_id should return 404
    resp_approve = client.post("/api/permissions/req-invalid-123/approve")
    assert resp_approve.status_code == 404

    # Deny invalid request_id should return 404
    resp_deny = client.post("/api/permissions/req-invalid-123/deny")
    assert resp_deny.status_code == 404

def test_api_history_endpoint_contract():
    response = client.get("/api/history/test_api_sess")
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert isinstance(data["messages"], list)
