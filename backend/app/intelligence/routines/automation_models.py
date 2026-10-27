"""
Unified Automation Model (Phase 9 - Advanced Automation 2.0).
Defines the canonical schema for Automations, Triggers, Deterministic Conditions,
Multi-Step Action Chains, Checkpoints, Idempotency, and Execution Records.
"""

import time
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from app.intelligence.routines.routine_model import (
    TriggerType,
    RoutineScope,
    AutonomyLevel,
    ApprovalPolicy,
    MissedRunPolicy
)

AutomationScope = RoutineScope


class AutomationStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DISABLED = "DISABLED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TriggerKind(str, Enum):
    TIME = "TIME"
    EVENT = "EVENT"
    USER = "USER"
    CONDITIONAL = "CONDITIONAL"


class ConditionLogic(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class UnifiedTrigger(BaseModel):
    kind: TriggerKind = TriggerKind.TIME
    trigger_type: TriggerType = TriggerType.TIME_TRIGGER
    event_type: Optional[str] = None  # e.g., "goal_progress_stalled", "task_completed", "document_changed"
    schedule: Dict[str, Any] = Field(default_factory=dict)  # cron, frequency, time_of_day, days_of_week
    timezone: str = "UTC"
    criteria: Dict[str, Any] = Field(default_factory=dict)
    description: str = "Trigger definition"


class DeterministicCondition(BaseModel):
    condition_id: str = Field(default_factory=lambda: f"cond_{int(time.time()*1000)}")
    field: str  # e.g., "task_status", "goal_progress", "deadline_hours", "file_exists", "research_conflicts"
    operator: str = "=="  # "==", "!=", ">", "<", ">=", "<=", "contains", "in", "exists"
    expected_value: Any = None
    logic: ConditionLogic = ConditionLogic.AND
    description: str = ""


class WorkflowStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"step_{int(time.time()*1000)}")
    name: str
    step_type: str = "TOOL"  # "TOOL" | "AGENT" | "CONDITION" | "NOTIFICATION"
    action_type: str = "execute"
    description: str = ""
    tool_id: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    input_bindings: Dict[str, str] = Field(default_factory=dict)  # e.g. {"input_text": "$step_1.output.summary"}
    risk_level: str = "low"  # "low" | "medium" | "high" | "critical"
    requires_approval: bool = False
    agent_goal: Optional[str] = None
    retry_on_failure: bool = True
    max_retries: int = 2


class WorkflowCheckpoint(BaseModel):
    checkpoint_id: str = Field(default_factory=lambda: f"chk_{int(time.time()*1000)}")
    automation_id: str
    run_id: str
    step_index: int
    step_id: str
    completed_steps: List[str] = Field(default_factory=list)
    step_outputs: Dict[str, Any] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
    verification_status: str = "VERIFIED"


class UnifiedAutomation(BaseModel):
    automation_id: str = Field(default_factory=lambda: f"auto_{int(time.time()*1000)}")
    name: str
    description: str = ""
    natural_language_definition: Optional[str] = None
    user_id: str = "default_local_user"
    organization_id: Optional[str] = None
    scope: RoutineScope = RoutineScope.GLOBAL
    project_id: Optional[str] = None
    goal_id: Optional[str] = None
    domain: str = "general"
    trigger: UnifiedTrigger = Field(default_factory=UnifiedTrigger)
    conditions: List[DeterministicCondition] = Field(default_factory=list)
    condition_logic: ConditionLogic = ConditionLogic.AND
    steps: List[WorkflowStep] = Field(default_factory=list)
    schedule: Dict[str, Any] = Field(default_factory=dict)
    timezone: str = "UTC"
    enabled: bool = True
    approval_policy: ApprovalPolicy = ApprovalPolicy.ASK_FOR_EACH_HIGH_RISK_ACTION
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {"max_retries": 3, "backoff_factor": 2.0})
    missed_run_policy: MissedRunPolicy = MissedRunPolicy.RUN_ONCE_AFTER_START
    autonomy_level: AutonomyLevel = AutonomyLevel.ASK
    timeout: float = 300.0
    max_runs: Optional[int] = None
    run_count: int = 0
    status: AutomationStatus = AutomationStatus.ACTIVE
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    next_run_at: Optional[float] = None
    last_run_at: Optional[float] = None
    last_status: Optional[str] = None
    failure_count: int = 0
    recursion_depth: int = 0
    max_recursion_depth: int = 3
    idempotency_key: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AutomationRunRecord(BaseModel):
    run_id: str = Field(default_factory=lambda: f"run_{int(time.time()*1000)}")
    automation_id: str
    user_id: str = "default_local_user"
    organization_id: Optional[str] = None
    started_at: float = Field(default_factory=time.time)
    completed_at: Optional[float] = None
    trigger_source: str = "MANUAL"
    status: str = "RUNNING"  # "RUNNING" | "SUCCESS" | "FAILED" | "PENDING_APPROVAL" | "PAUSED" | "CANCELLED"
    checkpoints: List[WorkflowCheckpoint] = Field(default_factory=list)
    steps_completed: List[str] = Field(default_factory=list)
    actions_attempted: List[Dict[str, Any]] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    approval_requests: List[Dict[str, Any]] = Field(default_factory=list)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    verification_status: str = "VERIFIED"
    failure_reason: Optional[str] = None
    retry_count: int = 0
    idempotency_key: str = ""


class AutomationBuilderPreview(BaseModel):
    """Clean user-facing representation of an automation before activation."""
    name: str
    description: str
    natural_language_prompt: str
    when_trigger: str
    if_conditions: List[str]
    do_steps: List[Dict[str, Any]]
    approval_requirement: str
    then_action: str
    frequency: str
    timezone: str
    is_confirmed: bool = False
