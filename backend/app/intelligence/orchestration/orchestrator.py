import logging
from typing import Dict, Any, List, Optional
from app.intelligence.context.context_engine import context_engine
from app.intelligence.domains.domain_router import domain_router
from app.intelligence.models.model_router import model_router
from app.intelligence.memory.memory_manager import memory_manager
from app.intelligence.tools.tool_registry import ToolRegistry
from app.intelligence.tools.tool_executor import tool_executor
from app.intelligence.permissions.permission_engine import permission_engine
from app.intelligence.planning.planner import planner_service
from app.intelligence.audit.intelligence_audit import audit_service
from app.intelligence.personalization.personalization_engine import personalization_engine
from app.core.plans import PlanService
from app.core.entitlements import get_current_plan

logger = logging.getLogger("app.intelligence.orchestrator")

class Orchestrator:
    @staticmethod
    def process_message(
        user_message: str,
        session_id: str = "default_session",
        user_id: str = "default_local_user",
        project_id: Optional[str] = None,
        permission_granted: bool = False,
        approval_token: Optional[str] = None,
        attachment_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main Intelligence Orchestration Pipeline:
        1. Context, Personalization, & Multimodal Gathering (Task > Project > Domain > Global precedence)
        2. Plan Capability Check & Model Selection
        3. Intent & Tool Requirement Detection
        4. Permission & Risk Check (Strict Server-Side Verified)
        5. Execution, Interaction Signal Learning, & Audit
        """
        from app.intelligence.permissions.permission_models import PermissionStatus, PermissionScope
        # 1. Context & Personalization Bundle
        bundle = context_engine.build_context_bundle(
            user_message=user_message,
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            attachment_id=attachment_id
        )
        domain = bundle.domain_context.active_domain
        current_plan = get_current_plan(user_id)
        pers_ctx = bundle.personalization_context

        # Learn domain interaction signal
        if pers_ctx and pers_ctx.personalization_enabled:
            personalization_engine.learn_interaction_signal(
                user_id=user_id,
                signal_type="domain_interaction",
                signal_data={"domain": domain, "complexity": "advanced" if len(user_message.split()) > 10 else "intermediate"}
            )

        # 2. Model Selection
        selected_model = model_router.select_model(task_type="chat", user_plan=current_plan)

        # 3. Tool Detection & Plan Synthesis
        needs_tools = False
        tool_to_use = None
        msg_lower = user_message.lower()

        if "analyze" in msg_lower and "jd" in msg_lower:
            needs_tools = True
            tool_to_use = "career.analyze_jd"
        elif "tailor" in msg_lower and ("resume" in msg_lower or "job" in msg_lower):
            needs_tools = True
            tool_to_use = "career.tailor_resume"
        elif "interview" in msg_lower and "prep" in msg_lower:
            needs_tools = True
            tool_to_use = "career.prepare_interview"
        elif "salary" in msg_lower or "offer" in msg_lower:
            needs_tools = True
            tool_to_use = "career.salary_analysis"
        elif "search" in msg_lower and "web" in msg_lower:
            needs_tools = True
            tool_to_use = "browser.search"
        elif "code" in msg_lower and "execute" in msg_lower:
            needs_tools = True
            tool_to_use = "code.execute"
        elif "terminal" in msg_lower or "command" in msg_lower:
            needs_tools = True
            tool_to_use = "terminal.execute"

        if tool_to_use and pers_ctx and pers_ctx.personalization_enabled:
            personalization_engine.learn_interaction_signal(
                user_id=user_id,
                signal_type="tool_used",
                signal_data={"tool_id": tool_to_use}
            )

        # 4. Synthesize Task Graph if complex or multi-domain goal
        task_graph = None
        if needs_tools or len(user_message.split()) > 5 or any(k in user_message.lower() for k in ["archaeol", "histor", "cybersecurity", "bio", "civil", "research", "compare"]):
            task_graph = planner_service.create_plan(user_message, domain=domain, user_id=user_id)
            # Create explicit domain handoffs if graph spans multiple domains
            if task_graph and len(task_graph.subdomains) > 1:
                from app.intelligence.domains.domain_handoff import domain_handoff_manager
                for i in range(len(task_graph.subdomains) - 1):
                    src = task_graph.subdomains[i]
                    dst = task_graph.subdomains[i+1]
                    domain_handoff_manager.create_handoff(
                        source_domain=src,
                        destination_domain=dst,
                        reason=f"Transition from {src.upper()} to {dst.upper()} for cross-domain objective execution",
                        input_artifact={"objective": user_message},
                        provenance={"task_id": task_graph.task_id}
                    )

        # 5. Execute Tool or Generate Response
        response_text = ""
        tool_execution_result = None

        if tool_to_use:
            tool_def = ToolRegistry.get_tool(tool_to_use)
            if tool_def:
                if not PlanService.is_capability_entitled(current_plan, tool_def.required_capability):
                    response_text = f"Tool '{tool_def.name}' requires capability '{tool_def.required_capability}' which is locked on your '{current_plan.upper()}' plan."
                else:
                    # Server-side verification for tools requiring confirmation
                    is_server_approved = False
                    if tool_def.requires_confirmation:
                        if approval_token:
                            perm_req = permission_engine.get_permission_request(approval_token)
                            if (
                                perm_req
                                and perm_req.user_id == user_id
                                and perm_req.tool_id == tool_to_use
                                and perm_req.status == PermissionStatus.APPROVED
                            ):
                                is_server_approved = True
                                # Revoke one-time permission to prevent replay attacks
                                if perm_req.scope == PermissionScope.ONE_TIME:
                                    permission_engine.revoke_permission(approval_token)
                            else:
                                logger.warning(f"Rejected invalid or forged approval token '{approval_token}' for user '{user_id}' and tool '{tool_to_use}'")
                        
                        if not is_server_approved:
                            perm_req = permission_engine.request_permission(
                                tool_id=tool_to_use,
                                action_description=f"Execute {tool_def.name} for request: '{user_message}'",
                                arguments={"user_message": user_message},
                                risk_level=tool_def.risk_level.value,
                                session_id=session_id,
                                user_id=user_id
                            )
                            response_text = f"I can execute '{tool_def.name}', but this requires explicit user permission due to {tool_def.risk_level.value} risk level."
                            return {
                                "status": "pending_confirmation",
                                "response": response_text,
                                "permission_request": perm_req.model_dump(),
                                "domain": domain,
                                "subdomains": bundle.domain_context.active_subdomains,
                                "selected_model": selected_model.id,
                                "context": bundle.model_dump()
                            }

                    tool_res = tool_executor.execute_tool(
                        tool_id=tool_to_use,
                        arguments={"jd_text": user_message, "query": user_message, "task": user_message},
                        user_id=user_id,
                        session_id=session_id,
                        permission_granted=True
                    )
                    tool_execution_result = tool_res
                    if tool_res.get("success"):
                        response_text = f"Successfully executed tool '{tool_def.name}'. Generated results and saved audit log."
                    else:
                        response_text = f"Tool execution failed: {tool_res.get('message')}"
        research_output = None
        if not tool_to_use:
            is_research_intent = (
                domain == "research"
                or any(k in msg_lower for k in ["research", "compare", "literature", "citations", "evidence summary", "tradeoff", "versus", "vs."])
            )
            if is_research_intent:
                try:
                    from app.intelligence.research.research_orchestrator import research_orchestrator
                    active_subdomains = task_graph.subdomains if task_graph else [domain]
                    res = research_orchestrator.conduct_research(
                        query=user_message,
                        user_id=user_id,
                        session_id=session_id,
                        domain_id=domain,
                        explicit_domains=active_subdomains
                    )
                    research_output = res
                    response_text = res.synthesis_summary
                except Exception as ex:
                    logger.warning(f"Research pipeline fallback: {ex}")
                    depth_str = f" ({pers_ctx.effective_technical_depth.upper()} depth)" if pers_ctx else ""
                    response_text = f"Saarthi Research Core ({domain.upper()} domain{depth_str}): {user_message}"
            else:
                depth_str = f" ({pers_ctx.effective_technical_depth.upper()} depth)" if pers_ctx else ""
                if task_graph and len(task_graph.subdomains) > 1:
                    domains_str = " -> ".join([d.capitalize() for d in task_graph.subdomains])
                    response_text = f"Saarthi Cross-Domain Engine ({domains_str}{depth_str}): Executed multi-domain pipeline with local {selected_model.name}."
                else:
                    response_text = f"Saarthi Intelligence Core ({domain.upper()} domain{depth_str}): Addressed query using local {selected_model.name}."

        # 6. Audit & Durable Memory Update
        audit_service.log_event(
            user_id=user_id,
            session_id=session_id,
            task_id=task_graph.task_id if task_graph else None,
            tool_name=tool_to_use,
            model_name=selected_model.id,
            domain=domain,
            action_summary=f"Processed message across {domain} domain."
        )

        return {
            "status": "success" if not (tool_to_use and ToolRegistry.get_tool(tool_to_use) and ToolRegistry.get_tool(tool_to_use).requires_confirmation and not permission_granted) else "pending_confirmation",
            "message": response_text,
            "response": response_text,
            "intent": tool_to_use or "conversational_query",
            "domain": domain,
            "subdomains": task_graph.subdomains if task_graph else [domain],
            "domain_transitions": task_graph.domain_transitions if task_graph else [],
            "confidence": 0.95,
            "memories_used": bundle.memory_context.relevant_memories,
            "tools_used": [tool_to_use] if tool_to_use else [],
            "task": task_graph.model_dump() if task_graph else None,
            "actions": [tool_execution_result] if tool_execution_result else [],
            "awaiting_confirmation": tool_to_use is not None and ToolRegistry.get_tool(tool_to_use) is not None and ToolRegistry.get_tool(tool_to_use).requires_confirmation and not permission_granted,
            "suggestions": [
                f"Continue working across {domain.upper()} workflow",
                "View domain transition graph in Cross-Domain Workflow View",
                "Check active task graph progress"
            ],
            "selected_model": selected_model.id,
            "context": bundle.model_dump(),
            "research_result": research_output.model_dump() if research_output else None
        }

orchestrator = Orchestrator()
