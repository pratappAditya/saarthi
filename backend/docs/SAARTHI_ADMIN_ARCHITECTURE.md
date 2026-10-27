# Saarthi Admin Control Panel Architecture Specification

## Overview

The **Admin Control Panel** is the operational control plane for Saarthi, engineered as a distinct, isolated system operating ABOVE existing core services.

```
+-----------------------------------------------------------------------+
|                         Admin UI (React / Vite)                       |
|         Operational Dashboard (Separate Route Boundary)               |
+-----------------------------------------------------------------------+
                                   | HTTP / REST (JWT or Admin Header)
                                   v
+-----------------------------------------------------------------------+
|                    Admin API Layer (`/api/admin/*`)                   |
|          Server-Side RBAC Enforcement (SUPER_ADMIN, ADMIN, etc.)      |
+-----------------------------------------------------------------------+
                                   | Service Layer Calls
                                   v
+-----------------------------------------------------------------------+
|                         Admin Service Layer                           |
|  (`backend/app/admin/services/*` & `admin_audit_service.py`)          |
+-----------------------------------------------------------------------+
                                   | Wraps Core Domain Systems
                                   v
+-----------------------------------------------------------------------+
|                       Existing Saarthi Subsystems                     |
|  Auth, Plans, Entitlements, Agent Runtime, Task Store, Routine Engine,|
|  Domain Registry, Model/Voice Services, Trust & Audit Engine          |
+-----------------------------------------------------------------------+
```

## Security & Role-Based Access Control (RBAC)

The Admin Control Plane enforces server-side role validation for every endpoint.

### Role Hierarchy & Capabilities

| Role | Scope & Privileges |
|---|---|
| `SUPER_ADMIN` | Full operational control, user deletion, policy modifications, maintenance overrides. |
| `ADMIN` | User directory management, plan tier updates, agent task control, routine management, diagnostics. |
| `SUPPORT` | User issue lookup, account diagnostics, diagnostic bundle generation. Write access to user state blocked. |
| `ANALYST` | Read-only analytics across metrics, audit logs, and system status. All mutating requests blocked (HTTP 403). |

## Data Models & Schema

The control plane introduces non-destructive database migrations:

1. **`admin_users`**: Admin user registry with hashed credentials and assigned role.
2. **`admin_roles`**: Granular role definitions mapping role names to JSON permission arrays.
3. **`admin_permissions`**: System permissions catalog.
4. **`admin_sessions`**: Admin JWT/Session tokens with client IP tracking and expiration timestamps.
5. **`admin_audit_events`**: Immutable audit log recording all operational actions.

## Immutable Operational Auditing

Every consequential admin operation records an audit entry containing:
- Admin Identity (`admin_id`)
- Timestamp (UTC ISO-8601)
- Action Code
- Target Entity (`user_id`, `task_id`, `routine_id`, etc.)
- Reason (for audited changes)
- Previous State (JSON snippet)
- Resulting State (JSON snippet)
- Request Metadata (IP address, client agent)
- Automatic Secret Redaction (Passkeys, API Tokens, Passwords sanitized to `[REDACTED]`)

## Destructive Action Safety Workflow

All destructive operational actions follow a mandatory 4-step workflow:
1. **Review**: Visual summary of action impact & target entity.
2. **Confirmation**: Admin explicit review and confirmation modal.
3. **Execution**: Server-side authorized action execution.
4. **Result & Audit**: State update with immutable audit record creation.
