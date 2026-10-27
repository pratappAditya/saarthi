# Saarthi Admin Control Panel Manual QA Protocol & Scenario Guide

## Test Scenarios & Manual Verification Checklist

1. **Scenario 1: Non-Admin API Access Rejection**:
   - Call `/api/admin/dashboard` without `X-Admin-Key` or Bearer token.
   - **Expected**: HTTP 403 Forbidden (`Unauthorized admin access.`).

2. **Scenario 2: Admin Login via Key**:
   - Post `admin_key` to `/api/admin/auth/login`.
   - **Expected**: HTTP 200 OK, returns admin session token.

3. **Scenario 3: System Dashboard Overview**:
   - Fetch `/api/admin/dashboard` with valid admin key.
   - **Expected**: Returns user counts, plan distribution, agent task count, hardware info.

4. **Scenario 4: User Search & Plan Upgrade**:
   - Post plan update (`POWER`) for user `test_user` to `/api/admin/update-plan`.
   - **Expected**: User plan updated in database to `POWER`, action logged to `admin_audit_log`.

5. **Scenario 5: User Suspension & Session Revocation**:
   - Post `/api/admin/users/suspend` for target user.
   - **Expected**: User role updated to `SUSPENDED`, active sessions deleted from `sessions` table.

6. **Scenario 6: User Account Restoration**:
   - Post `/api/admin/users/restore` for suspended user.
   - **Expected**: User role restored to `USER`.

7. **Scenario 7: Feature Flag Toggle**:
   - Toggle feature flag `experimental_nemotron_v3` to `enabled = True`, `rollout = 50%`.
   - **Expected**: Feature flag updated in `feature_flags` table and audit logged.

8. **Scenario 8: Maintenance Mode Override**:
   - Toggle maintenance mode to `enabled = True`.
   - **Expected**: Maintenance mode status returned as `ENABLED`.

9. **Scenario 9: Tool Policy Override**:
   - Set tool policy for `terminal` to `permission_level = ADMIN_APPROVAL`.
   - **Expected**: Tool policy saved in `tool_policies` table.

10. **Scenario 10: Audit Log Recording**:
    - Fetch `/api/admin/audit-logs`.
    - **Expected**: All admin actions recorded chronologically with admin ID, action, details, and timestamp.
