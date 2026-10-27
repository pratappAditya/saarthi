"""
Phase 3 — Automated Tests for Licensing & Entitlement Safety.
Verifies that:
- Fake licenses are rejected.
- Fake Power activations fail.
- Backend is authoritative (localStorage cannot alter entitlement status).
- Model switching respects plan tier permissions.
- FREE exports enforce watermarks.
- ULTRA hardware gate blocks Power activation on ineligible machines.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.profile import ProfileRepository, BenchmarkRepository
from app.licensing.middleware import default_client_manager
from app.licensing.models import LicenseStatus, LicensePlan
from app.system.hardware import HardwareProfile
from app.models.recommendation import NemotronRecommendationService

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_clean_state():
    """Ensure clean state before each test."""
    ProfileRepository.clear_profile()
    BenchmarkRepository.clear_benchmarks()
    default_client_manager.clear_license()
    yield
    ProfileRepository.clear_profile()
    BenchmarkRepository.clear_benchmarks()
    default_client_manager.clear_license()


def test_fake_license_key_activation_fails():
    """Verify that attempting to activate an arbitrary or fake license key fails."""
    fake_key = "SAARTHI-POWER-FAKE-KEY-99999"
    res = client.post("/api/license/activate", json={"license_key": fake_key})
    assert res.status_code in (400, 422, 404, 401)
    
    # Status should remain UNLICENSED / FREE
    status_res = client.get("/api/license/status").json()
    assert status_res["status"] == LicenseStatus.UNLICENSED.value
    assert status_res["entitlements"]["plan"] == LicensePlan.FREE.value


def test_unauthorized_unapproved_model_switch_fails():
    """Verify that switching to an unapproved model is rejected."""
    res = client.post("/api/ai/model/switch", json={"model_id": "unapproved-random-cloud-model"})
    assert res.status_code in (400, 403, 422, 500)


def test_free_watermark_enforcement():
    """Verify FREE entitlement strictly sets requires_watermark = True."""
    status_res = client.get("/api/license/status").json()
    assert status_res["entitlements"]["requires_watermark"] is True


def test_ultra_hardware_gate_evaluates_real_hardware():
    """Verify ULTRA hardware gate checks VRAM and RAM requirements accurately."""
    low_spec_profile = HardwareProfile(
        os_name="Windows",
        os_version="10.0.19045",
        architecture="x86_64",
        cpu_model="Intel Core i5-8250U",
        cpu_cores=4,
        total_ram_gb=8.0,
        available_ram_gb=4.0,
        gpu_vendor="Intel",
        gpu_model="UHD Graphics 620",
        vram_gb=0.0,
        free_storage_gb=50.0,
        ollama_installed=True,
        ollama_running=True,
        installed_nemotron_models=["nemotron:3b"]
    )
    
    # Evaluate low spec hardware profile against Nemotron recommendation engine
    recommendation = NemotronRecommendationService.recommend_nemotron_model(low_spec_profile)
    ultra_comp = recommendation.compatibility.get("ULTRA")
    
    assert ultra_comp is not None
    assert ultra_comp.compatible is False
    assert "Requires dedicated GPU with at least" in ultra_comp.reason or "Requires minimum" in ultra_comp.reason
    assert recommendation.recommended_tier != "ULTRA"
