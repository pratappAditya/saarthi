import time
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class TriggerType(str, Enum):
    TIME_TRIGGER = "TIME_TRIGGER"
    CONDITION_TRIGGER = "CONDITION_TRIGGER"
    EVENT_TRIGGER = "EVENT_TRIGGER"
    MANUAL_TRIGGER = "MANUAL_TRIGGER"
    VOICE_TRIGGER = "VOICE_TRIGGER"

class RoutineScope(str, Enum):
    GLOBAL = "GLOBAL"
    PROJECT = "PROJECT"
    DOMAIN = "DOMAIN"
    TASK = "TASK"

class AutonomyLevel(str, Enum):
    OBSERVE = "OBSERVE"
    SUGGEST = "SUGGEST"
    ASK = "ASK"
    ACT = "ACT"
    HIGH_RISK_ALWAYS_ASK = "HIGH_RISK_ALWAYS_ASK"

class ApprovalPolicy(str, Enum):
    ALWAYS_ASK = "ALWAYS_ASK"
    ASK_ON_FIRST_RUN = "ASK_ON_FIRST_RUN"
    ASK_FOR_EACH_HIGH_RISK_ACTION = "ASK_FOR_EACH_HIGH_RISK_ACTION"
    PRE_APPROVED_LOW_RISK = "PRE_APPROVED_LOW_RISK"
    USER_DEFINED = "USER_DEFINED"

class MissedRunPolicy(str, Enum):
    SKIP = "SKIP"
    RUN_ONCE_AFTER_START = "RUN_ONCE_AFTER_START"
    CATCH_UP = "CATCH_UP"
    ASK_USER = "ASK_USER"

class RoutineStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"

class RoutineCondition(BaseModel):
    condition_id: str = Field(default_factory=lambda: f"cond_{int(time.time()*1000)}")
    type: str  # e.g., "deadline_approaching", "application_status_changed", "goal_progress_stalled", "custom_event"
    description: str
    criteria: Dict[str, Any] = Field(default_factory=dict)

class RoutineAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"act_{int(time.time()*1000)}")
    action_type: str  # e.g., "analyze_projects", "generate_briefing", "interview_prep", "agent_task"
    description: str
    tool_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "low"  # low, medium, high, critical

class RoutineNotification(BaseModel):
    channel: str = "in_app"  # in_app, voice, desktop, digest
    message_template: Optional[str] = None
    quiet_hours_override: bool = False

class RoutineExecution(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"exec_{int(time.time()*1000)}")
    routine_id: str
    started_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    trigger: str
    status: str = "RUNNING"  # RUNNING, SUCCESS, FAILED, PENDING_APPROVAL, PAUSED
    task_graph: Optional[Dict[str, Any]] = None
    actions_attempted: List[Dict[str, Any]] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    approval_requests: List[Dict[str, Any]] = Field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    verification_status: str = "VERIFIED"
    failure_reason: Optional[str] = None
    retry_count: int = 0

class Routine(BaseModel):
    id: str = Field(default_factory=lambda: f"rtn_{int(time.time()*1000)}")
    name: str
    description: str
    natural_language_definition: Optional[str] = None
    owner_user_id: str = "default_local_user"
    scope: RoutineScope = RoutineScope.GLOBAL
    project_id: Optional[str] = None
    domain: str = "general"
    trigger_type: TriggerType = TriggerType.TIME_TRIGGER
    schedule: Dict[str, Any] = Field(default_factory=dict)  # cron, interval_minutes, time_of_day, days_of_week
    timezone: str = "UTC"
    conditions: List[RoutineCondition] = Field(default_factory=list)
    actions: List[RoutineAction] = Field(default_factory=list)
    execution_policy: Dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3, "timeout_seconds": 300})
    approval_policy: ApprovalPolicy = ApprovalPolicy.ASK_FOR_EACH_HIGH_RISK_ACTION
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3, "backoff_factor": 2.0})
    notification_policy: RoutineNotification = Field(default_factory=RoutineNotification)
    missed_run_policy: MissedRunPolicy = MissedRunPolicy.RUN_ONCE_AFTER_START
    autonomy_level: AutonomyLevel = AutonomyLevel.ASK
    status: RoutineStatus = RoutineStatus.ACTIVE
    enabled: bool = True
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    next_run_at: Optional[float] = None
    last_run_at: Optional[float] = None
    last_status: Optional[str] = None
    failure_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RoutineDefinition(BaseModel):
    """Structured response object for parsed natural language routine previews before activation."""
    name: str
    description: str
    natural_language_prompt: str
    scope: RoutineScope = RoutineScope.GLOBAL
    domain: str = "general"
    trigger_type: TriggerType
    schedule: Dict[str, Any] = Field(default_factory=dict)
    conditions: List[RoutineCondition] = Field(default_factory=list)
    actions: List[RoutineAction] = Field(default_factory=list)
    autonomy_level: AutonomyLevel = AutonomyLevel.ASK
    approval_policy: ApprovalPolicy = ApprovalPolicy.ASK_FOR_EACH_HIGH_RISK_ACTION
    requires_approval: bool = True
