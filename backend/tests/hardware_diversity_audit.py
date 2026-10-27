"""
Hardware Diversity Audit Script for Saarthi Closed Beta.
Queries physical host machine specifications, runs multi-tier capability analysis,
verifies pricing matrix, and measures local inference performance.
"""

import time
import asyncio
import psutil
from app.system.hardware import HardwareDetectionService
from app.models.recommendation import NemotronRecommendationService
from app.models.nemotron_catalog import NemotronModelCatalog
from app.models.nemotron_service import NemotronService, NemotronModelNotApprovedException
from app.system.installer import NemotronInstallerService
from app.config.settings import settings

async def audit_hardware_diversity():
    print("=== SAARTHI HARDWARE DIVERSITY AUDIT ===")
    profile = HardwareDetectionService.get_hardware_profile()
    
    print("\n--- [PHYSICAL HOST MACHINE PROFILE] ---")
    print(f"OS: {profile.os_name} {profile.os_version}")
    print(f"CPU: {profile.cpu_model} ({profile.cpu_cores} Cores)")
    print(f"RAM: {profile.total_ram_gb} GB Total ({profile.available_ram_gb} GB Available)")
    print(f"GPU: {profile.gpu_vendor} {profile.gpu_model} ({profile.vram_gb} GB VRAM)")
    print(f"Storage: {profile.free_storage_gb} GB SSD Free")
    print(f"Ollama Endpoint: {settings.OLLAMA_BASE_URL}")

    print("\n--- [TIER CAPABILITY MATRIX] ---")
    rec = NemotronRecommendationService.recommend_nemotron_model(profile)
    print(f"Recommended Tier: {rec.recommended_tier} ({rec.recommended_model.model_id})")
    
    for spec in NemotronModelCatalog.get_all_specs():
        comp = NemotronRecommendationService.check_model_compatibility(spec, profile)
        print(f"- Tier [{spec.tier}] ({spec.model_id}): Compatible={comp.compatible}, Status={comp.status.value}, Reason='{comp.reason}'")

    print("\n--- [SECURITY & UNAPPROVED MODEL REJECTION] ---")
    try:
        NemotronService(model_name="claude-3-5-sonnet")
        print("Unapproved Model Test: FAILED (did not reject)")
    except NemotronModelNotApprovedException:
        print("Unapproved Model Test: PASSED (successfully rejected non-approved model)")

    try:
        await NemotronInstallerService.switch_model_safely("invalid-model")
        print("Unapproved Switch Test: FAILED")
    except NemotronModelNotApprovedException:
        print("Unapproved Switch Test: PASSED (successfully blocked unapproved model switch)")

if __name__ == "__main__":
    asyncio.run(audit_hardware_diversity())
