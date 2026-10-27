import logging
import time
from typing import Dict, Any, List, Optional

from app.intelligence.routines.routine_model import (
    Routine,
    RoutineExecution,
    RoutineStatus,
    AutonomyLevel,
    ApprovalPolicy
)
from app.intelligence.routines.routine_store import routine_store, RoutineStore
from app.intelligence.routines.routine_notification_engine import routine_notification_engine
from app.intelligence.context.context_engine import context_engine
from app.intelligence.personalization.personalization_engine import personalization_engine
from app.intelligence.planning.planner import planner_service
from app.intelligence.agents.agent_runtime import agent_runtime
from app.intelligence.permissions.permission_engine import permission_engine
from app.intelligence.tools.tool_executor import tool_executor
from app.intelligence.audit.intelligence_audit import audit_service
from app.core.plans import PlanService
from app.core.entitlements import get_current_plan

logger = logging.getLogger("app.intelligence.routine_engine")

class RoutineEngine:
    def __init__(self, store: Optional[RoutineStore] = None):
        self.store = store or routine_store

    def execute_routine(
        self,
        routine_id: str,
        trigger_source: str = "MANUAL_TRIGGER",
        user_id: str = "default_local_user",
        permission_granted: bool = False
    ) -> RoutineExecution:
        routine = self.store.get_routine(routine_id)
        if not routine:
            raise ValueError(f"Routine '{routine_id}' not found.")

        if not routine.enabled or routine.status == RoutineStatus.PAUSED:
            logger.warning(f"Routine '{routine.name}' ({routine_id}) is paused or disabled. Skipping execution.")
            exec_record = RoutineExecution(
                routine_id=routine_id,
                started_at=time.time(),
                completed_at=time.time(),
                trigger=trigger_source,
                status="PAUSED",
                failure_reason="Routine is disabled or paused."
            )
            self.store.record_execution(exec_record)
            return exec_record

        # 1. Entitlement Capability Gate Check
        current_plan = get_current_plan(user_id)
        if not PlanService.is_capability_entitled(current_plan, "agents.routines"):
            logger.warning(f"User '{user_id}' plan '{current_plan}' lacks 'agents.routines' capability.")
            exec_record = RoutineExecution(
                routine_id=routine_id,
                started_at=time.time(),
                completed_at=time.time(),
                trigger=trigger_source,
                status="FAILED",
                failure_reason=f"Plan '{current_plan.upper()}' lacks routine execution capability."
            )
            self.store.record_execution(exec_record)
            return exec_record

        execution_id = f"exec_{int(time.time()*1000)}"
        started_at = time.time()
        execution = RoutineExecution(
            execution_id=execution_id,
            routine_id=routine_id,
            started_at=started_at,
            trigger=trigger_source,
            status="RUNNING"
        )
        self.store.record_execution(execution)

        actions_attempted = []
        tools_used = []
        approval_requests = []
        has_failure = False
        failure_msg = None

        try:
            # 2. Build ContextBundle with Personalization Context (Task > Project > Domain > Global)
            context_bundle = context_engine.build_context_bundle(
                user_message=routine.natural_language_definition or routine.name,
                user_id=user_id,
                project_id=routine.project_id
            )

            # 3. Process Each Action via Agent Runtime / Planner
            for action in routine.actions:
                act_info = {
                    "action_id": action.action_id,
                    "action_type": action.action_type,
                    "description": action.description,
                    "status": "EXECUTING"
                }

                # Risk & Approval Policy Check
                is_high_risk = action.risk_level in ["high", "critical"]
                needs_approval = False

                if routine.autonomy_level in [AutonomyLevel.ASK, AutonomyLevel.HIGH_RISK_ALWAYS_ASK] and is_high_risk:
                    needs_approval = True
                elif routine.approval_policy == ApprovalPolicy.ALWAYS_ASK:
                    needs_approval = True
                elif routine.approval_policy == ApprovalPolicy.ASK_FOR_EACH_HIGH_RISK_ACTION and is_high_risk:
                    needs_approval = True

                if needs_approval and not permission_granted:
                    perm_req = permission_engine.request_permission(
                        tool_id=action.tool_id or "routine.action",
                        action_description=f"Routine '{routine.name}': {action.description}",
                        arguments=action.parameters,
                        risk_level=action.risk_level,
                        user_id=user_id
                    )
                    approval_requests.append(perm_req.model_dump())
                    act_info["status"] = "PENDING_APPROVAL"
                    actions_attempted.append(act_info)

                    execution.status = "PENDING_APPROVAL"
                    execution.actions_attempted = actions_attempted
                    execution.approval_requests = approval_requests
                    execution.completed_at = time.time()
                    self.store.update_execution(execution)

                    routine.last_run_at = started_at
                    routine.last_status = "PENDING_APPROVAL"
                    self.store.update_routine(routine)

                    routine_notification_engine.dispatch_notification(
                        routine_name=routine.name,
                        execution_id=execution_id,
                        message=f"Routine '{routine.name}' requires explicit approval for action: '{action.description}'",
                        notification_policy=routine.notification_policy,
                        user_id=user_id
                    )
                    return execution

                # Synthesize Plan / Agent Task if applicable
                task_graph = planner_service.create_plan(
                    goal=action.description,
                    domain=routine.domain,
                    user_id=user_id
                )
                execution.task_graph = task_graph.model_dump()

                # Execute action tool if specified
                if action.tool_id:
                    tool_res = tool_executor.execute_tool(
                        tool_id=action.tool_id,
                        arguments=action.parameters,
                        user_id=user_id,
                        permission_granted=True
                    )
                    tools_used.append(action.tool_id)
                    act_info["tool_result"] = tool_res
                    if not tool_res.get("success", True):
                        has_failure = True
                        failure_msg = tool_res.get("message", "Tool execution failed.")
                        act_info["status"] = "FAILED"
                    else:
                        act_info["status"] = "SUCCESS"
                else:
                    act_info["status"] = "SUCCESS"

                actions_attempted.append(act_info)

            completed_at = time.time()
            if has_failure:
                execution.status = "FAILED"
                execution.failure_reason = failure_msg
                routine.failure_count += 1
                routine.last_status = "FAILED"

                # Check Retry Policy
                max_retries = routine.retry_policy.get("max_retries", 3)
                if routine.failure_count >= max_retries:
                    routine.status = RoutineStatus.PAUSED
                    logger.warning(f"Routine '{routine.name}' exceeded max retries ({max_retries}). Pausing routine.")
                    routine_notification_engine.dispatch_notification(
                        routine_name=routine.name,
                        execution_id=execution_id,
                        message=f"Routine '{routine.name}' repeatedly failed and has been PAUSED. Reason: {failure_msg}",
                        user_id=user_id
                    )
            else:
                execution.status = "SUCCESS"
                routine.failure_count = 0
                routine.last_status = "SUCCESS"

                routine_notification_engine.dispatch_notification(
                    routine_name=routine.name,
                    execution_id=execution_id,
                    message=f"Routine '{routine.name}' completed successfully.",
                    notification_policy=routine.notification_policy,
                    user_id=user_id
                )

            execution.completed_at = completed_at
            execution.actions_attempted = actions_attempted
            execution.tools_used = tools_used
            execution.result = {
                "summary": f"Routine '{routine.name}' executed {len(actions_attempted)} action(s).",
                "actions_count": len(actions_attempted)
            }
            self.store.update_execution(execution)

            routine.last_run_at = started_at
            routine.updated_at = completed_at
            # Update next_run_at if time trigger
            if routine.trigger_type == routine.trigger_type.TIME_TRIGGER:
                interval_secs = routine.schedule.get("interval_seconds", 86400) # default 24h
                routine.next_run_at = completed_at + interval_secs

            self.store.update_routine(routine)

            # Audit Log
            audit_service.log_event(
                user_id=user_id,
                session_id="routine_session",
                task_id=routine_id,
                domain=routine.domain,
                action_summary=f"Executed routine '{routine.name}' with status '{execution.status}'"
            )

            return execution

        except Exception as e:
            logger.error(f"Error executing routine '{routine_id}': {e}", exc_info=True)
            execution.status = "FAILED"
            execution.failure_reason = str(e)
            execution.completed_at = time.time()
            self.store.update_execution(execution)

            routine.failure_count += 1
            routine.last_status = "FAILED"
            self.store.update_routine(routine)
            return execution

    def evaluate_condition_triggers(self, event_type: str, event_data: Dict[str, Any], user_id: str = "default_local_user") -> List[RoutineExecution]:
        """Scans active condition/event routines and executes matching routines."""
        routines = self.store.list_routines(user_id=user_id)
        executed = []

        for rtn in routines:
            if not rtn.enabled or rtn.status != RoutineStatus.ACTIVE:
                continue

            if rtn.trigger_type in [rtn.trigger_type.CONDITION_TRIGGER, rtn.trigger_type.EVENT_TRIGGER]:
                matched = False
                for cond in rtn.conditions:
                    if cond.type == event_type:
                        matched = True
                        break

                if matched:
                    logger.info(f"Condition trigger '{event_type}' matched routine '{rtn.name}'. Executing...")
                    res = self.execute_routine(routine_id=rtn.id, trigger_source=f"EVENT:{event_type}", user_id=user_id)
                    executed.append(res)

        return executed

routine_engine = RoutineEngine()
