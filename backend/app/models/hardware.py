"""
Hardware Capability Detection Service for Saarthi.
Detects local system specifications (CPU, RAM, GPU, VRAM, Disk, OS, Architecture)
with 100% offline local privacy guarantees. Zero remote data transmission.
"""

import os
import platform
import shutil
import subprocess
import logging
from typing import Dict, Any, Optional
import psutil

logger = logging.getLogger("app.models.hardware")

class HardwareDetectionService:
    @staticmethod
    def _get_gpu_info() -> Dict[str, Any]:
        """
        Attempts to detect local GPU details using nvidia-smi or Windows WMIC/Get-CimInstance.
        Falls back safely if no dedicated GPU or tool is found.
        """
        gpu_name = "Integrated / Standard Display Device"
        gpu_vendor = "Unknown"
        vram_gb = 0.0

        # Method 1: Check nvidia-smi for NVIDIA GPUs
        try:
            cmd = ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
            if result.returncode == 0 and result.stdout.strip():
                line = result.stdout.strip().split("\n")[0]
                parts = line.split(",")
                if len(parts) >= 2:
                    gpu_name = parts[0].strip()
                    gpu_vendor = "NVIDIA"
                    try:
                        vram_mb = float(parts[1].strip())
                        vram_gb = round(vram_mb / 1024.0, 1)
                    except ValueError:
                        pass
                    return {
                        "gpu": gpu_name,
                        "gpu_vendor": gpu_vendor,
                        "vram_gb": vram_gb
                    }
        except Exception:
            pass

        # Method 2: Check Windows PowerShell CIM for Video Controller
        if platform.system() == "Windows":
            try:
                ps_cmd = (
                    "Get-CimInstance Win32_VideoController | "
                    "Select-Object Name, AdapterRAM | ConvertTo-Json"
                )
                res = subprocess.run(["powershell", "-Command", ps_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=3)
                if res.returncode == 0 and res.stdout.strip():
                    import json
                    data = json.loads(res.stdout)
                    controllers = data if isinstance(data, list) else [data]
                    best_vram = 0
                    best_name = gpu_name
                    for ctrl in controllers:
                        name = ctrl.get("Name", "")
                        ram_bytes = ctrl.get("AdapterRAM", 0) or 0
                        if ram_bytes > best_vram:
                            best_vram = ram_bytes
                            best_name = name
                    
                    if best_vram > 0:
                        vram_gb = round(best_vram / (1024.0 ** 3), 1)
                    gpu_name = best_name
                    if "nvidia" in gpu_name.lower():
                        gpu_vendor = "NVIDIA"
                    elif "amd" in gpu_name.lower() or "radeon" in gpu_name.lower():
                        gpu_vendor = "AMD"
                    elif "intel" in gpu_name.lower():
                        gpu_vendor = "Intel"
            except Exception:
                pass

        return {
            "gpu": gpu_name,
            "gpu_vendor": gpu_vendor,
            "vram_gb": vram_gb
        }

    @classmethod
    def detect_capabilities(cls) -> Dict[str, Any]:
        """
        Collects normalized hardware specs required for Nemotron model selection.
        """
        # CPU
        cpu_model = platform.processor() or platform.machine() or "Unknown CPU"
        cpu_cores = os.cpu_count() or 4

        # System RAM
        mem = psutil.virtual_memory()
        total_ram_gb = round(mem.total / (1024.0 ** 3), 1)
        free_ram_gb = round(mem.available / (1024.0 ** 3), 1)

        # Storage (Disk Space)
        # Target drive where Saarthi/Ollama data resides
        target_path = os.getcwd()
        total_disk, used_disk, free_disk = shutil.disk_usage(target_path)
        disk_free_gb = round(free_disk / (1024.0 ** 3), 1)

        # OS Details
        os_ver = f"{platform.system()} {platform.release()} ({platform.version()})"
        arch = platform.machine() or "x64"

        # GPU Specs
        gpu_info = cls._get_gpu_info()

        capabilities = {
            "cpu": cpu_model,
            "cpu_cores": cpu_cores,
            "ram_gb": total_ram_gb,
            "ram_free_gb": free_ram_gb,
            "gpu": gpu_info["gpu"],
            "gpu_vendor": gpu_info["gpu_vendor"],
            "vram_gb": gpu_info["vram_gb"],
            "architecture": arch,
            "disk_free_gb": disk_free_gb,
            "os_version": os_ver
        }

        logger.info(f"Detected hardware capabilities: {capabilities}")
        return capabilities

    @classmethod
    def get_hardware_profile(cls):
        from app.system.hardware import HardwareDetectionService as SystemHardwareService
        return SystemHardwareService.get_hardware_profile()
