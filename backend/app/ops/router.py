"""
Saarthi Ops Subsystem API Router.
Exposes read-only monitoring and diagnostic endpoints.
Strictly enforced by server-side RBAC (SUPER_ADMIN, ADMIN, ANALYST).
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from pydantic import BaseModel

from app.admin.auth.admin_auth import verify_admin_access, require_admin_role
from app.admin.audit.admin_audit_service import admin_audit_service
from app.ops.collector import ops_collector
from app.ops.diagnostics import ops_diagnostic_engine
from app.ops.config import (
    ALLOWED_OPS_SERVICES,
    MAX_ERROR_LOGS_LIMIT,
    DEFAULT_ERROR_LOGS_LIMIT,
    MAX_AUDIT_EVENTS_LIMIT,
    DEFAULT_AUDIT_EVENTS_LIMIT
)
from app.ops.redactor import ops_redactor
from app.ops.authenticity import snapshot_authenticity_service

logger = logging.getLogger("app.ops.router")

router = APIRouter(prefix="/ops", tags=["SaarthiOps"])

# Request model for triggering AI diagnostic reasoning
class DiagnoseRequest(BaseModel):
    snapshot_id: Optional[str] = None
    snapshot_envelope: Optional[Dict[str, Any]] = None
    incident_id: Optional[str] = None
    include_recent_errors: bool = True

class VerifySnapshotRequest(BaseModel):
    envelope: Dict[str, Any]

@router.get("/health")
def get_ops_health(
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "ANALYST"]))
) -> Dict[str, Any]:
    """Returns top-level Ops health summary, service counts, and active incidents."""
    admin_audit_service.record_event(
        admin_id=admin.get("admin_id", "UNKNOWN"),
        action="OPS_VIEW_HEALTH",
        target="ops/health",
        reason="View overall Ops health"
    )
    return ops_collector.get_overall_ops_health()

@router.get("/metrics")
def get_ops_metrics(
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "ANALYST"]))
) -> Dict[str, Any]:
    """Returns safe system hardware metrics (CPU, RAM, Disk, Uptime)."""
    admin_audit_service.record_event(
        admin_id=admin.get("admin_id", "UNKNOWN"),
        action="OPS_VIEW_METRICS",
        target="ops/metrics",
        reason="View system hardware metrics"
    )
    return ops_collector.get_system_metrics()

@router.get("/services")
def list_ops_services(
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "ANALYST"]))
) -> List[Dict[str, Any]]:
    """Returns the status of all strictly allowlisted Saarthi services."""
    admin_audit_service.record_event(
        admin_id=admin.get("admin_id", "UNKNOWN"),
        action="OPS_LIST_SERVICES",
        target="ops/services",
        reason="List configured Saarthi services"
    )
    return ops_collector.get_all_services()

@router.get("/services/{service_id}")
def get_ops_service_detail(
    service_id: str,
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "ANALYST"]))
) -> Dict[str, Any]:
    """
    Returns detailed health for a specific allowlisted service.
    Rejects unauthorized or unconfigured service names with HTTP 400.
    """
    clean_id = service_id.strip().lower()
    if clean_id not in ALLOWED_OPS_SERVICES:
        raise HTTPException(
            status_code=400,
            detail=f"Service '{service_id}' is not an allowlisted Saarthi service."
        )

    admin_audit_service.record_event(
        admin_id=admin.get("admin_id", "UNKNOWN"),
        action="OPS_VIEW_SERVICE_DETAIL",
        target=f"ops/services/{clean_id}",
        reason=f"Inspect service {clean_id}"
    )
    return ops_collector.get_service_health(clean_id)

@router.get("/errors")
def get_ops_recent_errors(
    request: Request,
    limit: int = Query(DEFAULT_ERROR_LOGS_LIMIT, ge=1, le=MAX_ERROR_LOGS_LIMIT),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "ANALYST"]))
) -> List[Dict[str, Any]]:
    """Returns recent sanitized application error events with full secret redaction."""
    admin_audit_service.record_event(
        admin_id=admin.get("admin_id", "UNKNOWN"),
        action="OPS_VIEW_ERRORS",
        target="ops/errors",
        reason="View recent sanitized application errors"
    )
    return ops_collector.get_recent_errors(limit=limit)

@router.get("/containers")
def get_ops_containers(
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "ANALYST"]))
) -> Dict[str, Any]:
    """
    Returns read-only container status for allowlisted Saarthi containers.
    Reports 'unavailable' in local development mode without container manager.
    """
    admin_audit_service.record_event(
        admin_id=admin.get("admin_id", "UNKNOWN"),
        action="OPS_VIEW_CONTAINERS",
        target="ops/containers",
        reason="Inspect read-only container states"
    )
    return ops_collector.get_container_status()

@router.get("/snapshots")
def get_ops_snapshots(
    request: Request,
    limit: int = Query(10, ge=1, le=50),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "ANALYST"]))
) -> List[Dict[str, Any]]:
    """Returns recent monitoring snapshots."""
    admin_audit_service.record_event(
        admin_id=admin.get("admin_id", "UNKNOWN"),
        action="OPS_VIEW_SNAPSHOTS",
        target="ops/snapshots",
        reason="View historical monitoring snapshots"
    )
    return ops_collector.get_snapshots(limit=limit)

@router.get("/incidents")
def get_ops_incidents(
    request: Request,
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "ANALYST"]))
) -> List[Dict[str, Any]]:
    """Returns detected active and recent infrastructure incidents."""
    admin_audit_service.record_event(
        admin_id=admin.get("admin_id", "UNKNOWN"),
        action="OPS_VIEW_INCIDENTS",
        target="ops/incidents",
        reason="View active infrastructure incidents"
    )
    return ops_collector.get_incidents()

@router.post("/snapshots/verify")
def verify_ops_snapshot(
    request: Request,
    payload: VerifySnapshotRequest = Body(...),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "ANALYST"]))
) -> Dict[str, Any]:
    """Cryptographically verifies a signed snapshot envelope using HMAC-SHA256 or Ed25519."""
    is_valid, reason, meta = snapshot_authenticity_service.verify_envelope(payload.envelope)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Snapshot verification failed: {reason}")
    ops_collector.register_verified_snapshot(payload.envelope, meta)
    return {
        "status": "verified",
        "reason": reason,
        "metadata": meta
    }

@router.post("/diagnose")
def trigger_ops_diagnosis(
    request: Request,
    payload: DiagnoseRequest = Body(...),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN"]))
) -> Dict[str, Any]:
    """
    Executes read-only AI diagnostic reasoning on current or specified snapshot.
    Produces structured facts, hypotheses, evidence, missing evidence, safe steps, and shared VPS impact.
    Strictly non-executing.
    """
    # 1. Unpack snapshot from payload envelope or generate/find signed snapshot
    snapshot_data = None

    if payload.snapshot_envelope:
        # Externally supplied snapshot across trust boundary -> Verify authenticity & freshness
        is_valid, reason, meta = snapshot_authenticity_service.verify_envelope(payload.snapshot_envelope)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Untrusted snapshot rejected: {reason}")
        ops_collector.register_verified_snapshot(payload.snapshot_envelope, meta)
        snapshot_data = payload.snapshot_envelope.get("payload", {})

    elif payload.snapshot_id:
        for s in ops_collector.get_snapshots(limit=50):
            inner = s.get("payload", {}) if isinstance(s, dict) and "payload" in s else s
            if inner.get("snapshot_id") == payload.snapshot_id:
                snapshot_data = inner
                break
        if not snapshot_data:
            raise HTTPException(status_code=404, detail=f"Snapshot '{payload.snapshot_id}' not found.")
    else:
        signed_snap = ops_collector.create_snapshot()
        snapshot_data = signed_snap.get("payload", {})

    # Find incident if requested
    incident = None
    if payload.incident_id:
        for inc in ops_collector.get_incidents():
            if inc.get("incident_id") == payload.incident_id:
                incident = inc
                break

    recent_errors = ops_collector.get_recent_errors(limit=10) if payload.include_recent_errors else []

    diagnosis = ops_diagnostic_engine.diagnose_snapshot(
        snapshot=snapshot_data,
        recent_errors=recent_errors,
        incident_context=incident
    )

    admin_audit_service.record_event(
        admin_id=admin.get("admin_id", "UNKNOWN"),
        action="OPS_TRIGGER_DIAGNOSIS",
        target=f"ops/diagnose/{snapshot_data.get('snapshot_id', 'unknown')}",
        reason="Triggered AI diagnostic analysis of system telemetry",
        resulting_state={"diagnosis_mode": diagnosis.get("diagnostic_mode"), "overall_health": diagnosis.get("overall_health")}
    )

    return diagnosis

@router.get("/audit")
def get_ops_audit_events(
    request: Request,
    limit: int = Query(DEFAULT_AUDIT_EVENTS_LIMIT, ge=1, le=MAX_AUDIT_EVENTS_LIMIT),
    admin: Dict[str, Any] = Depends(require_admin_role(["SUPER_ADMIN", "ADMIN", "ANALYST"]))
) -> List[Dict[str, Any]]:
    """Returns audit log records for Ops data access and actions."""
    return admin_audit_service.list_events(limit=limit, action_filter="OPS_")
