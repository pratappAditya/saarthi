"""
Deterministic Condition Engine (Phase 9 - Advanced Automation 2.0).
Evaluates structured, deterministic conditions with AND / OR / NOT boolean logic.
Avoids speculative natural-language interpretation at runtime.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from app.intelligence.routines.automation_models import (
    DeterministicCondition, ConditionLogic
)
from app.intelligence.planning.task_store import task_store
from app.intelligence.proactive.goal_system import goal_system
from app.intelligence.projects.project_manager import ProjectManager
from app.config.settings import settings

logger = logging.getLogger("app.intelligence.condition_engine")


class ConditionEngine:
    def __init__(self):
        self.project_manager = ProjectManager()

    def evaluate_single_condition(
        self,
        cond: DeterministicCondition,
        context: Dict[str, Any],
        user_id: str = "default_local_user"
    ) -> bool:
        """
        Evaluates one deterministic condition against runtime context or state stores.
        """
        field = cond.field
        op = cond.operator
        expected = cond.expected_value

        # 1. Resolve actual value from context or system state
        actual = None
        if field in context:
            actual = context[field]
        elif field == "task_status":
            t_id = context.get("task_id")
            if t_id:
                t = task_store.get_task(t_id)
                actual = t.get("status") if t else None
        elif field == "goal_progress":
            g_id = context.get("goal_id")
            if g_id:
                goals = goal_system.list_goals(user_id=user_id)
                match = [g for g in goals if g.id == g_id]
                actual = match[0].progress_percent if match else 0.0
        elif field == "deadline_hours":
            g_id = context.get("goal_id")
            if g_id:
                goals = goal_system.list_goals(user_id=user_id)
                match = [g for g in goals if g.id == g_id and g.target_date]
                if match:
                    try:
                        td = datetime.fromisoformat(match[0].target_date)
                        if td.tzinfo is None:
                            td = td.replace(tzinfo=timezone.utc)
                        now = datetime.now(timezone.utc)
                        actual = (td - now).total_seconds() / 3600.0
                    except Exception:
                        actual = 999.0
                else:
                    actual = 999.0
        elif field == "file_exists":
            filename = context.get("file_path") or str(expected)
            safe_base = os.path.abspath(settings.SAARTHI_DATA_DIR)
            p = os.path.join(safe_base, "workspaces", user_id, filename)
            actual = os.path.exists(p)
        elif field == "research_conflicts":
            actual = context.get("conflict_count", 0)
        else:
            # Fallback to direct variable lookup
            actual = context.get(field)

        # 2. Evaluate operator
        try:
            if op == "==":
                return actual == expected
            elif op == "!=":
                return actual != expected
            elif op == ">":
                return float(actual) > float(expected)
            elif op == "<":
                return float(actual) < float(expected)
            elif op == ">=":
                return float(actual) >= float(expected)
            elif op == "<=":
                return float(actual) <= float(expected)
            elif op == "contains":
                return expected in actual if actual is not None else False
            elif op == "in":
                return actual in expected if expected is not None else False
            elif op == "exists":
                return bool(actual)
            else:
                logger.warning(f"Unsupported operator '{op}', defaulting to False.")
                return False
        except Exception as e:
            logger.warning(f"Error evaluating condition '{cond.condition_id}': {e}")
            return False

    def evaluate_composite_conditions(
        self,
        conditions: List[DeterministicCondition],
        context: Dict[str, Any],
        logic: ConditionLogic = ConditionLogic.AND,
        user_id: str = "default_local_user"
    ) -> bool:
        """
        Evaluates a set of conditions using AND, OR, or NOT boolean logic.
        """
        if not conditions:
            return True

        evaluations = [
            self.evaluate_single_condition(c, context, user_id=user_id)
            for c in conditions
        ]

        if logic == ConditionLogic.AND:
            return all(evaluations)
        elif logic == ConditionLogic.OR:
            return any(evaluations)
        elif logic == ConditionLogic.NOT:
            return not all(evaluations)
        return all(evaluations)


condition_engine = ConditionEngine()
