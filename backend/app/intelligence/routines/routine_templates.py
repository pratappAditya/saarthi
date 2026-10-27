from typing import Dict, Any, List
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
    RoutineNotification
)

ROUTINE_TEMPLATES: List[Dict[str, Any]] = [
    {
        "template_id": "morning_briefing",
        "name": "Morning Briefing",
        "description": "Daily 8 AM personalized summary of goals, active projects, deadlines, memories, and priorities.",
        "natural_language_definition": "Every morning at 8 AM, give me a personalized briefing.",
        "domain": "general",
        "trigger_type": TriggerType.TIME_TRIGGER,
        "schedule": {"frequency": "daily", "time_of_day": "08:00"},
        "actions": [
            {
                "action_type": "generate_briefing",
                "description": "Synthesize goals, pending approvals, deadlines, and high-priority tasks into a morning briefing.",
                "tool_id": "core.briefing",
                "parameters": {"briefing_type": "morning"}
            }
        ],
        "autonomy_level": AutonomyLevel.OBSERVE,
        "approval_policy": ApprovalPolicy.PRE_APPROVED_LOW_RISK
    },
    {
        "template_id": "evening_review",
        "name": "Evening Review",
        "description": "Daily 8 PM review of completed tasks, unfinished items, and tomorrow's preparation.",
        "natural_language_definition": "Every evening at 8 PM, remind me about unfinished important tasks.",
        "domain": "general",
        "trigger_type": TriggerType.TIME_TRIGGER,
        "schedule": {"frequency": "daily", "time_of_day": "20:00"},
        "actions": [
            {
                "action_type": "review_tasks",
                "description": "Review today's task completions and highlight unfinished high-priority items.",
                "tool_id": "task.review",
                "parameters": {"scope": "evening_wrapup"}
            }
        ],
        "autonomy_level": AutonomyLevel.SUGGEST,
        "approval_policy": ApprovalPolicy.PRE_APPROVED_LOW_RISK
    },
    {
        "template_id": "weekly_project_review",
        "name": "Weekly Project Review",
        "description": "Every Monday at 9 AM review of active project health, approaching deadlines, and blockers.",
        "natural_language_definition": "Every Monday at 9 AM, review my active projects and tell me what needs attention.",
        "domain": "software",
        "trigger_type": TriggerType.TIME_TRIGGER,
        "schedule": {"frequency": "weekly", "day_of_week": "monday", "time_of_day": "09:00"},
        "actions": [
            {
                "action_type": "analyze_projects",
                "description": "Inspect active projects for approaching deadlines, unassigned issues, and stalled tasks.",
                "tool_id": "workspace.projects",
                "parameters": {"check_health": True}
            }
        ],
        "autonomy_level": AutonomyLevel.ASK,
        "approval_policy": ApprovalPolicy.ASK_FOR_EACH_HIGH_RISK_ACTION
    },
    {
        "template_id": "weekly_goal_review",
        "name": "Weekly Goal Review",
        "description": "Every Friday at 5 PM check for stalled goals and generate actionable recommendations.",
        "natural_language_definition": "Every Friday at 5 PM, review my goals and prepare a weekly summary.",
        "domain": "career",
        "trigger_type": TriggerType.TIME_TRIGGER,
        "schedule": {"frequency": "weekly", "day_of_week": "friday", "time_of_day": "17:00"},
        "actions": [
            {
                "action_type": "review_goals",
                "description": "Summarize goal milestones achieved and highlight blocked goals.",
                "tool_id": "career.goals",
                "parameters": {"scope": "friday_digest"}
            }
        ],
        "autonomy_level": AutonomyLevel.SUGGEST,
        "approval_policy": ApprovalPolicy.PRE_APPROVED_LOW_RISK
    },
    {
        "template_id": "research_digest",
        "name": "Research Digest",
        "description": "Weekly academic and domain paper digest for active research topics.",
        "natural_language_definition": "Every Wednesday at 10 AM, search literature for new research in my active domains.",
        "domain": "research",
        "trigger_type": TriggerType.TIME_TRIGGER,
        "schedule": {"frequency": "weekly", "day_of_week": "wednesday", "time_of_day": "10:00"},
        "actions": [
            {
                "action_type": "search_literature",
                "description": "Search arXiv and PubMed for recent publications in active research topics.",
                "tool_id": "research.multi_source",
                "parameters": {"scope": "weekly_digest"}
            }
        ],
        "autonomy_level": AutonomyLevel.OBSERVE,
        "approval_policy": ApprovalPolicy.PRE_APPROVED_LOW_RISK
    },
    {
        "template_id": "agent_failure_alert",
        "name": "Agent Failure Alert",
        "description": "Event-triggered notification when an autonomous agent task encounters a failure or blocker.",
        "natural_language_definition": "When an agent fails, alert me with the error details.",
        "domain": "general",
        "trigger_type": TriggerType.EVENT_TRIGGER,
        "schedule": {},
        "conditions": [
            {
                "type": "agent_failed",
                "description": "Trigger when agent status is FAILED",
                "criteria": {"status": "FAILED"}
            }
        ],
        "actions": [
            {
                "action_type": "notify_failure",
                "description": "Send high-priority alert regarding the failed agent task",
                "tool_id": "core.notify",
                "parameters": {"category": "agent_failure", "urgency": "high"}
            }
        ],
        "autonomy_level": AutonomyLevel.OBSERVE,
        "approval_policy": ApprovalPolicy.PRE_APPROVED_LOW_RISK
    },
    {
        "template_id": "pending_approval_alert",
        "name": "Pending Approval Alert",
        "description": "Event-triggered reminder when a consequential permission request is awaiting human decision.",
        "natural_language_definition": "When an approval is requested, notify me immediately.",
        "domain": "general",
        "trigger_type": TriggerType.EVENT_TRIGGER,
        "schedule": {},
        "conditions": [
            {
                "type": "approval_pending",
                "description": "Trigger when a high-risk tool requests user permission",
                "criteria": {"status": "PENDING_APPROVAL"}
            }
        ],
        "actions": [
            {
                "action_type": "notify_approval",
                "description": "Notify user via desktop and in-app channel",
                "tool_id": "core.notify",
                "parameters": {"category": "approval_request"}
            }
        ],
        "autonomy_level": AutonomyLevel.OBSERVE,
        "approval_policy": ApprovalPolicy.PRE_APPROVED_LOW_RISK
    },
    {
        "template_id": "document_change_review",
        "name": "Document Change Review",
        "description": "Event-triggered review and diff summary when a monitored project document changes.",
        "natural_language_definition": "Whenever this project report changes, summarize what changed.",
        "domain": "general",
        "trigger_type": TriggerType.EVENT_TRIGGER,
        "schedule": {},
        "conditions": [
            {
                "type": "file_modified",
                "description": "Trigger when target document timestamp changes",
                "criteria": {"event": "DOCUMENT_MODIFIED"}
            }
        ],
        "actions": [
            {
                "action_type": "diff_summary",
                "description": "Compute diff and generate semantic summary of document changes",
                "tool_id": "multimodal.summarize_changes",
                "parameters": {"untrusted_content": True}
            }
        ],
        "autonomy_level": AutonomyLevel.SUGGEST,
        "approval_policy": ApprovalPolicy.PRE_APPROVED_LOW_RISK
    },
    {
        "template_id": "career_progress_review",
        "name": "Career Progress Review",
        "description": "Condition-triggered interview question preparation when job application reaches interview stage.",
        "natural_language_definition": "When my application reaches interview stage, prepare interview questions.",
        "domain": "career",
        "trigger_type": TriggerType.CONDITION_TRIGGER,
        "conditions": [
            {
                "type": "application_status_changed",
                "description": "When job application status updates to Interview Stage",
                "criteria": {"target_status": "interview"}
            }
        ],
        "actions": [
            {
                "action_type": "interview_prep",
                "description": "Extract JD requirements and prepare 8-dimension STAR interview questions",
                "tool_id": "career.prepare_interview",
                "parameters": {"auto_generate": True}
            }
        ],
        "autonomy_level": AutonomyLevel.ASK,
        "approval_policy": ApprovalPolicy.ASK_FOR_EACH_HIGH_RISK_ACTION
    }
]

def instantiate_template(template_id: str, user_id: str = "default_local_user") -> Routine:
    t = next((tmpl for tmpl in ROUTINE_TEMPLATES if tmpl["template_id"] == template_id), None)
    if not t:
        raise ValueError(f"Template '{template_id}' not found.")

    return Routine(
        name=t["name"],
        description=t["description"],
        natural_language_definition=t["natural_language_definition"],
        owner_user_id=user_id,
        scope=RoutineScope.GLOBAL,
        domain=t["domain"],
        trigger_type=t["trigger_type"],
        schedule=t.get("schedule", {}),
        conditions=[RoutineCondition(**c) for c in t.get("conditions", [])],
        actions=[RoutineAction(**a) for a in t.get("actions", [])],
        autonomy_level=t["autonomy_level"],
        approval_policy=t["approval_policy"],
        enabled=True,
        status=RoutineStatus.ACTIVE
    )


def instantiate_unified_template(template_id: str, user_id: str = "default_local_user"):
    """Instantiates a UnifiedAutomation model from canonical template."""
    from app.intelligence.routines.automation_models import (
        UnifiedAutomation, UnifiedTrigger, TriggerKind, WorkflowStep,
        DeterministicCondition, AutomationStatus, AutomationScope
    )
    t = next((tmpl for tmpl in ROUTINE_TEMPLATES if tmpl["template_id"] == template_id), None)
    if not t:
        raise ValueError(f"Template '{template_id}' not found.")

    trig_kind = TriggerKind.TIME
    if t["trigger_type"] == TriggerType.EVENT_TRIGGER:
        trig_kind = TriggerKind.EVENT
    elif t["trigger_type"] == TriggerType.CONDITION_TRIGGER:
        trig_kind = TriggerKind.CONDITIONAL

    steps = []
    for idx, act in enumerate(t.get("actions", [])):
        steps.append(WorkflowStep(
            step_id=f"step_{idx+1}",
            name=act.get("description") or act.get("action_type") or f"Step {idx+1}",
            step_type="TOOL",
            tool_id=act.get("tool_id"),
            parameters=act.get("parameters", {})
        ))

    conditions = []
    for cond in t.get("conditions", []):
        conditions.append(DeterministicCondition(
            field=cond.get("type", "status"),
            operator="eq",
            expected_value=cond.get("criteria", {}).get("target_status") or cond.get("criteria", {}).get("status") or True
        ))

    return UnifiedAutomation(
        name=t["name"],
        description=t["description"],
        user_id=user_id,
        scope=AutomationScope.GLOBAL,
        domain=t["domain"],
        trigger=UnifiedTrigger(
            kind=trig_kind,
            cron_or_time=t.get("schedule", {}).get("time_of_day"),
            frequency=t.get("schedule", {}).get("frequency")
        ),
        conditions=conditions,
        steps=steps,
        schedule=t.get("schedule", {}),
        enabled=True,
        status=AutomationStatus.ACTIVE
    )
