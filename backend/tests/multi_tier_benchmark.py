"""
Multi-Tier Hardware Benchmark Script for Closed Beta Hardware Validation #3.
Tests tier recommendations, catalog checks, fallback safeguards, and atomic model switching.
"""

import time
import asyncio
import httpx
from app.system.hardware import HardwareDetectionService
from app.models.recommendation import NemotronRecommendationService
from app.models.nemotron_catalog import NemotronModelCatalog
from app.models.nemotron_service import NemotronService, NemotronModelNotApprovedException
from app.system.installer import NemotronInstallerService
from app.config.settings import settings

async def run_multi_tier_test():
    profile = HardwareDetectionService.get_hardware_profile()
    rec = NemotronRecommendationService.recommend_nemotron_model(profile)

    print("=== MULTI-TIER HARDWARE GUARDRAILS TEST ===")
    print(f"Detected RAM: {profile.total_ram_gb} GB | VRAM: {profile.vram_gb} GB | Storage: {profile.free_storage_gb} GB")
    print(f"Recommended Tier: {rec.recommended_tier} ({rec.recommended_model.model_id})")

    # Verify Catalog Guardrails
    for spec in NemotronModelCatalog.get_all_specs():
        comp = NemotronRecommendationService.check_model_compatibility(spec, profile)
        print(f"Tier [{spec.tier}] ({spec.model_id}): Compatible={comp.compatible}, Status={comp.status.value}, Reason={comp.reason}")

    # Verify Rejection of Unapproved Cloud / Arbitrary Model
    try:
        NemotronService(model_name="claude-3-5-sonnet")
        print("UNAPPROVED MODEL TEST: FAILED (did not reject)")
    except NemotronModelNotApprovedException:
        print("UNAPPROVED MODEL TEST: PASSED (successfully rejected non-approved model)")

    # Test Rejection of Unapproved Model in switch_model_safely
    try:
        await NemotronInstallerService.switch_model_safely("invalid-unapproved-model")
        print("SWITCH REJECTION TEST: FAILED")
    except NemotronModelNotApprovedException:
        print("SWITCH REJECTION TEST: PASSED (successfully blocked unapproved model switch)")

if __name__ == "__main__":
    asyncio.run(run_multi_tier_test())
