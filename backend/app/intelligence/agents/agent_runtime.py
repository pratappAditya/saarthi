import uuid
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.intelligence.agents.agent_state import AgentStatus
from app.intelligence.agents.agent_definition import AGENT_CATALOG, AgentDefinition
from app.intelligence.tools.tool_executor import tool_executor
from app.intelligence.tools.tool_registry import ToolRegistry
from app.intelligence.planning.planner import planner_service
from app.intelligence.planning.task_graph import TaskGraph, TaskStep, TaskStatus
from app.intelligence.planning.task_store import task_store
from app.intelligence.permissions.permission_engine import permission_engine
from app.intelligence.permissions.permission_models import PermissionStatus, PermissionScope
from app.core.plans import PlanService
from app.core.entitlements import get_current_plan

logger = logging.getLogger("app.intelligence.agent_runtime")


class AgentRuntime:
    """
    Production Autonomous Agent Execution Engine for Saarthi.
    Implements the real execution lifecycle:
    OBSERVE -> PLAN -> PERMISSION -> ACT -> VERIFY -> REPLAN IF NECESSARY
    Guarantees observable post-condition verification, persistence across restarts,
    safe checkpoints, rollback, pause/resume, and strict server-side approval verification.
    """

    @staticmethod
    def run_agent(
        agent_id: str,
        task_prompt: str,
        user_id: str = "default_local_user",
        session_id: Optional[str] = None,
        task_id: Optional[str] = None,
        approval_token: Optional[str] = None,
        max_steps: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes an agent workflow for a goal. Can start a new task or resume an existing task_id.
        """
        agent_def = AGENT_CATALOG.get(agent_id)
        if not agent_def:
            # Fallback to general agent definition if custom agent ID passed
            agent_def = AgentDefinition(
                id=agent_id,
                name=f"{agent_id.capitalize()} Agent",
                description="General purpose autonomous execution agent.",
                system_prompt="You are Saarthi Autonomous Agent.",
                allowed_tools=["browser.search", "file.read", "file.write", "file.search", "code.execute"],
                required_capabilities=["core.chat.basic"],
                max_steps=20,
                domain="general"
            )

        # 1. Entitlement Check
        current_plan = get_current_plan(user_id)
        for req_cap in agent_def.required_capabilities:
            if not PlanService.is_capability_entitled(current_plan, req_cap):
                return {
                    "success": False,
                    "error": "ENTITLEMENT_FORBIDDEN",
                    "message": f"Agent '{agent_id}' requires capability '{req_cap}' which is not in your '{current_plan.upper()}' plan."
                }

        run_id = f"run_{uuid.uuid4().hex[:8]}"
        step_limit = max_steps or agent_def.max_steps or 20

        # 2. Plan Generation or Task Resumption
        if task_id:
            task_data = task_store.get_task(task_id)
            if not task_data:
                return {"success": False, "error": f"Task '{task_id}' not found."}
            graph = TaskGraph(
                task_id=task_data["task_id"],
                user_id=task_data["user_id"],
                goal=task_data.get("objective") or task_data.get("goal") or task_prompt,
                domain=task_data.get("domain", agent_def.domain),
                status=TaskStatus(task_data.get("status", TaskStatus.IN_PROGRESS.value)),
                steps=[TaskStep(**s) for s in task_data.get("steps", [])],
                replan_count=task_data.get("metadata", {}).get("replan_count", 0)
            )
        else:
            graph = planner_service.create_plan(goal=task_prompt, domain=agent_def.domain, user_id=user_id)

        trace: List[Dict[str, Any]] = []
        step_count = 0
        all_verified = True
        consecutive_failures = 0
        last_failed_signature = None

        # Create initial checkpoint
        chk_init = graph.create_checkpoint("initial_plan")
        task_store.save_checkpoint(graph.task_id, chk_init, graph.checkpoints[chk_init])

        task_store.update_task_status(task_id=graph.task_id, status=TaskStatus.IN_PROGRESS.value)

        # 3. Observe -> Plan -> Permission -> Act -> Verify -> Replan Loop
        while step_count < step_limit:
            # Check for cancellation or pause
            current_state = task_store.get_task(graph.task_id)
            if current_state:
                if current_state.get("status") == "cancelled":
                    return {
                        "success": False,
                        "status": "cancelled",
                        "task_id": graph.task_id,
                        "message": "Task execution was cancelled by user.",
                        "steps_executed": step_count,
                        "verified": False,
                        "trace": trace
                    }
                elif current_state.get("status") == "paused":
                    return {
                        "success": True,
                        "status": "paused",
                        "task_id": graph.task_id,
                        "message": "Task execution paused at checkpoint.",
                        "steps_executed": step_count,
                        "verified": True,
                        "trace": trace
                    }

            # Find executable steps respecting DAG dependencies
            ready_steps = graph.get_executable_steps()
            if not ready_steps:
                # Check if all steps completed
                all_done = all(s.status == TaskStatus.COMPLETED for s in graph.steps)
                has_pending_approvals = any(s.approval_required and s.approval_state != "approved" and s.status == TaskStatus.PENDING for s in graph.steps)
                if has_pending_approvals:
                    task_store.update_task_status(task_id=graph.task_id, status="waiting_approval")
                    return {
                        "success": True,
                        "status": "waiting_approval",
                        "task_id": graph.task_id,
                        "message": "Task is awaiting explicit user approval for a consequential action.",
                        "steps_executed": step_count,
                        "trace": trace
                    }
                break

            # Execute next ready step (support parallel candidate selection)
            step = ready_steps[0]
            step_count += 1

            # Permission Check
            tool_id = step.tool_id or (agent_def.allowed_tools[0] if agent_def.allowed_tools else "file.search")
            tool_def = ToolRegistry.get_tool(tool_id)

            requires_approval = step.approval_required or (tool_def and tool_def.requires_confirmation)
            is_approved = False

            if requires_approval:
                # Strictly verify server-side approval token
                token_to_verify = approval_token or step.approval_token
                if token_to_verify:
                    perm_req = permission_engine.get_permission_request(token_to_verify)
                    if (
                        perm_req
                        and perm_req.user_id == user_id
                        and perm_req.tool_id == tool_id
                        and perm_req.status == PermissionStatus.APPROVED
                    ):
                        is_approved = True
                        step.approval_state = "approved"
                        if perm_req.scope == PermissionScope.ONE_TIME:
                            permission_engine.revoke_permission(token_to_verify)
                    else:
                        logger.warning(f"Rejected invalid/forged approval token '{token_to_verify}' for step '{step.step_id}'")

                if not is_approved:
                    # Request server-side permission
                    perm_req = permission_engine.request_permission(
                        tool_id=tool_id,
                        action_description=f"Action '{step.title}' requires user authorization.",
                        arguments=step.arguments,
                        risk_level=step.risk_level.upper() if step.risk_level else "MODERATE",
                        session_id=session_id or "default_session",
                        user_id=user_id
                    )
                    step.approval_state = "pending"
                    step.approval_token = perm_req.request_id

                    # Persist state
                    task_store.update_task_status(
                        task_id=graph.task_id,
                        status="waiting_approval",
                        steps=[s.model_dump() for s in graph.steps]
                    )

                    trace.append({
                        "step": step_count,
                        "step_id": step.step_id,
                        "tool_id": tool_id,
                        "status": "awaiting_approval",
                        "permission_request_id": perm_req.request_id,
                        "action_type": tool_def.operation_type if tool_def else "ACTION"
                    })

                    return {
                        "success": True,
                        "status": "waiting_approval",
                        "task_id": graph.task_id,
                        "run_id": run_id,
                        "pending_step_id": step.step_id,
                        "permission_request_id": perm_req.request_id,
                        "message": f"Execution paused awaiting approval for '{step.title}'.",
                        "steps_executed": step_count,
                        "trace": trace
                    }

            # Stage Model Selection
            from app.models.router import model_router
            from app.models.schema import ModelCapability
            req_cap = None
            if step.required_model_capability:
                try:
                    req_cap = ModelCapability(step.required_model_capability)
                except Exception:
                    pass
            stage_model = model_router.select_model(
                task_type=step.step_type.lower(),
                required_capability=req_cap,
                prefer_local=True
            )
            step.selected_model_id = stage_model.id

            # ACT: Execute Tool
            exec_res = tool_executor.execute_tool(
                tool_id=tool_id,
                arguments=step.arguments or {"query": task_prompt},
                user_id=user_id,
                session_id=session_id,
                permission_granted=True,
                approval_token=approval_token
            )

            # VERIFY: Observable Post-Condition Verification
            verified = exec_res.get("verified", False)
            step.result = exec_res.get("result")
            step.verification_state = "verified" if verified else "failed"
            step.verification_reason = exec_res.get("verification_reason")
            step.verification_evidence = exec_res.get("verification_evidence", {})

            # Propagate variables to graph
            if step.result and isinstance(step.result, dict):
                graph.variables[f"{step.step_id}_result"] = step.result

            if not verified or not exec_res.get("success"):
                all_verified = False
                step.status = TaskStatus.FAILED
                step.error = exec_res.get("verification_reason") or exec_res.get("message") or "Verification failed"

                # Check loop detection
                current_signature = f"{tool_id}:{str(step.arguments)}"
                if current_signature == last_failed_signature:
                    consecutive_failures += 1
                else:
                    consecutive_failures = 1
                last_failed_signature = current_signature

                if consecutive_failures >= 3:
                    logger.error(f"Infinite tool failure loop detected for tool '{tool_id}'. Aborting task.")
                    task_store.update_task_status(task_id=graph.task_id, status=TaskStatus.FAILED.value, steps=[s.model_dump() for s in graph.steps])
                    trace.append({
                        "step": step_count,
                        "step_id": step.step_id,
                        "tool_id": tool_id,
                        "status": "loop_aborted",
                        "error": "Aborted due to repeated identical execution failures."
                    })
                    break

                # Safe Retry or Replan
                if step.retry_count < step.max_retries:
                    step.retry_count += 1
                    step.status = TaskStatus.PENDING
                    logger.info(f"Retrying step '{step.step_id}' (attempt {step.retry_count}/{step.max_retries})...")
                    continue
                else:
                    # REPLAN IF NECESSARY
                    replan_graph = planner_service.replan_on_failure(
                        task_id=graph.task_id,
                        failed_step_id=step.step_id,
                        error_message=step.error,
                        failure_diagnosis=f"Post-action verification failed: {step.verification_reason}"
                    )
                    trace.append({
                        "step": step_count,
                        "step_id": step.step_id,
                        "tool_id": tool_id,
                        "status": "failed",
                        "verification_reason": step.verification_reason,
                        "replanned": replan_graph is not None
                    })
                    if replan_graph:
                        graph = replan_graph
                        continue
                    else:
                        break
            else:
                consecutive_failures = 0
                step.status = TaskStatus.COMPLETED
                trace.append({
                    "step": step_count,
                    "step_id": step.step_id,
                    "tool_id": tool_id,
                    "status": "verified",
                    "verification_reason": step.verification_reason,
                    "verification_evidence": step.verification_evidence,
                    "result": exec_res.get("result"),
                    "action_type": exec_res.get("operation_type", "ACTION")
                })

                # Milestone checkpoint
                if step_count % 2 == 0 or step.step_id == graph.steps[-1].step_id:
                    chk_id = graph.create_checkpoint(f"milestone_step_{step.step_id}")
                    task_store.save_checkpoint(graph.task_id, chk_id, graph.checkpoints[chk_id])

                # Persist step updates
                task_store.update_task_status(
                    task_id=graph.task_id,
                    status=TaskStatus.IN_PROGRESS.value,
                    steps=[s.model_dump() for s in graph.steps]
                )

        final_all_completed = all(s.status == TaskStatus.COMPLETED for s in graph.steps)
        final_status = "completed" if (final_all_completed and all_verified) else ("completed_with_replanning" if all_verified else "failed")
        task_store.update_task_status(task_id=graph.task_id, status=final_status, steps=[s.model_dump() for s in graph.steps])

        return {
            "success": all_verified and final_all_completed,
            "run_id": run_id,
            "task_id": graph.task_id,
            "agent_id": agent_id,
            "agent_name": agent_def.name,
            "domain": agent_def.domain,
            "status": final_status,
            "steps_executed": step_count,
            "execution_steps_count": step_count,
            "verified": all_verified,
            "trace": trace
        }

    @staticmethod
    def pause_task(task_id: str) -> bool:
        res = planner_service.pause_task(task_id)
        return res is not None

    @staticmethod
    def resume_task(task_id: str, user_id: str = "default_local_user", approval_token: Optional[str] = None) -> Dict[str, Any]:
        task_data = task_store.get_task(task_id)
        if not task_data:
            return {"success": False, "error": f"Task '{task_id}' not found."}
        agent_id = task_data.get("domain", "general")
        prompt = task_data.get("objective") or task_data.get("goal") or "Resume active task"
        return AgentRuntime.run_agent(
            agent_id=agent_id,
            task_prompt=prompt,
            user_id=user_id,
            task_id=task_id,
            approval_token=approval_token
        )

    @staticmethod
    def cancel_task(task_id: str) -> bool:
        return planner_service.cancel_task(task_id)

    @staticmethod
    def rollback_to_checkpoint(task_id: str, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        graph = planner_service.rollback_to_checkpoint(task_id, checkpoint_id)
        if not graph:
            return None
        return task_store.get_task(task_id)


agent_runtime = AgentRuntime()
