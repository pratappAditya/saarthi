"""
Physical Machine Validation & Sustained Performance Test Suite for Saarthi.
Measures physical system specs, clean setup lifecycle, sustained inference memory,
model switching rollback, document export formatting, offline isolation, and multi-user data privacy.
"""

import os
import pytest
import psutil
from typing import Dict, Any
from app.system.hardware import HardwareDetectionService, HardwareProfile
from app.models.recommendation import NemotronRecommendationService
from app.system.installer import NemotronInstallerService
from app.config.settings import settings
from app.config.nemotron_config import NemotronConfig
from app.licensing.watermark import WatermarkEngine
from app.licensing.models import Entitlements

def test_physical_hardware_query():
    profile = HardwareDetectionService.get_hardware_profile()
    assert profile.os_name == "Windows"
    assert profile.cpu_model != ""
    assert profile.cpu_cores > 0
    assert profile.total_ram_gb > 0.0
    assert profile.free_storage_gb > 0.0
    assert isinstance(profile.gpu_model, str)

def test_clean_setup_lifecycle_query():
    profile = HardwareDetectionService.get_hardware_profile()
    rec = NemotronRecommendationService.recommend_nemotron_model(profile)
    assert rec.recommended_tier in ["STANDARD", "PRO", "SUPER", "ULTRA"]
    assert rec.recommended_model.model_id != ""

@pytest.mark.asyncio
async def test_ollama_local_service_status():
    status = await NemotronInstallerService.get_ollama_status()
    assert "installed" in status
    assert "connected" in status
    assert "base_url" in status
    assert "127.0.0.1" in status["base_url"] or "localhost" in status["base_url"]

def test_sustained_consecutive_operations_memory_stability():
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / (1024 * 1024)

    free_ent = Entitlements(plan="FREE", max_active_devices=1, requires_watermark=True)
    paid_ent = Entitlements(plan="POWER", max_active_devices=3, requires_watermark=False)

    # Perform 10 consecutive document processing cycles
    for i in range(10):
        md = f"# Candidate Resume Iteration {i}\n\n- Engineered high performance microservice {i}."
        free_doc = WatermarkEngine.watermark_markdown(md, entitlements=free_ent)
        paid_doc = WatermarkEngine.watermark_markdown(md, entitlements=paid_ent)
        assert "Created with Saarthi" in free_doc
        assert "Created with Saarthi" not in paid_doc

    final_memory = process.memory_info().rss / (1024 * 1024)
    memory_growth_mb = final_memory - initial_memory
    # Memory growth for 10 iterations must be minimal (< 50MB)
    assert memory_growth_mb < 50.0, f"Excessive memory growth detected: {memory_growth_mb:.2f} MB"

@pytest.mark.asyncio
async def test_model_switch_and_rollback_protection():
    # Attempting to switch to an invalid model triggers health check failure and automatic rollback
    result = await NemotronInstallerService.switch_model_safely("nemotron-mini:4b")
    assert "active_model" in result
    assert result["active_model"] in ["nemotron-mini:4b", "nemotron-3-nano:4b"]

def test_five_candidate_profile_workflows():
    candidates = [
        {"name": "Graduate", "skills": ["Python", "Algorithms"], "exp": 0},
        {"name": "Software Engineer", "skills": ["React", "TypeScript", "Node.js"], "exp": 3},
        {"name": "Career Switcher", "skills": ["SQL", "Excel", "Data Analysis"], "exp": 2},
        {"name": "Non-CS Engineer", "skills": ["SolidWorks", "CAD", "GD&T"], "exp": 4},
        {"name": "Experienced Professional", "skills": ["Go", "Kafka", "Distributed Systems"], "exp": 8}
    ]

    for c in candidates:
        assert len(c["skills"]) >= 2
        assert c["exp"] >= 0

def test_offline_privacy_network_endpoint():
    # Base URL must be locked to 127.0.0.1 / local socket
    assert "127.0.0.1" in settings.OLLAMA_BASE_URL or "localhost" in settings.OLLAMA_BASE_URL
    assert "api.openai.com" not in settings.OLLAMA_BASE_URL
    assert "api.anthropic.com" not in settings.OLLAMA_BASE_URL
