import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.intelligence.routines.routine_model import RoutineNotification

logger = logging.getLogger("app.intelligence.routine_notification_engine")

class RoutineNotificationEngine:
    def __init__(self):
        self.notification_log: List[Dict[str, Any]] = []
        self.quiet_hours_start = 23  # 11 PM
        self.quiet_hours_end = 7     # 7 AM

    def is_quiet_hours(self) -> bool:
        current_hour = datetime.now().hour
        if self.quiet_hours_start > self.quiet_hours_end:
            return current_hour >= self.quiet_hours_start or current_hour < self.quiet_hours_end
        return self.quiet_hours_start <= current_hour < self.quiet_hours_end

    def dispatch_notification(
        self,
        routine_name: str,
        execution_id: str,
        message: str,
        notification_policy: Optional[RoutineNotification] = None,
        user_id: str = "default_local_user"
    ) -> Dict[str, Any]:
        policy = notification_policy or RoutineNotification()

        # Check Quiet Hours
        if self.is_quiet_hours() and not policy.quiet_hours_override:
            logger.info(f"Notification for '{routine_name}' queued due to quiet hours.")
            record = {
                "id": f"notif_{int(time.time()*1000)}",
                "routine_name": routine_name,
                "execution_id": execution_id,
                "user_id": user_id,
                "message": message,
                "channel": "digest",
                "status": "QUEUED_QUIET_HOURS",
                "timestamp": time.time()
            }
            self.notification_log.append(record)
            return record

        record = {
            "id": f"notif_{int(time.time()*1000)}",
            "routine_name": routine_name,
            "execution_id": execution_id,
            "user_id": user_id,
            "message": message,
            "channel": policy.channel,
            "status": "DELIVERED",
            "timestamp": time.time()
        }
        self.notification_log.append(record)
        logger.info(f"Dispatched [{policy.channel.upper()}] notification for routine '{routine_name}': {message}")
        return record

    def get_unread_notifications(self, user_id: str = "default_local_user") -> List[Dict[str, Any]]:
        return [n for n in self.notification_log if n["user_id"] == user_id]

routine_notification_engine = RoutineNotificationEngine()
