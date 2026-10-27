"""
Post-UI Integration Regression Test Suite for Saarthi
Verifies pricing matrix, Nemotron-only strictness, watermark entitlements,
hardware detection, tier recommendation, and atomic model switching.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.nemotron_config import NemotronConfig
from app.models.nemotron_service import NemotronService, NemotronModelMismatchException, NemotronModelNotApprovedException
from app.models.nemotron_catalog import NemotronModelCatalog
from app.system.hardware import HardwareDetectionService
from app.models.recommendation import NemotronRecommendationService
from app.system.installer import NemotronInstallerService
from app.licensing.watermark import WatermarkEngine
from app.licensing.models import Entitlements

client = TestClient(app)

def test_pricing_matrix_endpoint_inr():
    response = client.get("/api/billing/pricing-experiment?region=IN")
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "INR"
    assert data["free"] == 0
    assert data["personal"] == 399
    assert data["power"] == 799

def test_pricing_matrix_endpoint_usd():
    response = client.get("/api/billing/pricing-experiment?region=US")
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "USD"
    assert data["free"] == 0
    assert data["student"] == 1.50
    assert data["personal"] == 5.00
    assert data["power"] == 10.00

def test_nemotron_only_strict_rejection():
    # Attempting to instantiate NemotronService with non-approved or cloud models must raise exception
    with pytest.raises(NemotronModelNotApprovedException):
        NemotronService(model_name="gpt-4o")

    with pytest.raises(NemotronModelNotApprovedException):
        NemotronService(model_name="claude-3-5-sonnet")

    with pytest.raises(NemotronModelMismatchException):
        NemotronService(model_name="llama-3-8b")

def test_nemotron_approved_catalog_tiers():
    specs = NemotronModelCatalog.get_all_specs()
    tier_tags = [spec.model_id for spec in specs]
    assert "nemotron:3b" in tier_tags
    assert "nemotron-mini:4b" in tier_tags
    assert "nemotron-3-nano:4b" in tier_tags
    assert "nemotron-3-8b" in tier_tags

def test_watermark_free_vs_paid():
    free_ent = Entitlements(plan="FREE", max_active_devices=1, requires_watermark=True)
    paid_ent = Entitlements(plan="PERSONAL", max_active_devices=2, requires_watermark=False)

    # Free tier gets watermark
    free_doc = WatermarkEngine.watermark_markdown("Sample Resume Body", entitlements=free_ent)
    assert "Created with Saarthi" in free_doc

    # Paid tier gets clean doc
    paid_doc = WatermarkEngine.watermark_markdown("Sample Resume Body", entitlements=paid_ent)
    assert "Created with Saarthi" not in paid_doc
    assert paid_doc == "Sample Resume Body"

def test_hardware_detection_profile():
    profile = HardwareDetectionService.get_hardware_profile()
    assert profile.cpu_model != ""
    assert profile.total_ram_gb > 0
    assert isinstance(profile.gpu_model, str)

def test_tier_recommendation_logic():
    profile = HardwareDetectionService.get_hardware_profile()
    rec = NemotronRecommendationService.recommend_nemotron_model(profile)
    assert rec.recommended_tier in ["STANDARD", "PRO", "SUPER", "ULTRA"]
    assert rec.recommended_model is not None

@pytest.mark.asyncio
async def test_installer_safe_switch():
    result = await NemotronInstallerService.switch_model_safely("nemotron-mini:4b")
    assert "active_model" in result
    assert result["active_model"] in ["nemotron-mini:4b", "nemotron-3-nano:4b"]
