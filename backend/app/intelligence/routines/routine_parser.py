import logging
import re
import time
from typing import Dict, Any, List, Optional

from app.intelligence.routines.routine_model import (
    RoutineDefinition,
    TriggerType,
    RoutineScope,
    AutonomyLevel,
    ApprovalPolicy,
    RoutineCondition,
    RoutineAction
)

logger = logging.getLogger("app.intelligence.routine_parser")

class RoutineParser:
    """
    Parses natural language user prompts into structured RoutineDefinition objects
    for preview and confirmation before activation.
    """
    @staticmethod
    def parse_prompt(prompt: str, domain: str = "general") -> RoutineDefinition:
        text = prompt.strip()
        lower = text.lower()

        # 1. Determine Trigger Type & Schedule
        trigger_type = TriggerType.TIME_TRIGGER
        schedule = {}
        conditions = []

        if "monday" in lower:
            schedule = {"frequency": "weekly", "day_of_week": "monday", "time_of_day": "09:00"}
        elif "friday" in lower:
            schedule = {"frequency": "weekly", "day_of_week": "friday", "time_of_day": "17:00"}
        elif "morning" in lower or "am" in lower or "daily" in lower:
            schedule = {"frequency": "daily", "time_of_day": "08:00"}
        elif "evening" in lower or "night" in lower or "pm" in lower:
            schedule = {"frequency": "daily", "time_of_day": "20:00"}
        elif lower.startswith("when ") or "if " in lower:
            trigger_type = TriggerType.CONDITION_TRIGGER
            if "interview" in lower or "application" in lower:
                conditions.append(RoutineCondition(
                    type="application_status_changed",
                    description="When job application status changes to Interview Stage",
                    criteria={"target_status": "interview"}
                ))
            elif "deadline" in lower:
                conditions.append(RoutineCondition(
                    type="deadline_approaching",
                    description="When project deadline is approaching within 48 hours",
                    criteria={"hours_remaining": 48}
                ))
            elif "goal" in lower:
                conditions.append(RoutineCondition(
                    type="goal_progress_stalled",
                    description="When goal progress stalls for 7 days",
                    criteria={"stalled_days": 7}
                ))
            else:
                conditions.append(RoutineCondition(
                    type="custom_condition",
                    description=f"When condition trigger observed: {text[:40]}",
                    criteria={"raw_prompt": text}
                ))
        else:
            schedule = {"frequency": "daily", "time_of_day": "09:00"}

        # 2. Extract Actions
        actions = []
        if "project" in lower or "projects" in lower:
            actions.append(RoutineAction(
                action_type="analyze_projects",
                description="Review active project status, unresolved tasks, and potential blockers",
                tool_id="workspace.projects",
                parameters={"scope": "active_projects"}
            ))

        if "briefing" in lower or "summary" in lower or "summarize" in lower:
            actions.append(RoutineAction(
                action_type="generate_briefing",
                description="Synthesize personalized summary across goals, tasks, and priorities",
                tool_id="core.briefing",
                parameters={"style": "personalized"}
            ))

        if "interview" in lower:
            actions.append(RoutineAction(
                action_type="interview_prep",
                description="Extract job description requirements and prepare targeted interview questions",
                tool_id="career.prepare_interview",
                parameters={"mode": "auto_prep"}
            ))

        if "goal" in lower or "goals" in lower:
            actions.append(RoutineAction(
                action_type="review_goals",
                description="Track goal progress milestones and generate actionable recommendations",
                tool_id="career.goals",
                parameters={"scope": "milestone_review"}
            ))

        if "task" in lower or "tasks" in lower or "remind" in lower:
            actions.append(RoutineAction(
                action_type="task_reminder",
                description="Inspect unfinished high-priority tasks and dispatch reminders",
                tool_id="task.remind",
                parameters={"filter": "unfinished_important"}
            ))

        if not actions:
            actions.append(RoutineAction(
                action_type="general_workflow",
                description=f"Execute workflow for prompt: '{text}'",
                tool_id="agent.workflow",
                parameters={"user_prompt": text}
            ))

        # 3. Autonomy & Approval Policy
        has_high_risk = any(a.risk_level in ["high", "critical"] or "email" in lower or "delete" in lower for a in actions)
        autonomy = AutonomyLevel.HIGH_RISK_ALWAYS_ASK if has_high_risk else AutonomyLevel.ASK
        approval = ApprovalPolicy.ALWAYS_ASK if has_high_risk else ApprovalPolicy.ASK_FOR_EACH_HIGH_RISK_ACTION

        # 4. Generate Name & Description
        name = text[:40].strip().title()
        if len(text) > 40:
            name += "..."

        desc = f"Automated routine generated from prompt: '{text}'"

        return RoutineDefinition(
            name=name,
            description=desc,
            natural_language_prompt=text,
            scope=RoutineScope.GLOBAL,
            domain=domain,
            trigger_type=trigger_type,
            schedule=schedule,
            conditions=conditions,
            actions=actions,
            autonomy_level=autonomy,
            approval_policy=approval,
            requires_approval=True
        )

    @staticmethod
    def parse_automation_preview(
        prompt: str,
        domain: str = "general",
        timezone: str = "UTC",
        user_id: str = "default_local_user"
    ) -> Any:
        """
        Parses natural language prompt into user-friendly WHEN / IF / DO / APPROVAL / THEN representation.
        """
        from app.intelligence.routines.automation_models import AutomationBuilderPreview

        r_def = RoutineParser.parse_prompt(prompt, domain=domain)
        
        # When
        when_str = "Manual Execution"
        if r_def.trigger_type == TriggerType.TIME_TRIGGER:
            freq = r_def.schedule.get("frequency", "daily")
            tod = r_def.schedule.get("time_of_day", "09:00")
            dow = r_def.schedule.get("day_of_week", "")
            when_str = f"Every {dow.capitalize() + ' at ' if dow else ''}{tod} ({freq})"
        elif r_def.trigger_type == TriggerType.CONDITION_TRIGGER:
            when_str = f"When event observed: {r_def.conditions[0].description if r_def.conditions else prompt}"

        # If
        if_list = [c.description for c in r_def.conditions] if r_def.conditions else ["System state verified healthy"]

        # Do
        do_list = [{"step": i+1, "action": a.action_type, "description": a.description} for i, a in enumerate(r_def.actions)]

        # Approval
        appr_str = "Explicit confirmation required for high-risk tools (file.delete, terminal.execute, email.send)" if r_def.requires_approval else "Pre-approved safe operations"

        # Then
        then_str = "Notify user with execution summary and update workspace audit trail"

        return AutomationBuilderPreview(
            name=r_def.name,
            description=r_def.description,
            natural_language_prompt=prompt,
            when_trigger=when_str,
            if_conditions=if_list,
            do_steps=do_list,
            approval_requirement=appr_str,
            then_action=then_str,
            frequency=r_def.schedule.get("frequency", "event"),
            timezone=timezone,
            is_confirmed=False
        )

routine_parser = RoutineParser()

