import logging
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from app.intelligence.planning.task_store import task_store
from app.intelligence.tools.tool_registry import ToolRegistry
from app.intelligence.permissions.permission_engine import permission_engine
from app.admin.audit.admin_audit_service import admin_audit_service
from app.admin.repositories.admin_repository import AdminRepository

logger = logging.getLogger("app.admin.services.agent_ops")

class AgentOperationsService:
    @classmethod
    def list_tasks(cls, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        tasks = task_store.list_tasks()
        if status_filter:
            tasks = [t for t in tasks if t.get("status", "").lower() == status_filter.lower()]
        return tasks

    @classmethod
    def get_task_diagnostics(cls, task_id: str) -> Dict[str, Any]:
        task = task_store.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")

        steps = task_store.get_task_steps(task_id)
        return {
            "task": task,
            "steps_count": len(steps),
            "steps": steps,
            "status": task.get("status"),
            "error_detail": task.get("error")
        }

    @classmethod
    def cancel_task(cls, task_id: str, admin_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        task = task_store.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")

        prev_state = {"status": task.get("status")}
        from app.intelligence.planning.planner import planner_service
        cancelled = planner_service.cancel_task(task_id)

        resulting_state = {"status": "cancelled"}
        admin_audit_service.record_event(
            admin_id=admin_id,
            action="CANCEL_AGENT_TASK",
            target=task_id,
            reason=reason or "Force-cancelled by admin",
            previous_state=prev_state,
            resulting_state=resulting_state
        )

        return {"task_id": task_id, "cancelled": bool(cancelled), "status": "cancelled"}

    @classmethod
    def recover_task(cls, task_id: str, admin_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        task = task_store.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")

        prev_state = {"status": task.get("status")}
        task_store.update_task_status(task_id, "in_progress")
        updated = task_store.get_task(task_id)

        admin_audit_service.record_event(
            admin_id=admin_id,
            action="RECOVER_AGENT_TASK",
            target=task_id,
            reason=reason or "Task recovered/resumed",
            previous_state=prev_state,
            resulting_state={"status": "in_progress"}
        )

        return {"task_id": task_id, "recovered": True, "task": updated}

    @classmethod
    def list_pending_permissions(cls) -> List[Dict[str, Any]]:
        pending = permission_engine.list_pending_permissions()
        return [p.model_dump() for p in pending]

    @classmethod
    def process_permission_action(cls, req_id: str, action: str, admin_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        if action.lower() == "approve":
            res = permission_engine.grant_permission(req_id)
            action_code = "APPROVE_AGENT_PERMISSION"
        else:
            res = permission_engine.deny_permission(req_id)
            action_code = "DENY_AGENT_PERMISSION"

        if not res:
            raise HTTPException(status_code=404, detail=f"Permission request '{req_id}' not found.")

        admin_audit_service.record_event(
            admin_id=admin_id,
            action=action_code,
            target=req_id,
            reason=reason or f"Permission request {action}d",
            resulting_state={"action": action, "granted": action.lower() == "approve"}
        )

        return {"request_id": req_id, "action": action, "permission": res.model_dump()}

agent_ops_service = AgentOperationsService()
