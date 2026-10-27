import os
import platform
import sys
import shutil
import subprocess
from typing import Dict, Any
from app.tools.base import BaseTool
from app.security.permissions import PermissionLevel

class SystemInfoTool(BaseTool):
    @property
    def name(self) -> str:
        return "system_info"

    @property
    def description(self) -> str:
        return "Get safe specifications about the host computer (OS, CPU, RAM, GPU, Python, Node, Git, Docker, and disk space)."

    @property
    def permission_level(self) -> PermissionLevel:
        return PermissionLevel.READ_ONLY

    @property
    def risk_classification(self) -> str:
        return "LOW"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "os": {"type": "string"},
                "platform": {"type": "string"},
                "cpu": {"type": "string"},
                "cpu_cores": {"type": "integer"},
                "ram_total_gb": {"type": "number"},
                "ram_free_gb": {"type": "number"},
                "gpu": {"type": "string"},
                "python_version": {"type": "string"},
                "node_version": {"type": "string"},
                "git_version": {"type": "string"},
                "docker_version": {"type": "string"},
                "docker_daemon_running": {"type": "boolean"},
                "wsl_status": {"type": "string"},
                "workspace_disk_total_gb": {"type": "number"},
                "workspace_disk_free_gb": {"type": "number"}
            }
        }

    @property
    def is_synchronous(self) -> bool:
        return True

    async def execute(self, **kwargs) -> Any:
        import asyncio
        return await asyncio.to_thread(self._execute_sync, **kwargs)

    def _execute_sync(self, **kwargs) -> Any:
        info = {}
        
        # 1. OS Info
        info["os"] = f"{platform.system()} {platform.release()} (version {platform.version()})"
        info["platform"] = platform.platform()
        
        # 2. CPU Info
        info["cpu"] = platform.processor()
        info["cpu_cores"] = os.cpu_count()
        
        # 3. RAM Info
        # On Windows, retrieve total/free memory using WMIC
        if platform.system() == "Windows":
            try:
                # Get Total Physical Memory (bytes)
                total_mem_out = subprocess.check_output(
                    "wmic ComputerSystem get TotalPhysicalMemory", 
                    shell=True, text=True, stderr=subprocess.DEVNULL
                )
                total_bytes = int([line.strip() for line in total_mem_out.splitlines() if line.strip() and line.strip().isdigit()][0])
                info["ram_total_gb"] = round(total_bytes / (1024**3), 2)
                
                # Get Free Physical Memory (KB)
                free_mem_out = subprocess.check_output(
                    "wmic OS get FreePhysicalMemory", 
                    shell=True, text=True, stderr=subprocess.DEVNULL
                )
                free_kb = int([line.strip() for line in free_mem_out.splitlines() if line.strip() and line.strip().isdigit()][0])
                info["ram_free_gb"] = round((free_kb * 1024) / (1024**3), 2)
            except Exception:
                info["ram_total_gb"] = "Unknown (WMIC failed)"
                info["ram_free_gb"] = "Unknown"
        else:
            info["ram_total_gb"] = "Unknown (Unsupported OS)"
            info["ram_free_gb"] = "Unknown"

        # 4. GPU Info
        # On Windows, try checking for graphics cards using WMIC
        if platform.system() == "Windows":
            try:
                gpu_out = subprocess.check_output(
                    "wmic path win32_VideoController get name", 
                    shell=True, text=True, stderr=subprocess.DEVNULL
                )
                gpu_names = [line.strip() for line in gpu_out.splitlines() if line.strip() and "name" not in line.lower()]
                info["gpu"] = ", ".join(gpu_names) if gpu_names else "None detected"
            except Exception:
                info["gpu"] = "Unknown"
        else:
            info["gpu"] = "Unknown"

        # 5. Software Versions
        info["python_version"] = sys.version.split()[0]
        
        # Check Node.js version
        try:
            node_ver = subprocess.check_output(
                ["node", "--version"], 
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            info["node_version"] = node_ver
        except Exception:
            info["node_version"] = "Not installed or not in PATH"

        # Check Git version
        try:
            git_ver = subprocess.check_output(
                ["git", "--version"], 
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            info["git_version"] = git_ver
        except Exception:
            info["git_version"] = "Not installed or not in PATH"

        # Check Docker status
        try:
            docker_ver = subprocess.check_output(
                ["docker", "--version"], 
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            info["docker_version"] = docker_ver
            
            # Check if docker daemon is running
            subprocess.check_call(
                ["docker", "info"], 
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            info["docker_daemon_running"] = True
        except Exception:
            info["docker_version"] = "Not installed or not in PATH"
            info["docker_daemon_running"] = False

        # 6. Safe Workspace Disk Space
        try:
            # Query disk space of current workspace drive
            total, used, free = shutil.disk_usage(".")
            info["workspace_disk_total_gb"] = round(total / (1024**3), 2)
            info["workspace_disk_free_gb"] = round(free / (1024**3), 2)
        except Exception:
            pass

        # 7. WSL Status Check
        if platform.system() == "Windows":
            try:
                # Run wsl.exe --list --running safely
                wsl_out = subprocess.check_output(
                    ["wsl.exe", "--list", "--running"],
                    text=True, stderr=subprocess.DEVNULL
                ).strip()
                info["wsl_status"] = wsl_out if wsl_out else "Installed, none running"
            except Exception:
                info["wsl_status"] = "Not installed or not in PATH"
        else:
            info["wsl_status"] = "Not applicable"

        return info

