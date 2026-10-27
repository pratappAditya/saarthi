import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_nemotron_setup_endpoints():
    resp = client.get("/api/nemotron/hardware")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_ram_gb" in data

    resp_cat = client.get("/api/nemotron/models")
    assert resp_cat.status_code == 200
    assert len(resp_cat.json()["models"]) >= 4

    resp_rec = client.get("/api/nemotron/recommendation")
    assert resp_rec.status_code == 200
    assert "recommended_tier" in resp_rec.json()
