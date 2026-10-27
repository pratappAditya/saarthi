import pytest
from app.system.hardware import HardwareProfile
from app.models.recommendation import NemotronRecommendationService

def test_ultra_tier_recommendation_high_spec():
    profile = HardwareProfile(
        os_name="Windows",
        os_version="11",
        architecture="x64",
        cpu_model="Core i9",
        cpu_cores=16,
        total_ram_gb=32.0,
        available_ram_gb=24.0,
        gpu_vendor="NVIDIA",
        gpu_model="RTX 4080",
        vram_gb=16.0,
        free_storage_gb=200.0,
        ollama_installed=True,
        ollama_running=True
    )
    rec = NemotronRecommendationService.recommend_nemotron_model(profile)
    assert rec.recommended_tier == "ULTRA"
    assert rec.recommended_model.model_id == "nemotron-3-8b"

def test_super_tier_recommendation_mid_spec():
    profile = HardwareProfile(
        os_name="Windows",
        os_version="11",
        architecture="x64",
        cpu_model="Core i7",
        cpu_cores=8,
        total_ram_gb=16.0,
        available_ram_gb=10.0,
        gpu_vendor="NVIDIA",
        gpu_model="RTX 3060",
        vram_gb=4.0,
        free_storage_gb=100.0,
        ollama_installed=True,
        ollama_running=True
    )
    rec = NemotronRecommendationService.recommend_nemotron_model(profile)
    assert rec.recommended_tier in ("SUPER", "PRO")

def test_standard_tier_low_spec():
    profile = HardwareProfile(
        os_name="Windows",
        os_version="10",
        architecture="x64",
        cpu_model="Core i5",
        cpu_cores=4,
        total_ram_gb=6.0,
        available_ram_gb=4.0,
        gpu_vendor="Intel",
        gpu_model="Integrated",
        vram_gb=0.0,
        free_storage_gb=20.0,
        ollama_installed=False,
        ollama_running=False
    )
    rec = NemotronRecommendationService.recommend_nemotron_model(profile)
    assert rec.recommended_tier == "STANDARD"
