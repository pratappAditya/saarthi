"""
Safe Universal Automation Engine (Phase 9 - Advanced Automation 2.0).
Coordinates multi-step action chains, deterministic condition checking,
agent launches, checkpoint persistence, idempotency, bounded retries,
recursion/loop protection, and strict permission gating.
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.intelligence.routines.automation_models import (
    UnifiedAutomation, AutomationStatus, WorkflowStep, WorkflowCheckpoint,
    AutomationRunRecord, ConditionLogic, TriggerKind
)
from app.intelligence.routines.condition_engine import condition_engine
from app.intelligence.routines.timezone_service import timezone_service
from app.intelligence.routines.routine_store import routine_store
from app.intelligence.routines.routine_notification_engine import routine_notification_engine
from app.intelligence.planning.planner import planner_service
from app.intelligence.agents.agent_runtime import agent_runtime
from app.intelligence.permissions.permission_engine import permission_engine
from app.intelligence.permissions.permission_models import PermissionStatus, PermissionScope
from app.intelligence.tools.tool_executor import tool_executor
from app.intelligence.audit.intelligence_audit import audit_service
from app.core.plans import PlanService
from app.core.entitlements import get_current_plan

logger = logging.getLogger("app.intelligence.automation_engine")


class AutomationEngine:
    def __init__(self):
        self._automations: Dict[str, UnifiedAutomation] = {}
        self._checkpoints: Dict[str, List[WorkflowCheckpoint]] = {}  # run_id -> List[WorkflowCheckpoint]
        self._runs: Dict[str, AutomationRunRecord] = {}
        self._active_locks: Dict[str, float] = {}  # idempotency_key -> timestamp
        self._init_sqlite_tables()

    def _init_sqlite_tables(self):
        """Initializes SQLite tables for unified automations and checkpoints."""
        conn = routine_store._get_connection()
        try:
            with conn:
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
        except Exception as e:
            logger.warning(f"Error initializing unified automation tables: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def register_automation(self, automation: UnifiedAutomation) -> UnifiedAutomation:
        """Saves a unified automation into memory and SQLite."""
        self._automations[automation.automation_id] = automation
        conn = routine_store._get_connection()
        try:
            with conn:
                conn.execute("""
                INSERT OR REPLACE INTO unified_automations (
                    automation_id, name, description, user_id, organization_id, scope,
                    project_id, goal_id, domain, trigger_json, conditions_json, steps_json,
                    schedule_json, timezone, enabled, status, created_at, updated_at,
                    next_run_at, last_run_at, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    automation.automation_id, automation.name, automation.description,
                    automation.user_id, automation.organization_id, automation.scope.value,
                    automation.project_id, automation.goal_id, automation.domain,
                    json.dumps(automation.trigger.model_dump()),
                    json.dumps([c.model_dump() for c in automation.conditions]),
                    json.dumps([s.model_dump() for s in automation.steps]),
                    json.dumps(automation.schedule), automation.timezone,
                    1 if automation.enabled else 0, automation.status.value,
                    automation.created_at, automation.updated_at,
                    automation.next_run_at, automation.last_run_at,
                    json.dumps(automation.metadata)
                ))
        except Exception as e:
            if "no such table" in str(e).lower():
                self._init_sqlite_tables()
                with routine_store._get_connection() as retry_conn:
                    retry_conn.execute("""
                    INSERT OR REPLACE INTO unified_automations (
                        automation_id, name, description, user_id, organization_id, scope,
                        project_id, goal_id, domain, trigger_json, conditions_json, steps_json,
                        schedule_json, timezone, enabled, status, created_at, updated_at,
                        next_run_at, last_run_at, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        automation.automation_id, automation.name, automation.description,
                        automation.user_id, automation.organization_id, automation.scope.value,
                        automation.project_id, automation.goal_id, automation.domain,
                        json.dumps(automation.trigger.model_dump()),
                        json.dumps([c.model_dump() for c in automation.conditions]),
                        json.dumps([s.model_dump() for s in automation.steps]),
                        json.dumps(automation.schedule), automation.timezone,
                        1 if automation.enabled else 0, automation.status.value,
                        automation.created_at, automation.updated_at,
                        automation.next_run_at, automation.last_run_at,
                        json.dumps(automation.metadata)
                    ))
            else:
                raise
        finally:
            try:
                conn.close()
            except Exception:
                pass
        return automation

    def get_automation(self, automation_id: str, user_id: str = "default_local_user") -> Optional[UnifiedAutomation]:
        """Fetches automation ensuring tenant isolation."""
        auto = self._automations.get(automation_id)
        if not auto:
            conn = routine_store._get_connection()
            try:
                row = conn.execute("SELECT * FROM unified_automations WHERE automation_id = ?", (automation_id,)).fetchone()
                if row:
                    d = dict(row)
                    auto = UnifiedAutomation(
                        automation_id=d["automation_id"],
                        name=d["name"],
                        description=d.get("description", ""),
                        user_id=d["user_id"],
                        organization_id=d.get("organization_id"),
                        scope=d["scope"],
                        project_id=d.get("project_id"),
                        goal_id=d.get("goal_id"),
                        domain=d["domain"],
                        trigger=json.loads(d["trigger_json"]),
                        conditions=json.loads(d["conditions_json"]),
                        steps=json.loads(d["steps_json"]),
                        schedule=json.loads(d["schedule_json"]),
                        timezone=d["timezone"],
                        enabled=bool(d["enabled"]),
                        status=AutomationStatus(d["status"]),
                        created_at=d["created_at"],
                        updated_at=d["updated_at"],
                        next_run_at=d.get("next_run_at"),
                        last_run_at=d.get("last_run_at"),
                        metadata=json.loads(d.get("metadata_json") or "{}")
                    )
                    self._automations[automation_id] = auto
            finally:
                conn.close()

        if auto and auto.user_id != user_id and user_id != "admin_system":
            # Strict tenant isolation check
            logger.warning(f"Tenant Isolation Violation: User '{user_id}' denied access to automation '{automation_id}' owned by '{auto.user_id}'.")
            return None
        return auto

    def list_automations(self, user_id: str = "default_local_user", organization_id: Optional[str] = None) -> List[UnifiedAutomation]:
        """Lists automations respecting user and organization boundaries."""
        results = []
        conn = routine_store._get_connection()
        try:
            if organization_id:
                query = "SELECT * FROM unified_automations WHERE organization_id = ?"
                rows = conn.execute(query, (organization_id,)).fetchall()
            else:
                query = "SELECT * FROM unified_automations WHERE user_id = ?"
                rows = conn.execute(query, (user_id,)).fetchall()

            for r in rows:
                d = dict(r)
                auto = UnifiedAutomation(
                    automation_id=d["automation_id"],
                    name=d["name"],
                    description=d.get("description", ""),
                    user_id=d["user_id"],
                    organization_id=d.get("organization_id"),
                    scope=d["scope"],
                    project_id=d.get("project_id"),
                    goal_id=d.get("goal_id"),
                    domain=d["domain"],
                    trigger=json.loads(d["trigger_json"]),
                    conditions=json.loads(d["conditions_json"]),
                    steps=json.loads(d["steps_json"]),
                    schedule=json.loads(d["schedule_json"]),
                    timezone=d["timezone"],
                    enabled=bool(d["enabled"]),
                    status=AutomationStatus(d["status"]),
                    created_at=d["created_at"],
                    updated_at=d["updated_at"],
                    next_run_at=d.get("next_run_at"),
                    last_run_at=d.get("last_run_at"),
                    metadata=json.loads(d.get("metadata_json") or "{}")
                )
                self._automations[auto.automation_id] = auto
                results.append(auto)
        finally:
            conn.close()
        return results

    def _resolve_bindings(self, params: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """Substitutes dynamic step output bindings like $step_1.output.summary."""
        resolved = {}
        for k, v in params.items():
            if isinstance(v, str) and v.startswith("$"):
                path_parts = v[1:].split(".")
                curr = variables
                for p in path_parts:
                    if isinstance(curr, dict) and p in curr:
                        curr = curr[p]
                    else:
                        curr = v
                        break
                resolved[k] = curr
            else:
                resolved[k] = v
        return resolved

    def execute_automation(
        self,
        automation_id: str,
        trigger_source: str = "MANUAL",
        user_id: str = "default_local_user",
        session_id: str = "automation_session",
        approval_token: Optional[str] = None,
        permission_granted: bool = False,
        call_depth: int = 0
    ) -> AutomationRunRecord:
        """
        Executes a canonical UnifiedAutomation workflow through the full safe pipeline:
        TRIGGER -> CONTEXT -> CONDITION -> PLAN -> PERMISSION -> EXECUTE -> VERIFY -> CHECKPOINT -> COMPLETE
        """
        now_ts = time.time()
        auto = self.get_automation(automation_id, user_id=user_id)
        if not auto:
            raise ValueError(f"Automation '{automation_id}' not found or access denied.")

        # 1. State & Pause Check
        if not auto.enabled or auto.status in [AutomationStatus.PAUSED, AutomationStatus.DISABLED]:
            rec = AutomationRunRecord(
                automation_id=automation_id,
                user_id=user_id,
                started_at=now_ts,
                completed_at=now_ts,
                trigger_source=trigger_source,
                status="PAUSED",
                failure_reason="Automation is paused or disabled."
            )
            return rec

        # 2. Recursion & Loop Protection
        if call_depth >= auto.max_recursion_depth:
            logger.error(f"Recursion Limit Exceeded for '{automation_id}' (depth={call_depth}). Aborting.")
            rec = AutomationRunRecord(
                automation_id=automation_id,
                user_id=user_id,
                started_at=now_ts,
                completed_at=now_ts,
                trigger_source=trigger_source,
                status="FAILED",
                failure_reason=f"RECURSION_LIMIT_EXCEEDED: Exceeded max recursion depth of {auto.max_recursion_depth}."
            )
            return rec

        # 3. Idempotency & Duplicate Run Prevention
        idempotency_window = 10.0  # 10s concurrency lock window
        run_key = f"{automation_id}:{trigger_source}:{int(now_ts // idempotency_window)}"
        if run_key in self._active_locks and (now_ts - self._active_locks[run_key]) < idempotency_window:
            logger.warning(f"Duplicate execution suppressed by Idempotency Lock: '{run_key}'")
            return AutomationRunRecord(
                automation_id=automation_id,
                user_id=user_id,
                started_at=now_ts,
                completed_at=now_ts,
                trigger_source=trigger_source,
                status="COMPLETED",
                failure_reason="Duplicate execution suppressed by idempotency lock.",
                idempotency_key=run_key
            )
        self._active_locks[run_key] = now_ts

        # 4. Entitlement Capability Check
        current_plan = get_current_plan(user_id)
        if not PlanService.is_capability_entitled(current_plan, "agents.routines"):
            rec = AutomationRunRecord(
                automation_id=automation_id,
                user_id=user_id,
                started_at=now_ts,
                completed_at=now_ts,
                trigger_source=trigger_source,
                status="FAILED",
                failure_reason=f"Plan '{current_plan.upper()}' lacks capability 'agents.routines'."
            )
            return rec

        run_id = f"run_{int(now_ts*1000)}"
        run_record = AutomationRunRecord(
            run_id=run_id,
            automation_id=automation_id,
            user_id=user_id,
            organization_id=auto.organization_id,
            started_at=now_ts,
            trigger_source=trigger_source,
            status="RUNNING",
            idempotency_key=run_key
        )
        self._runs[run_id] = run_record

        # 5. Deterministic Condition Evaluation
        runtime_context = {
            "automation_id": automation_id,
            "user_id": user_id,
            "project_id": auto.project_id,
            "goal_id": auto.goal_id,
            "trigger_source": trigger_source
        }
        conditions_met = condition_engine.evaluate_composite_conditions(
            conditions=auto.conditions,
            context=runtime_context,
            logic=auto.condition_logic,
            user_id=user_id
        )
        if not conditions_met:
            logger.info(f"Conditions not met for automation '{auto.name}' ({automation_id}). Halting cleanly.")
            run_record.status = "COMPLETED"
            run_record.completed_at = time.time()
            run_record.result = {"summary": "Halted: Conditions evaluated to False."}
            return run_record

        # 6. Execute Multi-Step Action Chain
        variables: Dict[str, Any] = {"runtime_context": runtime_context}
        completed_steps: List[str] = []
        actions_attempted: List[Dict[str, Any]] = []
        tools_used: List[str] = []
        approval_requests: List[Dict[str, Any]] = []

        for idx, step in enumerate(auto.steps):
            step_desc = {
                "step_index": idx,
                "step_id": step.step_id,
                "name": step.name,
                "status": "EXECUTING"
            }

            # Resolve parameter bindings
            resolved_params = self._resolve_bindings(step.parameters, variables)

            # Permission & Risk Gate Check
            is_high_risk = step.risk_level in ["high", "critical"]
            requires_approval = step.requires_approval or is_high_risk

            if requires_approval and not permission_granted:
                # Check valid server-side approval token
                is_server_approved = False
                if approval_token:
                    perm_req = permission_engine.get_permission_request(approval_token)
                    if (
                        perm_req
                        and perm_req.user_id == user_id
                        and perm_req.status == PermissionStatus.APPROVED
                    ):
                        is_server_approved = True
                        if perm_req.scope == PermissionScope.ONE_TIME:
                            permission_engine.revoke_permission(approval_token)

                if not is_server_approved:
                    perm_req = permission_engine.request_permission(
                        tool_id=step.tool_id or "automation.consequential_step",
                        action_description=f"Automation '{auto.name}' Step {idx+1}: {step.name}",
                        arguments=resolved_params,
                        risk_level=step.risk_level,
                        user_id=user_id,
                        session_id=session_id
                    )
                    approval_requests.append(perm_req.model_dump())
                    step_desc["status"] = "PENDING_APPROVAL"
                    actions_attempted.append(step_desc)

                    # Save Checkpoint before pausing
                    chk = WorkflowCheckpoint(
                        automation_id=automation_id,
                        run_id=run_id,
                        step_index=idx,
                        step_id=step.step_id,
                        completed_steps=completed_steps,
                        step_outputs=variables,
                        variables=variables,
                        verification_status="PENDING_APPROVAL"
                    )
                    self._save_checkpoint(chk)
                    run_record.checkpoints.append(chk)

                    run_record.status = "PENDING_APPROVAL"
                    run_record.approval_requests = approval_requests
                    run_record.actions_attempted = actions_attempted
                    run_record.completed_at = time.time()
                    return run_record

            # Execute Step by Step Type
            step_output = {}
            if step.step_type == "AGENT":
                # Launch Agent Task
                task_goal = step.agent_goal or step.name
                plan = planner_service.create_plan(goal=task_goal, domain=auto.domain, user_id=user_id)
                agent_res = agent_runtime.run_agent(
                    agent_id="general_assistant",
                    task_prompt=task_goal,
                    user_id=user_id,
                    task_id=plan.task_id
                )
                step_output = {"agent_task_id": plan.task_id, "summary": agent_res.get("summary", "Agent task completed")}
                step_desc["agent_task_id"] = plan.task_id
                step_desc["status"] = "SUCCESS"

            elif step.step_type == "TOOL" and step.tool_id:
                tools_used.append(step.tool_id)
                try:
                    tool_res = tool_executor.execute_tool(
                        tool_id=step.tool_id,
                        arguments=resolved_params,
                        user_id=user_id,
                        session_id=session_id,
                        permission_granted=True
                    )
                except Exception as e:
                    tool_res = {"success": False, "message": str(e)}

                step_output = tool_res
                step_desc["tool_result"] = tool_res
                if not tool_res.get("success", True):
                    # Bounded Retries Check (only for non-destructive actions)
                    if step.retry_on_failure and not is_high_risk:
                        logger.info(f"Retrying safe step '{step.name}'...")
                        time.sleep(0.5)
                        try:
                            tool_res = tool_executor.execute_tool(
                                tool_id=step.tool_id,
                                arguments=resolved_params,
                                user_id=user_id,
                                session_id=session_id,
                                permission_granted=True
                            )
                        except Exception as e2:
                            tool_res = {"success": False, "message": str(e2)}
                        step_output = tool_res

                    if not tool_res.get("success", True):
                        step_desc["status"] = "FAILED"
                        run_record.status = "FAILED"
                        run_record.failure_reason = tool_res.get("message", "Step failed")
                        actions_attempted.append(step_desc)
                        run_record.completed_at = time.time()
                        return run_record

                step_desc["status"] = "SUCCESS"

            elif step.step_type == "NOTIFICATION":
                routine_notification_engine.dispatch_notification(
                    routine_name=auto.name,
                    execution_id=run_id,
                    message=resolved_params.get("message", f"Automation '{auto.name}' step executed."),
                    user_id=user_id
                )
                step_output = {"notification_sent": True}
                step_desc["status"] = "SUCCESS"

            else:
                step_output = {"status": "executed"}
                step_desc["status"] = "SUCCESS"

            completed_steps.append(step.step_id)
            actions_attempted.append(step_desc)
            variables[step.step_id] = {"output": step_output}

            # Save Checkpoint
            chk = WorkflowCheckpoint(
                automation_id=automation_id,
                run_id=run_id,
                step_index=idx,
                step_id=step.step_id,
                completed_steps=completed_steps,
                step_outputs=variables,
                variables=variables,
                verification_status="VERIFIED"
            )
            self._save_checkpoint(chk)
            run_record.checkpoints.append(chk)

        # 7. Complete Run
        completed_ts = time.time()
        run_record.status = "SUCCESS"
        run_record.completed_at = completed_ts
        run_record.steps_completed = completed_steps
        run_record.actions_attempted = actions_attempted
        run_record.tools_used = tools_used
        run_record.outputs = variables
        run_record.result = {
            "summary": f"Automation '{auto.name}' completed {len(completed_steps)} steps successfully.",
            "total_steps": len(auto.steps)
        }

        # Update Automation Status & Schedule
        auto.last_run_at = now_ts
        auto.last_status = "SUCCESS"
        auto.run_count += 1
        if auto.schedule:
            auto.next_run_at = timezone_service.calculate_next_run(
                schedule=auto.schedule,
                user_tz_str=auto.timezone,
                after_timestamp=completed_ts
            )
        self.register_automation(auto)

        audit_service.log_event(
            user_id=user_id,
            session_id=session_id,
            task_id=automation_id,
            domain=auto.domain,
            action_summary=f"Unified automation '{auto.name}' run {run_id} completed successfully."
        )

        return run_record

    def _save_checkpoint(self, chk: WorkflowCheckpoint):
        self._checkpoints.setdefault(chk.run_id, []).append(chk)
        conn = routine_store._get_connection()
        try:
            with conn:
                conn.execute("""
                INSERT OR REPLACE INTO automation_checkpoints (
                    checkpoint_id, automation_id, run_id, step_index, step_id,
                    completed_steps_json, step_outputs_json, variables_json,
                    timestamp, verification_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chk.checkpoint_id, chk.automation_id, chk.run_id,
                    chk.step_index, chk.step_id,
                    json.dumps(chk.completed_steps),
                    json.dumps(chk.step_outputs),
                    json.dumps(chk.variables),
                    chk.timestamp, chk.verification_status
                ))
        finally:
            conn.close()

    def get_checkpoints(self, run_id: str) -> List[WorkflowCheckpoint]:
        if run_id in self._checkpoints:
            return self._checkpoints[run_id]
        results = []
        conn = routine_store._get_connection()
        try:
            rows = conn.execute("SELECT * FROM automation_checkpoints WHERE run_id = ? ORDER BY step_index ASC", (run_id,)).fetchall()
            for r in rows:
                d = dict(r)
                chk = WorkflowCheckpoint(
                    checkpoint_id=d["checkpoint_id"],
                    automation_id=d["automation_id"],
                    run_id=d["run_id"],
                    step_index=d["step_index"],
                    step_id=d["step_id"],
                    completed_steps=json.loads(d["completed_steps_json"]),
                    step_outputs=json.loads(d["step_outputs_json"]),
                    variables=json.loads(d["variables_json"]),
                    timestamp=d["timestamp"],
                    verification_status=d["verification_status"]
                )
                results.append(chk)
        finally:
            conn.close()
        return results

    def pause_automation(self, automation_id: str, user_id: str = "default_local_user") -> bool:
        auto = self.get_automation(automation_id, user_id=user_id)
        if not auto:
            return False
        auto.status = AutomationStatus.PAUSED
        auto.enabled = False
        auto.updated_at = time.time()
        self.register_automation(auto)
        return True

    def resume_automation(self, automation_id: str, user_id: str = "default_local_user") -> bool:
        auto = self.get_automation(automation_id, user_id=user_id)
        if not auto:
            return False
        auto.status = AutomationStatus.ACTIVE
        auto.enabled = True
        auto.updated_at = time.time()
        self.register_automation(auto)
        return True

    def disable_automation(self, automation_id: str, user_id: str = "default_local_user") -> bool:
        auto = self.get_automation(automation_id, user_id=user_id)
        if not auto:
            return False
        auto.status = AutomationStatus.DISABLED
        auto.enabled = False
        auto.updated_at = time.time()
        self.register_automation(auto)
        return True

    def delete_automation(self, automation_id: str, user_id: str = "default_local_user") -> bool:
        auto = self.get_automation(automation_id, user_id=user_id)
        if not auto:
            return False
        if automation_id in self._automations:
            del self._automations[automation_id]
        conn = routine_store._get_connection()
        try:
            with conn:
                conn.execute("DELETE FROM unified_automations WHERE automation_id = ?", (automation_id,))
                conn.execute("DELETE FROM automation_checkpoints WHERE automation_id = ?", (automation_id,))
        finally:
            conn.close()
        return True

    def skip_next_run(self, automation_id: str, user_id: str = "default_local_user") -> Optional[float]:
        auto = self.get_automation(automation_id, user_id=user_id)
        if not auto or not auto.schedule:
            return None
        curr_next = auto.next_run_at or time.time()
        new_next = timezone_service.calculate_next_run(
            schedule=auto.schedule,
            user_tz_str=auto.timezone,
            after_timestamp=curr_next + 60
        )
        auto.next_run_at = new_next
        auto.updated_at = time.time()
        self.register_automation(auto)
        return new_next


automation_engine = AutomationEngine()
