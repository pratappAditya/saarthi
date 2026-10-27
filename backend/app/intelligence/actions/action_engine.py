import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.intelligence.actions.action_models import ActionItem, ActionStatus
from app.intelligence.tools.tool_executor import tool_executor
from app.intelligence.permissions.permission_engine import permission_engine, PermissionStatus

logger = logging.getLogger("app.intelligence.action_engine")

class ActionEngine:
    @staticmethod
    def execute_action(
        tool_id: str,
        arguments: Dict[str, Any],
        user_id: str = "default_local_user",
        session_id: Optional[str] = None,
        permission_id: Optional[str] = None,
        permission_engine_instance: Optional[Any] = None
    ) -> ActionItem:
        action_id = f"act_{uuid.uuid4().hex[:10]}"
        item = ActionItem(
            action_id=action_id,
            user_id=user_id,
            session_id=session_id,
            tool_id=tool_id,
            arguments=arguments,
            permission_id=permission_id
        )

        eng = permission_engine_instance or permission_engine
        permission_granted = True
        if permission_id:
            perm = eng.get_permission_request(permission_id)
            if not perm or (perm.status.value if hasattr(perm.status, "value") else str(perm.status)) != "approved":
                item.status = ActionStatus.DENIED
                item.error = "Permission denied or not approved."
                return item

        res = tool_executor.execute_tool(
            tool_id=tool_id,
            arguments=arguments,
            user_id=user_id,
            session_id=session_id,
            permission_granted=permission_granted
        )

        if res.get("success"):
            item.status = ActionStatus.COMPLETED
            item.result = res.get("result")
        elif res.get("requires_confirmation"):
            item.status = ActionStatus.AWAITING_CONFIRMATION
            item.error = res.get("message")
        else:
            item.status = ActionStatus.FAILED
            item.error = res.get("message")

        return item

action_engine = ActionEngine()
