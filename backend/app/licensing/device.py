import os
import platform
import uuid
import hashlib
import subprocess
from typing import Dict, Any, Optional

def get_hardware_identifiers() -> Dict[str, str]:
    info = {}
    system = platform.system()
    info["system"] = system
    info["machine"] = platform.machine()
    info["processor"] = platform.processor()
    
    # Node MAC address hash
    info["mac_hash"] = str(uuid.getnode())
    
    if system == "Windows":
        try:
            # Motherboard UUID via wmic/powershell
            cmd = "wmic csproduct get uuid"
            output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
            lines = [line.strip() for line in output.splitlines() if line.strip()]
            if len(lines) > 1:
                info["board_uuid"] = lines[1]
        except Exception:
            pass
            
        try:
            # OS MachineGuid from Registry
            import winreg
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            guid, _ = winreg.QueryValueEx(registry_key, "MachineGuid")
            winreg.CloseKey(registry_key)
            info["machine_guid"] = guid
        except Exception:
            pass
            
    elif system == "Linux":
        try:
            if os.path.exists("/etc/machine-id"):
                with open("/etc/machine-id", "r") as f:
                    info["machine_guid"] = f.read().strip()
        except Exception:
            pass

    return info

def get_device_fingerprint(custom_info: Optional[Dict[str, Any]] = None) -> str:
    raw = custom_info if custom_info is not None else get_hardware_identifiers()
    
    # Sort keys for deterministic hash computation
    sorted_pairs = sorted([(str(k), str(v)) for k, v in raw.items()])
    combined = "|".join([f"{k}:{v}" for k, v in sorted_pairs])
    
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()
