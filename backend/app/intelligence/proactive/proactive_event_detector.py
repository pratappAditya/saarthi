"""
Proactive Event Detector (Phase 8 - Proactive Saarthi 2.0).
Inspects authorized runtime context across Goals, Projects, Tasks/Agents,
Routines, Research, Desktop, and Multimodal systems to emit normalized ProactiveEvents.
STRICT PRIVACY: Never monitors microphone, never performs continuous screen recording,
and never accesses unauthorized applications or password stores.
"""

import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.intelligence.proactive.proactive_models import (
    ProactiveEvent, ProactiveEventCategory
)
from app.intelligence.proactive.goal_system import goal_system
from app.intelligence.proactive.routine_manager import routine_manager
from app.intelligence.projects.project_manager import ProjectManager
from app.intelligence.planning.task_store import task_store
from app.intelligence.permissions.permission_engine import permission_engine

logger = logging.getLogger("app.intelligence.proactive_event_detector")


class ProactiveEventDetector:
    def __init__(self):
        self.project_manager = ProjectManager()

    def detect_all_events(
        self,
        user_id: str = "default_local_user",
        active_project_id: Optional[str] = None,
        active_domain: str = "general",
        desktop_context: Optional[Dict[str, Any]] = None,
        multimodal_context: Optional[Dict[str, Any]] = None
    ) -> List[ProactiveEvent]:
        """
        Gathers live authorized events across Goals, Projects, Agents,
        Routines, Research, Desktop, and Multimodal sources.
        """
        events: List[ProactiveEvent] = []

        # 1. Goal Awareness Events
        try:
            goals = goal_system.list_goals(user_id=user_id)
            for g in goals:
                if g.status == "in_progress":
                    pending_milestones = [m for m in g.milestones if m.status == "pending"]
                    if pending_milestones:
                        # Goal Progress / Remaining Milestones
                        events.append(ProactiveEvent(
                            event_id=f"evt_goal_{g.id}_{uuid.uuid4().hex[:6]}",
                            category=ProactiveEventCategory.GOAL_PROGRESS,
                            source="goal_system",
                            user_id=user_id,
                            goal_id=g.id,
                            confidence=0.95,
                            importance=0.85,
                            data={
                                "goal_id": g.id,
                                "goal_title": g.title,
                                "remaining_count": len(pending_milestones),
                                "next_milestone": pending_milestones[0].title,
                                "domain": g.domain,
                                "target_date": g.target_date or "No deadline set",
                                "topic": f"goal_{g.title}"
                            }
                        ))
                    if g.target_date:
                        # Deadline Approaching
                        events.append(ProactiveEvent(
                            event_id=f"evt_dead_{g.id}_{uuid.uuid4().hex[:6]}",
                            category=ProactiveEventCategory.DEADLINE_APPROACHING,
                            source="goal_system",
                            user_id=user_id,
                            goal_id=g.id,
                            confidence=0.92,
                            importance=0.90,
                            data={
                                "goal_id": g.id,
                                "item_title": g.title,
                                "target_date": g.target_date,
                                "time_left": "upcoming milestone window",
                                "topic": f"deadline_{g.title}"
                            }
                        ))
        except Exception as e:
            logger.warning(f"Error reading goals for events: {e}")

        # 2. Agent & Task Awareness Events
        try:
            tasks = task_store.list_tasks(user_id=user_id)
            for t in tasks:
                t_id = t.get("task_id", "")
                t_status = t.get("status", "")
                t_domain = t.get("domain", "general")
                goal_desc = t.get("goal", "Agent workflow")

                if t_status == "waiting_approval":
                    events.append(ProactiveEvent(
                        event_id=f"evt_task_appr_{t_id}_{uuid.uuid4().hex[:6]}",
                        category=ProactiveEventCategory.AGENT_APPROVAL_NEEDED,
                        source="task_store",
                        user_id=user_id,
                        task_id=t_id,
                        confidence=0.99,
                        importance=0.95,
                        data={
                            "task_id": t_id,
                            "task_name": goal_desc,
                            "tool_id": "consequential_tool",
                            "domain": t_domain,
                            "topic": f"approval_{t_id}"
                        }
                    ))
                elif t_status == "failed":
                    events.append(ProactiveEvent(
                        event_id=f"evt_task_fail_{t_id}_{uuid.uuid4().hex[:6]}",
                        category=ProactiveEventCategory.AGENT_FAILURE,
                        source="task_store",
                        user_id=user_id,
                        task_id=t_id,
                        confidence=0.95,
                        importance=0.90,
                        data={
                            "task_id": t_id,
                            "task_name": goal_desc,
                            "failed_step": "step_verification",
                            "error": t.get("metadata", {}).get("error", "Verification failure"),
                            "domain": t_domain,
                            "topic": f"failed_{t_id}"
                        }
                    ))
                elif t_status == "completed":
                    events.append(ProactiveEvent(
                        event_id=f"evt_task_comp_{t_id}_{uuid.uuid4().hex[:6]}",
                        category=ProactiveEventCategory.AGENT_COMPLETION,
                        source="task_store",
                        user_id=user_id,
                        task_id=t_id,
                        confidence=0.90,
                        importance=0.75,
                        data={
                            "task_id": t_id,
                            "task_name": goal_desc,
                            "domain": t_domain,
                            "topic": f"completed_{t_id}"
                        }
                    ))
                elif t_status == "paused":
                    events.append(ProactiveEvent(
                        event_id=f"evt_task_pause_{t_id}_{uuid.uuid4().hex[:6]}",
                        category=ProactiveEventCategory.TASK_BLOCKED,
                        source="task_store",
                        user_id=user_id,
                        task_id=t_id,
                        confidence=0.90,
                        importance=0.80,
                        data={
                            "task_id": t_id,
                            "task_title": goal_desc,
                            "dependency": "user pause / external state",
                            "topic": f"paused_{t_id}"
                        }
                    ))
        except Exception as e:
            logger.warning(f"Error reading tasks for events: {e}")

        # 3. Routine Awareness Events
        try:
            routines = routine_manager.list_routines()
            for r in routines:
                if r.is_active:
                    events.append(ProactiveEvent(
                        event_id=f"evt_rtn_{r.id}_{uuid.uuid4().hex[:6]}",
                        category=ProactiveEventCategory.ROUTINE_DUE,
                        source="routine_manager",
                        user_id=user_id,
                        confidence=0.92,
                        importance=0.75,
                        data={
                            "routine_id": r.id,
                            "routine_name": r.name,
                            "cron_expression": r.cron_expression,
                            "domain": r.domain,
                            "tool_id": r.tool_id,
                            "topic": f"routine_{r.name}"
                        }
                    ))
        except Exception as e:
            logger.warning(f"Error reading routines for events: {e}")

        # 4. Project Awareness Events
        try:
            if active_project_id:
                proj = self.project_manager.get_project(active_project_id)
                if proj:
                    events.append(ProactiveEvent(
                        event_id=f"evt_proj_{proj.project_id}_{uuid.uuid4().hex[:6]}",
                        category=ProactiveEventCategory.PROJECT_CHANGE,
                        source="project_manager",
                        user_id=user_id,
                        project_id=proj.project_id,
                        confidence=0.88,
                        importance=0.75,
                        data={
                            "project_id": proj.project_id,
                            "project_name": proj.name,
                            "domain": proj.domain,
                            "topic": f"project_{proj.name}"
                        }
                    ))
        except Exception as e:
            logger.warning(f"Error reading projects for events: {e}")

        # 5. Desktop Context Awareness Events (Authorized desktop interactions)
        if desktop_context:
            app_name = desktop_context.get("active_app", "")
            selected_text = desktop_context.get("selected_text", "")
            if selected_text and len(selected_text.strip()) > 5:
                events.append(ProactiveEvent(
                    event_id=f"evt_desk_sel_{uuid.uuid4().hex[:6]}",
                    category=ProactiveEventCategory.USER_REQUEST_FOLLOWUP,
                    source="desktop_context",
                    user_id=user_id,
                    confidence=0.95,
                    importance=0.85,
                    data={
                        "active_app": app_name,
                        "selected_text": selected_text[:100],
                        "topic": "desktop_selection",
                        "action_offered": "REWRITE_OR_EXPLAIN"
                    }
                ))
            elif "code" in app_name.lower() or "studio" in app_name.lower():
                events.append(ProactiveEvent(
                    event_id=f"evt_desk_ide_{uuid.uuid4().hex[:6]}",
                    category=ProactiveEventCategory.SYSTEM_STATUS,
                    source="desktop_context",
                    user_id=user_id,
                    confidence=0.80,
                    importance=0.70,
                    data={
                        "active_app": app_name,
                        "topic": "ide_workspace",
                        "domain": "software"
                    }
                ))

        # 6. Multimodal Awareness Events (Document/Image updates)
        if multimodal_context:
            doc_name = multimodal_context.get("filename")
            doc_change = multimodal_context.get("change_type")
            if doc_name:
                events.append(ProactiveEvent(
                    event_id=f"evt_multi_doc_{uuid.uuid4().hex[:6]}",
                    category=ProactiveEventCategory.DOCUMENT_CHANGE,
                    source="multimodal_engine",
                    user_id=user_id,
                    confidence=0.90,
                    importance=0.80,
                    data={
                        "filename": doc_name,
                        "change_type": doc_change or "updated",
                        "topic": f"document_{doc_name}"
                    }
                ))

        return events


proactive_event_detector = ProactiveEventDetector()
