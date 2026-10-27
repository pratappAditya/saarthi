# Saarthi Teams & Multi-Tenant Organization Architecture

## Executive Summary
The Teams module brings multi-tenant organization support to Saarthi, enabling team collaboration, seat allocation governance, role-based member permissions, and server-enforced data isolation.

---

## 1. Organization Structure & Roles

Organizations (`organizations`) are bound to a subscription plan (typically `TEAMS` at ₹699/user/month) and carry explicit seat limits (`seat_limit`).

### Roles & Access Matrix
- **`OWNER`**: Organization creator. Holds full billing control, member invitation/removal privileges, role assignment, and organization deletion rights.
- **`ADMIN`**: Can invite new members, view member rosters, and manage team workspaces. Cannot modify owner settings or cancel primary billing subscriptions.
- **`MEMBER`**: Accesses shared team resources, agent routines, and organization workspaces. Cannot invite or remove users.

---

## 2. Seat Limit Enforcement & Invitation Workflow

1. **Invitation Generation**: `/api/team/{org_id}/invite`
   - Checks current active member count + pending invitations against `seat_limit`.
   - If `count >= seat_limit`, server rejects request with `HTTP 400 Seat limit reached`.
   - Generates single-use invitation token stored in `organization_invitations`.
2. **Invitation Acceptance**: `/api/team/accept-invite`
   - Validates invitation token status and target email.
   - Adds user to `organization_members` with status `ACTIVE`.
   - Atomically updates organization seat utilization counter.

---

## 3. Server-Side Data Isolation

Data security across organizations is guaranteed at the database service layer:
- **`verify_org_access(user_id, org_id, required_role)`**: Every team endpoint verifies active membership before executing operations.
- **Tenant Scoping**: All queries on organization resources include `WHERE org_id = ?` filters bound to validated session parameters.
- **Cross-Tenant Prevention**: Users cannot read, modify, or list resources of organizations they do not belong to.
