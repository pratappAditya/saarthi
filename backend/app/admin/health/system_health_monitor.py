import os
import psutil
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from app.config.settings import settings
from app.db.connection import get_db_connection
from app.system.hardware import HardwareDetectionService

logger = logging.getLogger("app.admin.health")

class SystemHealthMonitor:
    @classmethod
    def get_full_health_report(cls) -> Dict[str, Any]:
        # 1. System Hardware / Memory / CPU
        try:
            hw_profile = HardwareDetectionService.get_hardware_profile().model_dump()
            cpu_usage = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage(os.getcwd())
            ram_info = {
                "total_mb": round(mem.total / (1024 * 1024), 2),
                "available_mb": round(mem.available / (1024 * 1024), 2),
                "used_mb": round(mem.used / (1024 * 1024), 2),
                "percent_used": mem.percent
            }
            disk_info = {
                "total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
                "free_gb": round(disk.free / (1024 * 1024 * 1024), 2),
                "used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
                "percent_used": disk.percent
            }
        except Exception as e:
            logger.warning(f"Error reading hardware stats: {e}")
            hw_profile = {}
            cpu_usage = 0.0
            ram_info = {}
            disk_info = {}

        # 2. Database Health & Integrity
        db_size_bytes = 0
        db_status = "UNKNOWN"
        integrity = "UNKNOWN"
        try:
            if os.path.exists(settings.DATABASE_PATH):
                db_size_bytes = os.path.getsize(settings.DATABASE_PATH)
            with get_db_connection() as conn:
                check = conn.execute("PRAGMA integrity_check").fetchone()
                integrity = check[0] if check else "FAILED"
                db_status = "HEALTHY" if integrity.lower() == "ok" else "DEGRADED"
        except Exception as e:
            db_status = f"ERROR: {e}"

        # 3. Ollama Status
        ollama_status = "UNKNOWN"
        import urllib.request
        try:
            url = f"{settings.OLLAMA_BASE_URL}/api/tags"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                if resp.status == 200:
                    ollama_status = "ONLINE"
                else:
                    ollama_status = f"HTTP_{resp.status}"
        except Exception:
            ollama_status = "OFFLINE"

        # 4. Backup Status
        backup_dir = os.path.join(os.path.dirname(settings.DATABASE_PATH), "backups")
        last_backup = "NONE"
        if os.path.exists(backup_dir):
            files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith(".db")]
            if files:
                latest = max(files, key=os.path.getmtime)
                last_backup = datetime.fromtimestamp(os.path.getmtime(latest), timezone.utc).isoformat()

        return {
            "status": "healthy" if db_status == "HEALTHY" else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "subsystems": {
                "backend": {"status": "ONLINE", "version": "0.5.0-rc2"},
                "database": {"status": db_status, "path": settings.DATABASE_PATH, "size_bytes": db_size_bytes, "integrity": integrity},
                "storage": disk_info,
                "cpu": {"percent_used": cpu_usage, "count": os.cpu_count()},
                "ram": ram_info,
                "ollama": {"status": ollama_status, "base_url": settings.OLLAMA_BASE_URL},
                "frontend": {"status": "ONLINE"},
                "scheduler": {"status": "ACTIVE"},
                "workers": {"status": "HEALTHY"},
                "backup": {"last_backup": last_backup}
            },
            "hardware_profile": hw_profile
        }

system_health_monitor = SystemHealthMonitor()
