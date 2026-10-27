import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_record_churn_reason_success():
    res = client.post("/api/churn/reason", json={"category": "JOB_FOUND", "user_id": "test_user_1"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "privacy guarantee" in data["message"].lower()

def test_record_churn_reason_invalid_category():
    res = client.post("/api/churn/reason", json={"category": "INVALID_CAT", "user_id": "test_user_1"})
    assert res.status_code == 400
    assert "Invalid churn category" in res.json()["detail"]
