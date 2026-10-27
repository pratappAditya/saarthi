"""
Proactive Models & Normalization Schema (Phase 8 - Proactive Saarthi 2.0).
Defines normalized event models, suggestion schemas, priority tiers,
action types, user controls, and feedback tracking.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ProactiveEventCategory(str, Enum):
    GOAL_PROGRESS = "GOAL_PROGRESS"
    PROJECT_CHANGE = "PROJECT_CHANGE"
    TASK_BLOCKED = "TASK_BLOCKED"
    DEADLINE_APPROACHING = "DEADLINE_APPROACHING"
    ROUTINE_DUE = "ROUTINE_DUE"
    RESEARCH_CHANGE = "RESEARCH_CHANGE"
    DOCUMENT_CHANGE = "DOCUMENT_CHANGE"
    WORKFLOW_PATTERN = "WORKFLOW_PATTERN"
    USER_REQUEST_FOLLOWUP = "USER_REQUEST_FOLLOWUP"
    AGENT_COMPLETION = "AGENT_COMPLETION"
    AGENT_FAILURE = "AGENT_FAILURE"
    AGENT_APPROVAL_NEEDED = "AGENT_APPROVAL_NEEDED"
    SYSTEM_STATUS = "SYSTEM_STATUS"
    SECURITY_EVENT = "SECURITY_EVENT"
    ACCOUNT_EVENT = "ACCOUNT_EVENT"


class ProactiveActionType(str, Enum):
    REVIEW = "REVIEW"
    DRAFT = "DRAFT"
    SEARCH = "SEARCH"
    SUMMARIZE = "SUMMARIZE"
    SCHEDULE = "SCHEDULE"
    CONTINUE = "CONTINUE"
    RETRY = "RETRY"
    ORGANIZE = "ORGANIZE"
    SUGGEST = "SUGGEST"
    ASK = "ASK"
    ACT = "ACT"


class SuggestionStatus(str, Enum):
    PENDING = "pending"
    SHOWN = "shown"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    SNOOZED = "snoozed"
    EXPIRED = "expired"
    EXECUTED = "executed"
    FAILED = "failed"


class ProactivePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProactiveEvent(BaseModel):
    event_id: str
    category: ProactiveEventCategory
    source: str  # e.g., "goal_system", "task_store", "research_orchestrator", "desktop_context"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    user_id: str = "default_local_user"
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    task_id: Optional[str] = None
    confidence: float = 0.90
    importance: float = 0.80
    expiration: Optional[str] = None
    actionability: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)


class ProactiveSuggestion(BaseModel):
    id: str
    user_id: str = "default_local_user"
    type: ProactiveEventCategory = ProactiveEventCategory.GOAL_PROGRESS
    title: str
    notice_text: str  # "I noticed..."
    message: str = ""  # Detailed message
    rationale: str  # "Why Saarthi suggested this / Because..."
    reason: str = ""  # Synonymous with rationale for backward compatibility
    source: str = "situational_awareness"
    confidence: float = 0.90
    priority: str = "medium"  # "low" | "medium" | "high" | "critical"
    action_type: str = "ASK"  # "SUGGEST" | "ASK" | "ACT" | "REVIEW" | "CONTINUE" | "RETRY" etc.
    target_domain: str = "general"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: Optional[str] = None
    related_project: Optional[str] = None
    related_goal: Optional[str] = None
    related_task: Optional[str] = None
    suggested_action: Optional[str] = None  # e.g., "CONTINUE", "RETRY", "REVIEW"
    suggested_tool: Optional[str] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)
    tool_arguments: Dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = True
    status: str = "pending"  # "pending" | "shown" | "accepted" | "dismissed" | "snoozed" | "executed"
    snooze_until: Optional[str] = None
    feed_category: str = "TODAY"  # "TODAY" | "PROJECT" | "RESEARCH" | "AGENTS" | "SYSTEM"
    execution_result: Optional[Dict[str, Any]] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.message:
            self.message = self.notice_text
        if not self.reason:
            self.reason = self.rationale
        if not self.tool_arguments and self.arguments:
            self.tool_arguments = self.arguments
        elif not self.arguments and self.tool_arguments:
            self.arguments = self.tool_arguments


class UserProactiveSettings(BaseModel):
    user_id: str = "default_local_user"
    enabled: bool = True
    frequency: str = "moderate"  # "high" | "moderate" | "low" | "quiet"
    quiet_hours_enabled: bool = True
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "08:00"
    voice_notifications_enabled: bool = False
    desktop_notifications_enabled: bool = True
    research_suggestions_enabled: bool = True
    goal_suggestions_enabled: bool = True
    project_suggestions_enabled: bool = True
    automation_suggestions_enabled: bool = True
    enabled_categories: Dict[str, bool] = Field(default_factory=lambda: {
        ProactiveEventCategory.GOAL_PROGRESS.value: True,
        ProactiveEventCategory.PROJECT_CHANGE.value: True,
        ProactiveEventCategory.TASK_BLOCKED.value: True,
        ProactiveEventCategory.DEADLINE_APPROACHING.value: True,
        ProactiveEventCategory.ROUTINE_DUE.value: True,
        ProactiveEventCategory.RESEARCH_CHANGE.value: True,
        ProactiveEventCategory.DOCUMENT_CHANGE.value: True,
        ProactiveEventCategory.WORKFLOW_PATTERN.value: True,
        ProactiveEventCategory.AGENT_COMPLETION.value: True,
        ProactiveEventCategory.AGENT_FAILURE.value: True,
        ProactiveEventCategory.AGENT_APPROVAL_NEEDED.value: True,
        ProactiveEventCategory.SYSTEM_STATUS.value: True,
    })
    disabled_types: List[str] = Field(default_factory=list)
    cooldown_minutes: int = 15
    max_daily_suggestions: int = 20
    dismissal_counts: Dict[str, int] = Field(default_factory=dict)
    suppressed_fingerprints: List[str] = Field(default_factory=list)
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProactiveFeedItem(BaseModel):
    category: str  # "TODAY" | "PROJECT" | "RESEARCH" | "AGENTS"
    title: str
    notice_text: str
    rationale: str
    action_type: str
    suggested_action: Optional[str] = None
    priority: str
    suggestion_id: str
    created_at: str
    requires_approval: bool = True
