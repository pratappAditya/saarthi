"""
Phase 4, 5, 6, 7 — Automated Tests for Hardware Detection, Nemotron Model Selection,
GPU Acceleration Diagnostics, and Ollama Lifecycle.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.system.hardware import HardwareDetectionService, HardwareProfile
from app.models.recommendation import NemotronRecommendationService
from app.models.nemotron_catalog import NemotronModelCatalog
from app.models.installer import NemotronLifecycleManager
from app.config.settings import settings

client = TestClient(app)


def test_hardware_detection_returns_real_system_parameters():
    """Verify hardware detection endpoint returns valid system specs from physical host."""
    res = client.get("/api/ai/hardware")
    assert res.status_code == 200
    data = res.json()
    assert "os_name" in data and len(data["os_name"]) > 0
    assert "cpu_model" in data and len(data["cpu_model"]) > 0
    assert data["cpu_cores"] > 0
    assert data["total_ram_gb"] > 0
    assert "gpu_vendor" in data
    assert "gpu_model" in data
    assert data["vram_gb"] >= 0
    assert data["free_storage_gb"] >= 0


def test_unified_hardware_recommendation_pipeline():
    """Verify hardware profile deterministically selects appropriate Nemotron tier."""
    profile = HardwareDetectionService.get_hardware_profile()
    rec = NemotronRecommendationService.recommend_nemotron_model(profile)
    assert rec.recommended_tier in ("STANDARD", "PRO", "SUPER", "ULTRA")
    assert rec.recommended_model is not None
    assert len(rec.reason) > 0


def test_no_unapproved_cloud_llm_fallback():
    """Verify system config does NOT use OpenAI, Anthropic, or external cloud LLMs."""
    assert settings.MODEL_PROVIDER.lower() in ("ollama", "mock")
    assert "openai" not in settings.MODEL_NAME.lower()
    assert "claude" not in settings.MODEL_NAME.lower()
    assert "gpt" not in settings.MODEL_NAME.lower()


def test_gpu_acceleration_diagnostics_endpoint():
    """Verify GPU acceleration status endpoint provides real diagnostic info."""
    res = client.get("/api/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert "state_code" in data
    assert "active_model" in data
    assert data["is_approved_nemotron"] is True or False


@pytest.mark.asyncio
async def test_ollama_lifecycle_status():
    """Verify Ollama lifecycle manager accurately reports status and reachability."""
    status = await NemotronLifecycleManager.check_ollama_status()
    assert "connected" in status
    assert "status_code" in status
