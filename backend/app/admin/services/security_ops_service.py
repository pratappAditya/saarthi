import logging
from typing import Dict, Any, List, Optional
from app.admin.audit.admin_audit_service import admin_audit_service
from app.admin.repositories.admin_repository import AdminRepository
from app.intelligence.audit.intelligence_audit import audit_service

logger = logging.getLogger("app.admin.services.security_ops")

class SecurityOperationsService:
    @classmethod
    def get_security_overview(cls, limit: int = 100) -> Dict[str, Any]:
        admin_events = admin_audit_service.list_events(limit=limit)
        trust_events = audit_service.list_audit_logs(limit=limit)
        bans = AdminRepository.list_ip_bans()

        return {
            "status": "success",
            "audit_timeline": admin_events,
            "trust_events": trust_events,
            "security_bans": bans,
            "security_summary": {
                "prompt_injection_detections": 0,
                "sandbox_violations": 0,
                "entitlement_violations": 0,
                "active_bans_count": len(bans)
            }
        }

    @classmethod
    def add_ban(cls, identifier: str, ban_type: str, reason: str, admin_id: str) -> Dict[str, Any]:
        ban = AdminRepository.add_ip_ban(identifier=identifier, ban_type=ban_type, reason=reason, admin_id=admin_id)
        admin_audit_service.record_event(
            admin_id=admin_id,
            action="ADD_SECURITY_BAN",
            target=identifier,
            reason=reason,
            resulting_state={"banned": True, "ban_type": ban_type}
        )
        return ban

    @classmethod
    def remove_ban(cls, identifier: str, admin_id: str) -> Dict[str, Any]:
        unbanned = AdminRepository.remove_ip_ban(identifier)
        admin_audit_service.record_event(
            admin_id=admin_id,
            action="REMOVE_SECURITY_BAN",
            target=identifier,
            reason="Ban lifted by admin",
            resulting_state={"unbanned": unbanned}
        )
        return {"identifier": identifier, "unbanned": unbanned}

security_ops_service = SecurityOperationsService()
