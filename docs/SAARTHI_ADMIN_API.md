# Saarthi Admin Control Panel API Documentation

## Authentication & Authorization Headers

All Admin Control Panel endpoints require one of the following HTTP headers:
- `X-Admin-Key: <VENDOR_ADMIN_KEY>`
- `Authorization: Bearer <ADMIN_SESSION_TOKEN>`

Unauthenticated or unauthorized requests return `HTTP 403 Forbidden`.

---

## Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/admin/auth/login` | Authenticate admin via key or credentials |
| `GET` | `/api/admin/auth/verify` | Verify current admin token status |
| `GET` | `/api/admin/dashboard` | Consolidated system metrics & hardware overview |
| `GET` | `/api/admin/users` | List & filter user accounts |
| `GET` | `/api/admin/users/{id}/details` | View user profile, devices, orders, and quotas |
| `POST` | `/api/admin/users/update-role` | Update user role (`USER`, `ADMIN`, `SUPER_ADMIN`, `SUSPENDED`) |
| `POST` | `/api/admin/update-plan` | Update user plan (`FREE`, `STUDENT`, `PERSONAL`, `POWER`, `TEAMS`, `ENTERPRISE`) |
| `POST` | `/api/admin/users/suspend` | Suspend account and revoke active sessions |
| `POST` | `/api/admin/users/restore` | Restore account to active `USER` status |
| `DELETE` | `/api/admin/users/{id}` | Permanently delete user account |
| `GET` | `/api/admin/subscriptions` | Subscription tier user breakdown |
| `GET` | `/api/admin/entitlements` | System entitlement capability matrix |
| `GET` | `/api/admin/quotas` | Free usage quotas per user/device |
| `POST` | `/api/admin/quotas/reset` | Reset usage quota for user/device |
| `GET` | `/api/admin/ai/config` | AI model provider settings |
| `POST` | `/api/admin/ai/config` | Update model temperature, provider, max tokens |
| `GET` | `/api/admin/domains` | List 17 registered domain packs |
| `GET` | `/api/admin/tools` | List registered tools and risk policies |
| `POST` | `/api/admin/tools/policy` | Set tool risk classification & permission requirement |
| `GET` | `/api/admin/agent/tasks` | List running and completed agent tasks |
| `POST` | `/api/admin/agent/tasks/{id}/cancel` | Force-cancel running agent task |
| `GET` | `/api/admin/routines` | List user routines system-wide |
| `POST` | `/api/admin/routines/{id}/toggle` | Pause or resume user routine |
| `GET` | `/api/admin/permissions/pending` | List pending risk approvals queue |
| `POST` | `/api/admin/permissions/{id}/action` | Force approve or deny pending risk request |
| `GET` | `/api/admin/audit-logs` | Query administrative action audit log |
| `GET` | `/api/admin/trust-events` | Query system trust & security audit events |
| `GET` | `/api/admin/diagnostics` | Server hardware stats & database size |
| `POST` | `/api/admin/diagnostics/db-check` | Run SQLite database integrity check |
| `GET` | `/api/admin/feature-flags` | List system feature flags |
| `POST` | `/api/admin/feature-flags/update` | Toggle feature flag and update rollout percentage |
| `GET` | `/api/admin/maintenance` | Get maintenance mode state |
| `POST` | `/api/admin/maintenance/toggle` | Toggle maintenance mode with custom message |
| `GET` | `/api/admin/feedback` | List user feedback submissions |
| `GET` | `/api/admin/organizations` | List team & enterprise organizations |
| `POST` | `/api/admin/organizations` | Create team/enterprise organization |
| `GET` | `/api/admin/security/bans` | List banned IPs/devices |
| `POST` | `/api/admin/security/ban` | Ban IP or device identifier |
| `POST` | `/api/admin/security/unban` | Unban IP or device identifier |
| `GET` | `/api/admin/version` | Component version & deployment details |
