import logging
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from app.intelligence.routines.routine_store import routine_store
from app.admin.audit.admin_audit_service import admin_audit_service

logger = logging.getLogger("app.admin.services.automation_ops")

class AutomationOperationsService:
    @classmethod
    def list_routines(cls) -> Dict[str, Any]:
        routines = [r.model_dump() for r in routine_store.list_routines()]
        active_count = len([r for r in routines if r.get("enabled", True)])
        return {
            "status": "success",
            "total_routines": len(routines),
            "active_routines": active_count,
            "scheduler_health": "ONLINE",
            "worker_health": "HEALTHY",
            "routines": routines
        }

    @classmethod
    def toggle_routine(cls, routine_id: str, admin_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        r = routine_store.get_routine(routine_id)
        if not r:
            raise HTTPException(status_code=404, detail=f"Routine '{routine_id}' not found.")

        prev_state = {"enabled": r.enabled}
        if r.enabled:
            r_up = routine_store.pause_routine(routine_id)
            action_code = "PAUSE_ROUTINE"
        else:
            r_up = routine_store.resume_routine(routine_id)
            action_code = "RESUME_ROUTINE"

        res_dict = r_up.model_dump() if r_up else {}
        admin_audit_service.record_event(
            admin_id=admin_id,
            action=action_code,
            target=routine_id,
            reason=reason or f"Routine toggled by admin",
            previous_state=prev_state,
            resulting_state={"enabled": res_dict.get("enabled")}
        )

        return {"routine_id": routine_id, "routine": res_dict}

automation_ops_service = AutomationOperationsService()
