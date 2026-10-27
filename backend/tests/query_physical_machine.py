"""
Query Host Physical Machine Hardware Profile.
"""

import platform
import psutil
import shutil
import os
from app.system.hardware import HardwareDetectionService
from app.models.recommendation import NemotronRecommendationService

def main():
    profile = HardwareDetectionService.get_hardware_profile()
    print("=== PHYSICAL HOST MACHINE IDENTIFICATION ===")
    print(f"OS Name & Version : {profile.os_name} {profile.os_version}")
    print(f"Architecture      : {profile.architecture}")
    print(f"CPU Model         : {profile.cpu_model}")
    print(f"CPU Cores         : {profile.cpu_cores}")
    print(f"Total System RAM  : {profile.total_ram_gb} GB")
    print(f"Available RAM     : {profile.available_ram_gb} GB")
    print(f"GPU Vendor        : {profile.gpu_vendor}")
    print(f"GPU Model         : {profile.gpu_model}")
    print(f"Dedicated VRAM    : {profile.vram_gb} GB")
    print(f"Free SSD Storage  : {profile.free_storage_gb} GB")
    print(f"Ollama Installed  : {profile.ollama_installed}")
    print(f"Ollama Running    : {profile.ollama_running}")
    print(f"Installed Models  : {profile.installed_nemotron_models}")

    rec = NemotronRecommendationService.recommend_nemotron_model(profile)
    print(f"\nRecommended Tier  : {rec.recommended_tier}")
    print(f"Recommended Model : {rec.recommended_model.model_id if rec.recommended_model else 'None'}")
    print(f"Reason            : {rec.reason}")

if __name__ == "__main__":
    main()
