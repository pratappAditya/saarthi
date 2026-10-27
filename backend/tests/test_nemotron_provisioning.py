import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_nemotron_hardware_discovery():
    response = client.get("/api/nemotron/hardware")
    assert response.status_code == 200
    data = response.json()
    assert "total_ram_gb" in data
    assert "cpu_cores" in data
    assert "gpu_vendor" in data
    assert "free_storage_gb" in data

def test_nemotron_model_catalog():
    response = client.get("/api/nemotron/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) >= 4
    
    # Check that Nemotron 3.5 Bolt is in catalog
    model_ids = [m["model_id"] for m in data["models"]]
    assert "nemotron-3.5-bolt-e4b" in model_ids
    
    # Verify rich metadata fields are present
    bolt = next(m for m in data["models"] if m["model_id"] == "nemotron-3.5-bolt-e4b")
    assert bolt["model_license"] == "NVIDIA Open Model License"
    assert "recommended_ram_gb" in bolt
    assert "estimated_download_size_gb" in bolt
    assert "context_length" in bolt

def test_nemotron_recommendation():
    response = client.get("/api/nemotron/recommendation")
    assert response.status_code == 200
    data = response.json()
    assert "recommended_tier" in data
    assert "recommended_model" in data
    assert "compatibility" in data

def test_nemotron_download_unapproved_model_rejected():
    response = client.post("/api/nemotron/install-model", json={"model_id": "malicious_unapproved_model:latest"})
    assert response.status_code == 400
    assert "not an approved NVIDIA Nemotron model" in response.json()["detail"]

@pytest.mark.asyncio
async def test_nemotron_download_lifecycle():
    # Test starting a download for approved model
    with patch("app.system.installer.NemotronInstallerService.start_model_download", new_callable=AsyncMock) as mock_start:
        mock_start.return_value = {
            "success": True,
            "status": "DOWNLOADING",
            "model_id": "nemotron-mini:4b",
            "message": "Model download initiated in background."
        }
        response = client.post("/api/nemotron/install-model", json={"model_id": "nemotron-mini:4b"})
        assert response.status_code == 200
        assert response.json()["status"] == "DOWNLOADING"

    # Test download status endpoint
    with patch("app.system.installer.NemotronInstallerService.get_download_status") as mock_status:
        mock_status.return_value = {
            "status": "DOWNLOADING",
            "progress_percent": 45.5,
            "bytes_downloaded": 1024000,
            "bytes_total": 2048000,
            "speed_mbps": 12.4,
            "eta_seconds": 82
        }
        response = client.get("/api/nemotron/download-status/nemotron-mini:4b")
        assert response.status_code == 200
        assert response.json()["progress_percent"] == 45.5

    # Test cancel download endpoint
    with patch("app.system.installer.NemotronInstallerService.cancel_download") as mock_cancel:
        mock_cancel.return_value = {
            "success": True,
            "status": "CANCELLED",
            "model_id": "nemotron-mini:4b",
            "message": "Download cancelled by user."
        }
        response = client.post("/api/nemotron/cancel-download/nemotron-mini:4b")
        assert response.status_code == 200
        assert response.json()["status"] == "CANCELLED"

    # Test model deletion (storage reclamation)
    with patch("app.system.installer.NemotronInstallerService.delete_model", new_callable=AsyncMock) as mock_delete:
        mock_delete.return_value = {
            "success": True,
            "model_id": "nemotron-mini:4b",
            "message": "Model weights removed from local runtime."
        }
        response = client.delete("/api/nemotron/models/nemotron-mini:4b")
        assert response.status_code == 200
        assert response.json()["success"] is True

def test_nemotron_smoke_test():
    with patch("app.system.installer.NemotronInstallerService.run_inference_smoke_test", new_callable=AsyncMock) as mock_smoke:
        mock_smoke.return_value = {
            "success": True,
            "model_id": "nemotron-mini:4b",
            "device": "NVIDIA GPU (CUDA)",
            "gpu_accelerated": True,
            "latency_ms": 142.5,
            "tokens_per_second": 38.2,
            "output": "Executive briefing initialized."
        }
        response = client.post("/api/nemotron/smoke-test", json={"model_id": "nemotron-mini:4b", "prompt": "Test"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["gpu_accelerated"] is True
        assert data["tokens_per_second"] == 38.2
