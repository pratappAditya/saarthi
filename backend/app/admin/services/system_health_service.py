import logging
from typing import Dict, Any
from app.admin.health.system_health_monitor import system_health_monitor
from app.db.connection import get_db_connection

logger = logging.getLogger("app.admin.services.system_health")

class SystemHealthService:
    @classmethod
    def get_system_health(cls) -> Dict[str, Any]:
        return system_health_monitor.get_full_health_report()

    @classmethod
    def run_database_integrity_check(cls) -> Dict[str, Any]:
        with get_db_connection() as conn:
            res = conn.execute("PRAGMA integrity_check").fetchone()[0]
            return {
                "status": "success",
                "integrity_check_result": res,
                "is_healthy": res.lower() == "ok"
            }

system_health_service = SystemHealthService()
