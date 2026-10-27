import time
import threading
import logging
from typing import Dict, Any, List, Optional

from app.intelligence.routines.routine_model import Routine, RoutineStatus, MissedRunPolicy
from app.intelligence.routines.routine_store import routine_store, RoutineStore
from app.intelligence.routines.routine_engine import routine_engine, RoutineEngine

logger = logging.getLogger("app.intelligence.routine_scheduler")

class RoutineScheduler:
    """
    Background scheduler for Saarthi Desktop:
    - Persistent polling loop checking due routines in SQLite.
    - Timezone-aware schedule calculation.
    - Restart recovery & missed run policy handling.
    - Execution locking & duplicate prevention.
    """
    def __init__(
        self,
        store: Optional[RoutineStore] = None,
        engine: Optional[RoutineEngine] = None,
        check_interval_seconds: float = 10.0
    ):
        self.store = store or routine_store
        self.engine = engine or routine_engine
        self.check_interval = check_interval_seconds
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._locks: Dict[str, bool] = {}

    def start(self):
        if self._running:
            logger.info("RoutineScheduler is already running.")
            return

        self._running = True
        self._recover_schedules_on_startup()
        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True, name="SaarthiRoutineScheduler")
        self._thread.start()
        logger.info("RoutineScheduler background daemon started successfully.")

    def stop(self):
        if not self._running:
            return
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)
        logger.info("RoutineScheduler stopped.")

    def is_running(self) -> bool:
        return self._running

    def _recover_schedules_on_startup(self):
        """Processes missed run policy and initializes next_run_at on engine restart."""
        try:
            now = time.time()
            routines = self.store.list_routines()

            for rtn in routines:
                if not rtn.enabled or rtn.status != RoutineStatus.ACTIVE:
                    continue

                # Initialize next_run_at if missing
                if rtn.next_run_at is None and rtn.trigger_type == rtn.trigger_type.TIME_TRIGGER:
                    rtn.next_run_at = now + 60.0  # schedule first run in 1 min
                    self.store.update_routine(rtn)
                    continue

                # Handle missed runs
                if rtn.next_run_at and rtn.next_run_at < now:
                    logger.info(f"Missed run detected for routine '{rtn.name}' ({rtn.id}). Policy: {rtn.missed_run_policy.value}")

                    if rtn.missed_run_policy == MissedRunPolicy.SKIP:
                        rtn.next_run_at = now + 3600.0  # advance schedule
                        self.store.update_routine(rtn)

                    elif rtn.missed_run_policy == MissedRunPolicy.RUN_ONCE_AFTER_START:
                        logger.info(f"Executing missed run ONCE on startup for routine '{rtn.name}'.")
                        self.engine.execute_routine(routine_id=rtn.id, trigger_source="MISSED_RUN_RECOVERY")
                        updated = self.store.get_routine(rtn.id)
                        if updated:
                            updated.next_run_at = max(now + 3600.0, updated.next_run_at or (now + 3600.0))
                            self.store.update_routine(updated)

                    elif rtn.missed_run_policy == MissedRunPolicy.CATCH_UP:
                        self.engine.execute_routine(routine_id=rtn.id, trigger_source="MISSED_RUN_CATCHUP")
                        updated = self.store.get_routine(rtn.id)
                        if updated:
                            updated.next_run_at = max(now + 3600.0, updated.next_run_at or (now + 3600.0))
                            self.store.update_routine(updated)

            # Recover Unified Automations
            from app.intelligence.routines.automation_engine import automation_engine
            from app.intelligence.routines.timezone_service import timezone_service

            conn = self.store._get_connection()
            try:
                rows = conn.execute(
                    "SELECT automation_id, user_id FROM unified_automations WHERE enabled = 1 AND status = 'ACTIVE' AND next_run_at IS NOT NULL AND next_run_at < ?",
                    (now,)
                ).fetchall()
                for row in rows:
                    auto_id = row["automation_id"]
                    auto_uid = row["user_id"]
                    auto = automation_engine.get_automation(auto_id, user_id=auto_uid)
                    if not auto:
                        continue
                    logger.info(f"Missed run detected for unified automation '{auto.name}' ({auto.automation_id}). Policy: {auto.missed_run_policy.value}")
                    if auto.missed_run_policy == MissedRunPolicy.SKIP:
                        auto.next_run_at = timezone_service.calculate_next_run(auto.schedule, auto.timezone, after_timestamp=now)
                        automation_engine.register_automation(auto)
                    elif auto.missed_run_policy == MissedRunPolicy.RUN_ONCE_AFTER_START:
                        automation_engine.execute_automation(automation_id=auto_id, trigger_source="MISSED_RUN_RECOVERY", user_id=auto_uid)
                    elif auto.missed_run_policy == MissedRunPolicy.CATCH_UP:
                        automation_engine.execute_automation(automation_id=auto_id, trigger_source="MISSED_RUN_CATCHUP", user_id=auto_uid)
            finally:
                conn.close()

        except Exception as e:
            logger.error(f"Error recovering routine schedules on startup: {e}", exc_info=True)

    def _scheduler_loop(self):
        while self._running:
            try:
                now = time.time()
                due = self.store.get_due_routines(now)

                for rtn in due:
                    if self._locks.get(rtn.id):
                        logger.warning(f"Routine '{rtn.name}' ({rtn.id}) is locked/running. Skipping duplicate trigger.")
                        continue

                    # Lock routine during execution
                    self._locks[rtn.id] = True
                    try:
                        logger.info(f"Scheduler executing due routine '{rtn.name}' ({rtn.id}).")
                        self.engine.execute_routine(routine_id=rtn.id, trigger_source="SCHEDULED_TIMER")
                    finally:
                        self._locks[rtn.id] = False

                # Unified Automations due check
                from app.intelligence.routines.automation_engine import automation_engine
                conn = self.store._get_connection()
                try:
                    due_autos = conn.execute(
                        "SELECT automation_id, user_id, name FROM unified_automations WHERE enabled = 1 AND status = 'ACTIVE' AND next_run_at IS NOT NULL AND next_run_at <= ?",
                        (now,)
                    ).fetchall()
                    for r in due_autos:
                        a_id = r["automation_id"]
                        a_uid = r["user_id"]
                        a_name = r["name"]
                        if self._locks.get(a_id):
                            continue
                        self._locks[a_id] = True
                        try:
                            logger.info(f"Scheduler executing due unified automation '{a_name}' ({a_id}).")
                            automation_engine.execute_automation(automation_id=a_id, trigger_source="SCHEDULED_TIMER", user_id=a_uid)
                        finally:
                            self._locks[a_id] = False
                finally:
                    conn.close()

            except Exception as e:
                logger.error(f"Error in RoutineScheduler loop: {e}", exc_info=True)

            time.sleep(self.check_interval)

routine_scheduler = RoutineScheduler()
