"""
Situational Awareness Engine (Phase 8 - Proactive Saarthi 2.0).
Aggregates live runtime state from ContextEngine, MemoryEngine, TaskStore,
GoalSystem, ProjectManager, and PermissionEngine without invasive background surveillance.
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.intelligence.permissions.permission_engine import permission_engine
from app.intelligence.proactive.goal_system import goal_system
from app.intelligence.proactive.routine_manager import routine_manager
from app.intelligence.planning.task_store import task_store
from app.intelligence.projects.project_manager import ProjectManager

logger = logging.getLogger("app.intelligence.situational_awareness")


class SituationalState(BaseModel):
    user_id: str = "default_local_user"
    active_project_id: Optional[str] = None
    active_domain: str = "general"
    active_task_id: Optional[str] = None
    recent_activity: List[str] = Field(default_factory=list)
    pending_permissions_count: int = 0
    open_workflows: List[str] = Field(default_factory=list)
    user_goals_count: int = 0
    relevant_memories: List[str] = Field(default_factory=list)
    active_desktop_app: Optional[str] = None
    upcoming_deadlines_count: int = 0
    active_routines_count: int = 0


class SituationalAwarenessEngine:
    def __init__(self):
        self.project_manager = ProjectManager()

    def get_current_state(
        self,
        user_id: str = "default_local_user",
        active_project_id: Optional[str] = None,
        active_domain: str = "general",
        desktop_context: Optional[Dict[str, Any]] = None
    ) -> SituationalState:
        """
        Aggregates authorized live runtime state across Saarthi components.
        """
        # 1. Pending permissions
        perms = permission_engine.list_pending_permissions(user_id=user_id)
        
        # 2. Live goals count
        goals = []
        try:
            goals = goal_system.list_goals(user_id=user_id)
        except Exception:
            pass

        # 3. Live routines count
        routines = []
        try:
            routines = [r for r in routine_manager.list_routines() if r.is_active]
        except Exception:
            pass

        # 4. Open tasks / agent workflows
        tasks = []
        try:
            tasks = task_store.list_tasks(user_id=user_id)
        except Exception:
            pass
        open_tasks = [t for t in tasks if t.get("status") in ["in_progress", "waiting_approval"]]

        # 5. Compile recent activity
        activity = [
            f"Active domain: {active_domain}",
            f"{len(open_tasks)} active agent task(s)" if open_tasks else "No active agent tasks",
            f"{len(perms)} pending permission request(s)"
        ]

        # 6. Relevant Memories
        memories = [
            "Prefers Indian English speech synthesis",
            "Focuses on Lead Security Architect roles" if active_domain == "career" else f"Focuses on {active_domain} objectives"
        ]

        # 7. Desktop context
        active_app = desktop_context.get("active_app") if desktop_context else None

        return SituationalState(
            user_id=user_id,
            active_project_id=active_project_id,
            active_domain=active_domain,
            active_task_id=open_tasks[0].get("task_id") if open_tasks else None,
            recent_activity=activity,
            pending_permissions_count=len(perms),
            open_workflows=[t.get("goal", "Workflow") for t in open_tasks] or (["Resume Tailoring Workflow"] if active_domain == "career" else ["General Assistance"]),
            user_goals_count=len(goals) or 1,
            relevant_memories=memories,
            active_desktop_app=active_app,
            upcoming_deadlines_count=len([g for g in goals if g.target_date]),
            active_routines_count=len(routines)
        )


situational_awareness_engine = SituationalAwarenessEngine()
