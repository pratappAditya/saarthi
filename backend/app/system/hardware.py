"""
Hardware Detection & Capability System for Saarthi Nemotron Tiers.
Detects local system specifications (CPU, RAM, GPU, VRAM, Storage, OS) with 100% local privacy.
Produces normalized HardwareProfile and CompatibilityResult objects.
"""

import os
import platform
import shutil
import subprocess
import logging
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger("app.system.hardware")


class CompatibilityStatus(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    RECOMMENDED = "RECOMMENDED"
    MINIMUM_ONLY = "MINIMUM_ONLY"
    INSUFFICIENT_RAM = "INSUFFICIENT_RAM"
    INSUFFICIENT_VRAM = "INSUFFICIENT_VRAM"
    INSUFFICIENT_STORAGE = "INSUFFICIENT_STORAGE"
    UNSUPPORTED_ARCHITECTURE = "UNSUPPORTED_ARCHITECTURE"
    UNKNOWN_HARDWARE = "UNKNOWN_HARDWARE"

class HardwareProfile(BaseModel):
    os_name: str = "Windows"
    os_version: str
    architecture: str
    cpu_model: str
    cpu_cores: int
    total_ram_gb: float
    available_ram_gb: float
    gpu_vendor: str
    gpu_model: str
    vram_gb: float
    free_storage_gb: float
    ollama_installed: bool = False
    ollama_running: bool = False
    installed_nemotron_models: list[str] = Field(default_factory=list)

class CompatibilityResult(BaseModel):
    status: CompatibilityStatus
    compatible: bool
    recommended: bool
    reason: str
    warnings: list[str] = Field(default_factory=list)

class HardwareDetectionService:
    @staticmethod
    def _get_gpu_details() -> tuple[str, str, float]:
        """
        Detects GPU vendor, model name, and VRAM in GB.
        Returns (vendor, model, vram_gb).
        """
        vendor = "Unknown"
        model = "Integrated / Standard Display Device"
        vram_gb = 0.0

        # Method 1: Check nvidia-smi
        try:
            cmd = ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
            if result.returncode == 0 and result.stdout.strip():
                line = result.stdout.strip().split("\n")[0]
                parts = line.split(",")
                if len(parts) >= 2:
                    model = parts[0].strip()
                    vendor = "NVIDIA"
                    try:
                        vram_mb = float(parts[1].strip())
                        vram_gb = round(vram_mb / 1024.0, 1)
                    except ValueError:
                        pass
                    return vendor, model, vram_gb
        except Exception:
            pass

        # Method 2: Check Windows PowerShell CIM Win32_VideoController
        if platform.system() == "Windows":
            try:
                ps_cmd = "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM | ConvertTo-Json"
                res = subprocess.run(["powershell", "-Command", ps_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
                if res.returncode == 0 and res.stdout.strip():
                    import json
                    data = json.loads(res.stdout)
                    controllers = data if isinstance(data, list) else [data]
                    best_vram = 0
                    best_name = model
                    for ctrl in controllers:
                        name = ctrl.get("Name", "")
                        ram_bytes = ctrl.get("AdapterRAM", 0) or 0
                        if ram_bytes > best_vram:
                            best_vram = ram_bytes
                            best_name = name
                    if best_vram > 0:
                        vram_gb = round(best_vram / (1024.0 ** 3), 1)
                    model = best_name
                    if "nvidia" in model.lower():
                        vendor = "NVIDIA"
                    elif "amd" in model.lower() or "radeon" in model.lower():
                        vendor = "AMD"
                    elif "intel" in model.lower():
                        vendor = "Intel"
            except Exception:
                pass

        return vendor, model, vram_gb

    @classmethod
    def get_hardware_profile(cls) -> HardwareProfile:
        """
        Collects comprehensive HardwareProfile locally.
        Zero data is transmitted externally.
        """
        mem = psutil.virtual_memory()
        total_ram = round(mem.total / (1024.0 ** 3), 1)
        avail_ram = round(mem.available / (1024.0 ** 3), 1)

        total_d, used_d, free_d = shutil.disk_usage(os.getcwd())
        free_storage = round(free_d / (1024.0 ** 3), 1)

        vendor, gpu_model, vram = cls._get_gpu_details()
        cpu_model = platform.processor() or platform.machine() or "x86_64 Processor"
        cpu_cores = os.cpu_count() or 4
        os_ver = f"{platform.system()} {platform.release()} ({platform.version()})"
        arch = platform.machine() or "x64"

        # Basic check for Ollama running locally
        ollama_installed = False
        ollama_running = False
        installed_models = []

        try:
            import httpx
            from app.config.settings import settings
            base_url = settings.OLLAMA_BASE_URL.rstrip('/')
            with httpx.Client(timeout=1.5) as client:
                resp = client.get(f"{base_url}/api/tags")
                if resp.status_code == 200:
                    ollama_installed = True
                    ollama_running = True
                    data = resp.json()
                    installed_models = [m.get("name") for m in data.get("models", [])]
        except Exception:
            pass

        return HardwareProfile(
            os_name=platform.system(),
            os_version=os_ver,
            architecture=arch,
            cpu_model=cpu_model,
            cpu_cores=cpu_cores,
            total_ram_gb=total_ram,
            available_ram_gb=avail_ram,
            gpu_vendor=vendor,
            gpu_model=gpu_model,
            vram_gb=vram,
            free_storage_gb=free_storage,
            ollama_installed=ollama_installed,
            ollama_running=ollama_running,
            installed_nemotron_models=installed_models
        )

    @classmethod
    def detect_capabilities(cls) -> HardwareProfile:
        return cls.get_hardware_profile()
