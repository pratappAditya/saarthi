import os
import json
import sqlite3
import logging
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.intelligence.routines.routine_model import (
    Routine,
    RoutineScope,
    TriggerType,
    AutonomyLevel,
    ApprovalPolicy,
    MissedRunPolicy,
    RoutineStatus,
    RoutineCondition,
    RoutineAction,
    RoutineNotification,
    RoutineExecution
)

from app.db.connection import get_db_connection
from app.config.settings import settings

logger = logging.getLogger("app.intelligence.routine_store")

class RoutineStore:
    def __init__(self, db_path: Optional[Any] = None):
        self._db_path = db_path
        self._init_db()

    @property
    def db_path(self) -> Path:
        p = self._db_path or settings.DATABASE_PATH
        return Path(p) if isinstance(p, (str, Path)) else Path(settings.DATABASE_PATH)

    @db_path.setter
    def db_path(self, val: Any):
        self._db_path = val

    def _get_connection(self):
        return get_db_connection(str(self.db_path))

    def _init_db(self):
        with self._get_connection() as conn:
            # Table: routines
            conn.execute("""
            CREATE TABLE IF NOT EXISTS routines (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                natural_language_definition TEXT,
                owner_user_id TEXT NOT NULL,
                scope TEXT NOT NULL,
                project_id TEXT,
                domain TEXT NOT NULL,
                trigger_type TEXT NOT NULL,
                schedule TEXT,
                timezone TEXT,
                conditions TEXT,
                actions TEXT,
                execution_policy TEXT,
                approval_policy TEXT,
                retry_policy TEXT,
                notification_policy TEXT,
                missed_run_policy TEXT,
                autonomy_level TEXT NOT NULL,
                status TEXT NOT NULL,
                enabled INTEGER NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                next_run_at REAL,
                last_run_at REAL,
                last_status TEXT,
                failure_count INTEGER DEFAULT 0,
                metadata TEXT
            )
            """)

            # Table: routine_executions
            conn.execute("""
            CREATE TABLE IF NOT EXISTS routine_executions (
                execution_id TEXT PRIMARY KEY,
                routine_id TEXT NOT NULL,
                started_at REAL NOT NULL,
                completed_at REAL,
                trigger_type TEXT NOT NULL,
                status TEXT NOT NULL,
                task_graph TEXT,
                actions_attempted TEXT,
                tools_used TEXT,
                approval_requests TEXT,
                result TEXT,
                verification_status TEXT,
                failure_reason TEXT,
                retry_count INTEGER DEFAULT 0,
                FOREIGN KEY (routine_id) REFERENCES routines (id) ON DELETE CASCADE
            )
            """)

            # Table: unified_automations (Phase 9)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS unified_automations (
                automation_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                user_id TEXT NOT NULL,
                organization_id TEXT,
                scope TEXT NOT NULL,
                project_id TEXT,
                goal_id TEXT,
                domain TEXT NOT NULL,
                trigger_json TEXT NOT NULL,
                conditions_json TEXT NOT NULL,
                steps_json TEXT NOT NULL,
                schedule_json TEXT NOT NULL,
                timezone TEXT NOT NULL,
                enabled INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                next_run_at REAL,
                last_run_at REAL,
                metadata_json TEXT
            );
            """)

            # Table: automation_checkpoints (Phase 9)
            conn.execute("""
            CREATE TABLE IF NOT EXISTS automation_checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                automation_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                step_index INTEGER NOT NULL,
                step_id TEXT NOT NULL,
                completed_steps_json TEXT NOT NULL,
                step_outputs_json TEXT NOT NULL,
                variables_json TEXT NOT NULL,
                timestamp REAL NOT NULL,
                verification_status TEXT NOT NULL
            );
            """)
            conn.commit()

    def create_routine(self, routine: Routine) -> Routine:
        with self._get_connection() as conn:
            conn.execute("""
            INSERT INTO routines (
                id, name, description, natural_language_definition, owner_user_id,
                scope, project_id, domain, trigger_type, schedule, timezone,
                conditions, actions, execution_policy, approval_policy, retry_policy,
                notification_policy, missed_run_policy, autonomy_level, status, enabled,
                created_at, updated_at, next_run_at, last_run_at, last_status,
                failure_count, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                routine.id,
                routine.name,
                routine.description,
                routine.natural_language_definition,
                routine.owner_user_id,
                routine.scope.value if isinstance(routine.scope, RoutineScope) else routine.scope,
                routine.project_id,
                routine.domain,
                routine.trigger_type.value if isinstance(routine.trigger_type, TriggerType) else routine.trigger_type,
                json.dumps(routine.schedule),
                routine.timezone,
                json.dumps([c.model_dump() for c in routine.conditions]),
                json.dumps([a.model_dump() for a in routine.actions]),
                json.dumps(routine.execution_policy),
                routine.approval_policy.value if isinstance(routine.approval_policy, ApprovalPolicy) else routine.approval_policy,
                json.dumps(routine.retry_policy),
                json.dumps(routine.notification_policy.model_dump()),
                routine.missed_run_policy.value if isinstance(routine.missed_run_policy, MissedRunPolicy) else routine.missed_run_policy,
                routine.autonomy_level.value if isinstance(routine.autonomy_level, AutonomyLevel) else routine.autonomy_level,
                routine.status.value if isinstance(routine.status, RoutineStatus) else routine.status,
                1 if routine.enabled else 0,
                routine.created_at,
                routine.updated_at,
                routine.next_run_at,
                routine.last_run_at,
                routine.last_status,
                routine.failure_count,
                json.dumps(routine.metadata)
            ))
            conn.commit()
        return routine

    def get_routine(self, routine_id: str) -> Optional[Routine]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM routines WHERE id = ?", (routine_id,)).fetchone()
            if not row:
                return None
            return self._row_to_routine(row)

    def list_routines(
        self,
        user_id: Optional[str] = None,
        scope: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> List[Routine]:
        with self._get_connection() as conn:
            query = "SELECT * FROM routines WHERE 1=1"
            params = []
            if user_id:
                query += " AND owner_user_id = ?"
                params.append(user_id)
            if scope:
                query += " AND scope = ?"
                params.append(scope)
            if project_id:
                query += " AND project_id = ?"
                params.append(project_id)
                query += " AND project_id = ?"
                params.append(project_id)

            query += " ORDER BY created_at DESC"
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_routine(r) for r in rows]

    def update_routine(self, routine: Routine) -> Routine:
        routine.updated_at = time.time()
        with self._get_connection() as conn:
            conn.execute("""
            UPDATE routines SET
                name = ?, description = ?, natural_language_definition = ?,
                scope = ?, project_id = ?, domain = ?, trigger_type = ?,
                schedule = ?, timezone = ?, conditions = ?, actions = ?,
                execution_policy = ?, approval_policy = ?, retry_policy = ?,
                notification_policy = ?, missed_run_policy = ?, autonomy_level = ?,
                status = ?, enabled = ?, updated_at = ?, next_run_at = ?,
                last_run_at = ?, last_status = ?, failure_count = ?, metadata = ?
            WHERE id = ?
            """, (
                routine.name,
                routine.description,
                routine.natural_language_definition,
                routine.scope.value if isinstance(routine.scope, RoutineScope) else routine.scope,
                routine.project_id,
                routine.domain,
                routine.trigger_type.value if isinstance(routine.trigger_type, TriggerType) else routine.trigger_type,
                json.dumps(routine.schedule),
                routine.timezone,
                json.dumps([c.model_dump() for c in routine.conditions]),
                json.dumps([a.model_dump() for a in routine.actions]),
                json.dumps(routine.execution_policy),
                routine.approval_policy.value if isinstance(routine.approval_policy, ApprovalPolicy) else routine.approval_policy,
                json.dumps(routine.retry_policy),
                json.dumps(routine.notification_policy.model_dump()),
                routine.missed_run_policy.value if isinstance(routine.missed_run_policy, MissedRunPolicy) else routine.missed_run_policy,
                routine.autonomy_level.value if isinstance(routine.autonomy_level, AutonomyLevel) else routine.autonomy_level,
                routine.status.value if isinstance(routine.status, RoutineStatus) else routine.status,
                1 if routine.enabled else 0,
                routine.updated_at,
                routine.next_run_at,
                routine.last_run_at,
                routine.last_status,
                routine.failure_count,
                json.dumps(routine.metadata),
                routine.id
            ))
            conn.commit()
        return routine

    def delete_routine(self, routine_id: str) -> bool:
        with self._get_connection() as conn:
            res = conn.execute("DELETE FROM routines WHERE id = ?", (routine_id,))
            conn.commit()
            return res.rowcount > 0

    def set_routine_status(self, routine_id: str, status: RoutineStatus, enabled: bool) -> bool:
        with self._get_connection() as conn:
            res = conn.execute(
                "UPDATE routines SET status = ?, enabled = ?, updated_at = ? WHERE id = ?",
                (status.value, 1 if enabled else 0, time.time(), routine_id)
            )
            conn.commit()
            return res.rowcount > 0

    def record_execution(self, execution: RoutineExecution) -> RoutineExecution:
        with self._get_connection() as conn:
            conn.execute("""
            INSERT INTO routine_executions (
                execution_id, routine_id, started_at, completed_at, trigger_type,
                status, task_graph, actions_attempted, tools_used, approval_requests,
                result, verification_status, failure_reason, retry_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                execution.execution_id,
                execution.routine_id,
                execution.started_at,
                execution.completed_at,
                execution.trigger,
                execution.status,
                json.dumps(execution.task_graph) if execution.task_graph else None,
                json.dumps(execution.actions_attempted),
                json.dumps(execution.tools_used),
                json.dumps(execution.approval_requests),
                json.dumps(execution.result) if execution.result else None,
                execution.verification_status,
                execution.failure_reason,
                execution.retry_count
            ))
            conn.commit()
        return execution

    def update_execution(self, execution: RoutineExecution) -> RoutineExecution:
        with self._get_connection() as conn:
            conn.execute("""
            UPDATE routine_executions SET
                completed_at = ?, status = ?, task_graph = ?, actions_attempted = ?,
                tools_used = ?, approval_requests = ?, result = ?, verification_status = ?,
                failure_reason = ?, retry_count = ?
            WHERE execution_id = ?
            """, (
                execution.completed_at,
                execution.status,
                json.dumps(execution.task_graph) if execution.task_graph else None,
                json.dumps(execution.actions_attempted),
                json.dumps(execution.tools_used),
                json.dumps(execution.approval_requests),
                json.dumps(execution.result) if execution.result else None,
                execution.verification_status,
                execution.failure_reason,
                execution.retry_count,
                execution.execution_id
            ))
            conn.commit()
        return execution

    def list_executions(self, routine_id: Optional[str] = None, limit: int = 50) -> List[RoutineExecution]:
        with self._get_connection() as conn:
            query = "SELECT * FROM routine_executions"
            params = []
            if routine_id:
                query += " WHERE routine_id = ?"
                params.append(routine_id)
            query += " ORDER BY started_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [self._row_to_execution(r) for r in rows]

    def get_due_routines(self, current_time: float) -> List[Routine]:
        with self._get_connection() as conn:
            rows = conn.execute("""
            SELECT * FROM routines
            WHERE enabled = 1 AND status = 'ACTIVE'
            AND next_run_at IS NOT NULL AND next_run_at <= ?
            """, (current_time,)).fetchall()
            return [self._row_to_routine(r) for r in rows]

    def reset_all(self, user_id: str = "default_local_user"):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM routine_executions")
            conn.execute("DELETE FROM routines WHERE owner_user_id = ?", (user_id,))
            conn.commit()

    def _row_to_routine(self, r) -> Routine:
        cond_raw = json.loads(r["conditions"]) if r["conditions"] else []
        act_raw = json.loads(r["actions"]) if r["actions"] else []
        notif_raw = json.loads(r["notification_policy"]) if r["notification_policy"] else {}

        return Routine(
            id=r["id"],
            name=r["name"],
            description=r["description"] or "",
            natural_language_definition=r["natural_language_definition"],
            owner_user_id=r["owner_user_id"],
            scope=RoutineScope(r["scope"]),
            project_id=r["project_id"],
            domain=r["domain"],
            trigger_type=TriggerType(r["trigger_type"]),
            schedule=json.loads(r["schedule"]) if r["schedule"] else {},
            timezone=r["timezone"] or "UTC",
            conditions=[RoutineCondition(**c) for c in cond_raw],
            actions=[RoutineAction(**a) for a in act_raw],
            execution_policy=json.loads(r["execution_policy"]) if r["execution_policy"] else {},
            approval_policy=ApprovalPolicy(r["approval_policy"]),
            retry_policy=json.loads(r["retry_policy"]) if r["retry_policy"] else {},
            notification_policy=RoutineNotification(**notif_raw),
            missed_run_policy=MissedRunPolicy(r["missed_run_policy"]),
            autonomy_level=AutonomyLevel(r["autonomy_level"]),
            status=RoutineStatus(r["status"]),
            enabled=bool(r["enabled"]),
            created_at=r["created_at"],
            updated_at=r["updated_at"],
            next_run_at=r["next_run_at"],
            last_run_at=r["last_run_at"],
            last_status=r["last_status"],
            failure_count=r["failure_count"] or 0,
            metadata=json.loads(r["metadata"]) if r["metadata"] else {}
        )

    def _row_to_execution(self, r) -> RoutineExecution:
        return RoutineExecution(
            execution_id=r["execution_id"],
            routine_id=r["routine_id"],
            started_at=r["started_at"],
            completed_at=r["completed_at"],
            trigger=r["trigger_type"],
            status=r["status"],
            task_graph=json.loads(r["task_graph"]) if r["task_graph"] else None,
            actions_attempted=json.loads(r["actions_attempted"]) if r["actions_attempted"] else [],
            tools_used=json.loads(r["tools_used"]) if r["tools_used"] else [],
            approval_requests=json.loads(r["approval_requests"]) if r["approval_requests"] else [],
            result=json.loads(r["result"]) if r["result"] else None,
            verification_status=r["verification_status"] or "VERIFIED",
            failure_reason=r["failure_reason"],
            retry_count=r["retry_count"] or 0
        )

routine_store = RoutineStore()
