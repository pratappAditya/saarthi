from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.intelligence.planning.task_state import TaskStatus

class TaskStep(BaseModel):
    step_id: str
    title: str
    description: str
    domain: str = "general"
    subdomain: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    tool_id: Optional[str] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    step_type: str = "ACTION"  # "OBSERVATION" | "ACTION" | "CONDITIONAL" | "SYNTHESIS"
    is_parallel: bool = False
    condition: Optional[str] = None
    checkpoint_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    output_artifact: Optional[Dict[str, Any]] = None
    confidence: float = 0.95
    risk_level: str = "low"  # "low" | "medium" | "high" | "critical"
    approval_required: bool = False
    approval_state: str = "not_required"  # "not_required" | "pending" | "approved" | "rejected"
    approval_token: Optional[str] = None
    required_model_capability: Optional[str] = None
    selected_model_id: Optional[str] = None
    provenance: Dict[str, Any] = Field(default_factory=dict)
    verification_state: str = "unverified"  # "unverified" | "verified" | "failed"
    verification_reason: Optional[str] = None
    verification_evidence: Dict[str, Any] = Field(default_factory=dict)

class TaskGraph(BaseModel):
    task_id: str
    goal: str
    domain: str = "general"
    subdomains: List[str] = Field(default_factory=list)
    user_id: str = "default_local_user"
    steps: List[TaskStep] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    domain_transitions: List[Dict[str, Any]] = Field(default_factory=list)
    approval_requirements: List[str] = Field(default_factory=list)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    verification_state: str = "unverified"
    checkpoints: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
    replan_count: int = 0
    max_replans: int = 3

    def get_step(self, step_id: str) -> Optional[TaskStep]:
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def get_executable_steps(self) -> List[TaskStep]:
        ready_steps = []
        completed_step_ids = {s.step_id for s in self.steps if s.status == TaskStatus.COMPLETED}
        
        for step in self.steps:
            if step.status == TaskStatus.PENDING:
                if step.approval_required and step.approval_state != "approved":
                    continue
                # Check condition if present
                if step.condition and not self._evaluate_condition(step.condition):
                    continue
                if all(dep in completed_step_ids for dep in step.dependencies):
                    ready_steps.append(step)
        return ready_steps

    def _evaluate_condition(self, condition_expr: str) -> bool:
        """Evaluates simple step preconditions based on completed step results or variables."""
        try:
            # Safe evaluation against graph variables
            for var_key, var_val in self.variables.items():
                if var_key in condition_expr:
                    condition_expr = condition_expr.replace(var_key, repr(var_val))
            return bool(eval(condition_expr, {"__builtins__": None}, {}))
        except Exception:
            return True

    def create_checkpoint(self, name: str) -> str:
        chk_id = f"chk_{len(self.checkpoints) + 1}_{datetime.now(timezone.utc).strftime('%H%M%S')}"
        snapshot = {
            "checkpoint_id": chk_id,
            "name": name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "steps": [s.model_dump() for s in self.steps],
            "variables": dict(self.variables),
            "status": self.status.value
        }
        self.checkpoints[chk_id] = snapshot
        return chk_id

    def rollback_to_checkpoint(self, chk_id: str) -> bool:
        if chk_id not in self.checkpoints:
            return False
        snap = self.checkpoints[chk_id]
        self.steps = [TaskStep(**s) for s in snap["steps"]]
        self.variables = dict(snap.get("variables", {}))
        self.status = TaskStatus(snap.get("status", TaskStatus.IN_PROGRESS.value))
        self.updated_at = datetime.now(timezone.utc).isoformat()
        return True
