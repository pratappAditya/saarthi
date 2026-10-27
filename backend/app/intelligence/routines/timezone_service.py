"""
Timezone & Missed-Run Service (Phase 9 - Advanced Automation 2.0).
Provides explicit timezone handling, DST accommodation, and policies
for missed runs when the host system was offline.
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Python 3.8 fallback
    from backports.zoneinfo import ZoneInfo

from app.intelligence.routines.routine_model import MissedRunPolicy

logger = logging.getLogger("app.intelligence.timezone_service")


class TimezoneService:
    @staticmethod
    def get_user_now(tz_str: str = "UTC") -> datetime:
        """Returns the current datetime in the user's explicit timezone."""
        try:
            tz = ZoneInfo(tz_str)
            return datetime.now(tz)
        except Exception:
            return datetime.now(timezone.utc)

    @staticmethod
    def to_user_time(epoch_seconds: float, tz_str: str = "UTC") -> datetime:
        """Converts UTC epoch seconds to user timezone datetime."""
        dt = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
        try:
            tz = ZoneInfo(tz_str)
            return dt.astimezone(tz)
        except Exception:
            return dt

    @staticmethod
    def calculate_next_run(
        schedule: Dict[str, Any],
        user_tz_str: str = "UTC",
        after_timestamp: Optional[float] = None
    ) -> float:
        """
        Calculates the next execution timestamp (UTC epoch seconds)
        based on the user's timezone and schedule specification.
        """
        base_time = after_timestamp or time.time()
        base_dt = datetime.fromtimestamp(base_time, tz=timezone.utc)

        try:
            user_tz = ZoneInfo(user_tz_str)
            user_dt = base_dt.astimezone(user_tz)
        except Exception:
            user_tz = timezone.utc
            user_dt = base_dt

        freq = schedule.get("frequency", "daily").lower()
        time_of_day = schedule.get("time_of_day", "09:00")
        try:
            target_h, target_m = map(int, time_of_day.split(":"))
        except Exception:
            target_h, target_m = 9, 0

        if freq == "once":
            # One-time future timestamp or immediate
            run_at = schedule.get("run_at")
            if run_at:
                try:
                    dt = datetime.fromisoformat(run_at)
                    return dt.timestamp()
                except Exception:
                    pass
            return base_time + 60.0

        elif freq == "interval":
            interval_secs = float(schedule.get("interval_seconds", 3600))
            return base_time + max(60.0, interval_secs)

        elif freq == "daily":
            candidate = user_dt.replace(hour=target_h, minute=target_m, second=0, microsecond=0)
            if candidate <= user_dt:
                candidate += timedelta(days=1)
            return candidate.astimezone(timezone.utc).timestamp()

        elif freq == "weekly":
            day_str = schedule.get("day_of_week", "monday").lower()
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            target_weekday = days.index(day_str) if day_str in days else 0

            candidate = user_dt.replace(hour=target_h, minute=target_m, second=0, microsecond=0)
            days_ahead = (target_weekday - user_dt.weekday()) % 7
            if days_ahead == 0 and candidate <= user_dt:
                days_ahead = 7
            candidate += timedelta(days=days_ahead)
            return candidate.astimezone(timezone.utc).timestamp()

        elif freq == "monthly":
            # Runs on day of month (e.g. 1st)
            target_day = int(schedule.get("day_of_month", 1))
            candidate = user_dt.replace(day=min(target_day, 28), hour=target_h, minute=target_m, second=0, microsecond=0)
            if candidate <= user_dt:
                # Next month
                month = user_dt.month + 1 if user_dt.month < 12 else 1
                year = user_dt.year if user_dt.month < 12 else user_dt.year + 1
                candidate = candidate.replace(year=year, month=month)
            return candidate.astimezone(timezone.utc).timestamp()

        # Default fallback
        return base_time + 86400.0

    @staticmethod
    def evaluate_missed_run(
        last_scheduled: float,
        policy: MissedRunPolicy,
        now: Optional[float] = None
    ) -> Tuple[bool, str]:
        """
        Determines action when a routine's scheduled timestamp has passed while offline.
        Returns (should_run, explanation).
        """
        cur = now or time.time()
        if last_scheduled >= cur:
            return False, "Not missed; schedule is in the future."

        elapsed_hours = (cur - last_scheduled) / 3600.0

        if policy == MissedRunPolicy.SKIP:
            return False, f"Missed run ({elapsed_hours:.1f}h ago) skipped per policy 'SKIP'."
        elif policy == MissedRunPolicy.RUN_ONCE_AFTER_START:
            return True, f"Running missed execution once on recovery ({elapsed_hours:.1f}h late)."
        elif policy == MissedRunPolicy.CATCH_UP:
            return True, f"Running catch-up execution ({elapsed_hours:.1f}h late)."
        elif policy == MissedRunPolicy.ASK_USER:
            return False, f"Policy 'ASK_USER': pending user confirmation to execute missed run ({elapsed_hours:.1f}h late)."
        return False, "Unknown policy."


timezone_service = TimezoneService()
