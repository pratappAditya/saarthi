import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

logger = logging.getLogger("app.intelligence.domain_handoff")

class DomainHandoff(BaseModel):
    handoff_id: str
    source_domain: str
    destination_domain: str
    reason: str
    input_artifact: Optional[Dict[str, Any]] = None
    output_artifact: Optional[Dict[str, Any]] = None
    confidence: float = 0.95
    provenance: Dict[str, Any] = Field(default_factory=dict)
    verification_status: str = "verified" # "verified" | "pending" | "flagged"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DomainHandoffManager:
    def __init__(self):
        self.handoff_history: List[DomainHandoff] = []

    def create_handoff(
        self,
        source_domain: str,
        destination_domain: str,
        reason: str,
        input_artifact: Optional[Dict[str, Any]] = None,
        output_artifact: Optional[Dict[str, Any]] = None,
        confidence: float = 0.95,
        provenance: Optional[Dict[str, Any]] = None
    ) -> DomainHandoff:
        import uuid
        handoff = DomainHandoff(
            handoff_id=f"handoff_{uuid.uuid4().hex[:8]}",
            source_domain=source_domain,
            destination_domain=destination_domain,
            reason=reason,
            input_artifact=input_artifact,
            output_artifact=output_artifact,
            confidence=confidence,
            provenance=provenance or {
                "source": source_domain,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "evidence_type": "domain_handoff_payload"
            },
            verification_status="verified"
        )
        self.handoff_history.append(handoff)
        logger.info(f"Cross-Domain Handoff created: {source_domain} -> {destination_domain} ({reason})")
        return handoff

    def get_handoffs_for_task(self, task_id: str) -> List[DomainHandoff]:
        return [h for h in self.handoff_history if h.provenance.get("task_id") == task_id]

domain_handoff_manager = DomainHandoffManager()
