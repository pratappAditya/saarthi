import secrets
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from app.db.connection import get_db_connection, with_db_retry

class TeamService:
    @classmethod
    @with_db_retry()
    def create_organization(cls, owner_id: str, name: str, plan_name: str = "TEAMS", seat_limit: int = 5) -> Dict[str, Any]:
        org_id = f"org_{secrets.token_hex(8)}"
        now_str = datetime.now(timezone.utc).isoformat()

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO organizations (org_id, name, owner_id, subscription_plan, seat_limit, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (org_id, name, owner_id, plan_name.upper(), seat_limit, now_str, now_str))

            conn.execute("""
                INSERT INTO organization_members (org_id, user_id, role, status, joined_at)
                VALUES (?, ?, 'OWNER', 'ACTIVE', ?)
            """, (org_id, owner_id, now_str))

            conn.commit()

        return cls.get_organization_details(org_id, owner_id)

    @classmethod
    @with_db_retry()
    def verify_org_access(cls, user_id: str, org_id: str, required_roles: Optional[List[str]] = None) -> Dict[str, Any]:
        with get_db_connection() as conn:
            member = conn.execute("""
                SELECT * FROM organization_members WHERE org_id = ? AND user_id = ? AND status = 'ACTIVE'
            """, (org_id, user_id)).fetchone()

            if not member:
                raise HTTPException(status_code=403, detail="Access denied. User is not an active member of this organization.")

            m_dict = dict(member)
            if required_roles and m_dict["role"] not in required_roles:
                raise HTTPException(status_code=403, detail=f"Action requires one of roles: {required_roles}")

            return m_dict

    @classmethod
    @with_db_retry()
    def get_organization_details(cls, org_id: str, user_id: str) -> Dict[str, Any]:
        cls.verify_org_access(user_id, org_id)
        with get_db_connection() as conn:
            org = conn.execute("SELECT * FROM organizations WHERE org_id = ?", (org_id,)).fetchone()
            if not org:
                raise HTTPException(status_code=404, detail="Organization not found.")

            org_dict = dict(org)
            members = conn.execute("""
                SELECT m.id, m.org_id, m.user_id, m.role, m.status, m.joined_at, u.email, u.full_name
                FROM organization_members m
                JOIN users u ON m.user_id = u.user_id
                WHERE m.org_id = ?
            """, (org_id,)).fetchall()

            invites = conn.execute("SELECT * FROM organization_invitations WHERE org_id = ? AND status = 'PENDING'", (org_id,)).fetchall()

            member_list = [dict(m) for m in members]
            invite_list = [dict(i) for i in invites]

            return {
                "organization": org_dict,
                "members": member_list,
                "invitations": invite_list,
                "seat_usage": {
                    "used_seats": len(member_list),
                    "seat_limit": org_dict["seat_limit"],
                    "available_seats": max(0, org_dict["seat_limit"] - len(member_list))
                }
            }

    @classmethod
    @with_db_retry()
    def invite_member(cls, org_id: str, actor_id: str, email: str, role: str = "MEMBER") -> Dict[str, Any]:
        cls.verify_org_access(actor_id, org_id, required_roles=["OWNER", "ADMIN"])
        email = email.strip().lower()
        now = datetime.now(timezone.utc)
        now_str = now.isoformat()
        expires_at = (now + timedelta(days=7)).isoformat()

        with get_db_connection() as conn:
            org = conn.execute("SELECT seat_limit FROM organizations WHERE org_id = ?", (org_id,)).fetchone()
            members_count = conn.execute("SELECT COUNT(*) as count FROM organization_members WHERE org_id = ?", (org_id,)).fetchone()["count"]

            if members_count >= org["seat_limit"]:
                raise HTTPException(status_code=400, detail=f"Seat limit of {org['seat_limit']} reached. Upgrade seats to invite more members.")

            invite_token = secrets.token_urlsafe(32)
            invite_id = f"inv_{secrets.token_hex(8)}"

            conn.execute("""
                INSERT INTO organization_invitations (invite_id, org_id, email, role, token, status, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, 'PENDING', ?, ?)
            """, (invite_id, org_id, email, role.upper(), invite_token, now_str, expires_at))

            conn.commit()

        return {
            "status": "success",
            "message": f"Invitation dispatched to {email}.",
            "invite_token": invite_token
        }

    @classmethod
    @with_db_retry()
    def accept_invitation(cls, token: str, user_id: str) -> Dict[str, Any]:
        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            invite = conn.execute("SELECT * FROM organization_invitations WHERE token = ? AND status = 'PENDING'", (token,)).fetchone()
            if not invite:
                raise HTTPException(status_code=400, detail="Invalid or expired organization invitation.")

            inv_dict = dict(invite)
            if inv_dict["expires_at"] < now_str:
                raise HTTPException(status_code=400, detail="Invitation token has expired.")

            # Add to members
            conn.execute("""
                INSERT INTO organization_members (org_id, user_id, role, status, joined_at)
                VALUES (?, ?, ?, 'ACTIVE', ?)
                ON CONFLICT(org_id, user_id) DO UPDATE SET role = excluded.role, status = 'ACTIVE'
            """, (inv_dict["org_id"], user_id, inv_dict["role"], now_str))

            conn.execute("UPDATE organization_invitations SET status = 'ACCEPTED' WHERE id = ?", (inv_dict["id"],))
            conn.commit()

            return cls.get_organization_details(inv_dict["org_id"], user_id)

    @classmethod
    @with_db_retry()
    def remove_member(cls, org_id: str, actor_id: str, target_user_id: str) -> bool:
        cls.verify_org_access(actor_id, org_id, required_roles=["OWNER", "ADMIN"])
        with get_db_connection() as conn:
            target = conn.execute("SELECT role FROM organization_members WHERE org_id = ? AND user_id = ?", (org_id, target_user_id)).fetchone()
            if not target:
                raise HTTPException(status_code=404, detail="Member not found in organization.")

            if target["role"] == "OWNER" and actor_id != target_user_id:
                raise HTTPException(status_code=403, detail="Organization owner cannot be removed. Transfer ownership first.")

            conn.execute("DELETE FROM organization_members WHERE org_id = ? AND user_id = ?", (org_id, target_user_id))
            conn.commit()
            return True

    @classmethod
    @with_db_retry()
    def update_member_role(cls, org_id: str, actor_id: str, target_user_id: str, new_role: str) -> bool:
        cls.verify_org_access(actor_id, org_id, required_roles=["OWNER"])
        new_role_upper = new_role.upper()
        if new_role_upper not in ["OWNER", "ADMIN", "MEMBER"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be OWNER, ADMIN, or MEMBER.")

        with get_db_connection() as conn:
            conn.execute("UPDATE organization_members SET role = ? WHERE org_id = ? AND user_id = ?", (new_role_upper, org_id, target_user_id))
            if new_role_upper == "OWNER":
                conn.execute("UPDATE organizations SET owner_id = ? WHERE org_id = ?", (target_user_id, org_id))
            conn.commit()
            return True

    @classmethod
    @with_db_retry()
    def update_seat_limit(cls, org_id: str, actor_id: str, new_seat_limit: int) -> Dict[str, Any]:
        cls.verify_org_access(actor_id, org_id, required_roles=["OWNER", "ADMIN"])
        if new_seat_limit < 1:
            raise HTTPException(status_code=400, detail="Seat limit must be at least 1.")

        now_str = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            conn.execute("UPDATE organizations SET seat_limit = ?, updated_at = ? WHERE org_id = ?", (new_seat_limit, now_str, org_id))
            conn.commit()

        return cls.get_organization_details(org_id, actor_id)

    @classmethod
    @with_db_retry()
    def get_user_organizations(cls, user_id: str) -> List[Dict[str, Any]]:
        with get_db_connection() as conn:
            rows = conn.execute("""
                SELECT o.*, m.role as user_role, m.joined_at
                FROM organizations o
                JOIN organization_members m ON o.org_id = m.org_id
                WHERE m.user_id = ? AND m.status = 'ACTIVE'
            """, (user_id,)).fetchall()
            return [dict(r) for r in rows]
