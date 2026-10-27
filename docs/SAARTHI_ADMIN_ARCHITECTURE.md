# Saarthi Admin Architecture Documentation

## Executive Overview
The Saarthi Admin Control Panel is the operational control plane for the Saarthi AI Operating Companion. It operates as a distinct, privileged surface with strict server-side authorization, comprehensive management capabilities across all 21 operational sub-systems, and full audit trail logging.

---

## Architectural Components

1. **Privileged Operational Surface**:
   - Built as a dedicated UI component (`AdminControlPanelView.tsx`) separate from normal user navigation.
   - Hidden from standard navigation across all 4 experience shells (`Signature`, `Forge`, `Pulse`, `Aurora`).
   - Protected by `AdminAuthModal.tsx` requiring secret key or admin account authentication.

2. **Server-Side Authorization & Middleware**:
   - `verify_admin_access` FastAPI dependency in `app/api/admin.py`.
   - Checks `X-Admin-Key` header against `settings.VENDOR_ADMIN_KEY` or validates Bearer token against SQLite `users` table for `role IN ('ADMIN', 'SUPER_ADMIN')`.
   - Returns `403 Forbidden` for unauthenticated or standard `USER` role accounts.

3. **Database & Persistence Engine ([app/db/admin_db.py](file:///e:/Saarthi/backend/app/db/admin_db.py))**:
   - `admin_audit_log`: Records admin ID, action, target user, IP address, details, and ISO timestamp.
   - `feature_flags`: Dynamic feature flags with rollout percentages.
   - `maintenance_mode`: Global maintenance toggle, message, and bypass whitelist.
   - `tool_policies`: Dynamic tool risk classification and permission requirements.
   - `organizations`: Teams and enterprise account rosters.
   - `ip_bans`: IP/device security ban list.

4. **21 Operational Sub-Systems**:
   - **Admin Auth & RBAC**: `POST /api/admin/auth/login`, `GET /api/admin/auth/verify`.
   - **Dashboard Overview**: Metrics aggregation (`GET /api/admin/dashboard`).
   - **User Directory**: Search, role update, plan update, suspend/restore, delete.
   - **Subscriptions & Plans**: Canonical plan tier switcher (`FREE` -> `ENTERPRISE`).
   - **Entitlement Matrix**: Capability mappings & dynamic overrides.
   - **Quota Management**: Usage quota tracking & reset.
   - **AI Configuration**: Model provider, temperature, max tokens, model switching.
   - **Domain Pack Manager**: 17 domain pack state management.
   - **Tool Policy Manager**: Risk level & permission policy overrides.
   - **Agent Runtime Monitor**: Running task graphs & cancellation.
   - **Routines Monitor**: User routines system-wide management.
   - **Permissions Queue**: Pending risk approvals queue & admin override.
   - **Trust & Security Audit**: Audit log viewer & trust event tracking.
   - **System Health**: Hardware metrics (CPU, RAM, VRAM), SQLite integrity check.
   - **Error Log Monitor**: Incident tracking.
   - **Feature Flags**: Controlled rollout percentages.
   - **Maintenance Controls**: Global maintenance mode toggle.
   - **Feedback Management**: User support & feedback submissions.
   - **Organizations**: Team seat allocations.
   - **Security Controls**: IP & device ban manager.
   - **Build Information**: Component versioning & deployment info.
