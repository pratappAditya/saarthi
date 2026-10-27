# Saarthi Admin Security Model Documentation

## Security Principles

1. **Strict Server-Side Authorization**:
   - Client-side visibility alone is not trusted. All administrative endpoints enforce `verify_admin_access` on the backend.
   - Non-admin users attempting to invoke any `/api/admin/*` endpoint are blocked with `HTTP 403 Forbidden`.

2. **Privilege Escalation Prevention**:
   - Standard user registration assigns `role = 'USER'`.
   - Changing a user role to `ADMIN` or `SUPER_ADMIN` requires an existing authenticated admin session or `VENDOR_ADMIN_KEY`.
   - Users cannot modify their own `role` or `subscription_plan` via user-facing profile endpoints.

3. **Complete Audit Trail**:
   - Every administrative modification (POST, PUT, PATCH, DELETE) executes `AdminRepository.log_action()`.
   - Logs store: `admin_id`, `action`, `target_user`, `details`, `ip_address`, `timestamp`.

4. **Maintenance Mode Enforcement**:
   - Global maintenance mode can be toggled by admins.
   - Whitelisted IPs/users bypass maintenance mode, while standard users receive clear operational status feedback.

5. **Security Ban & Abuse Control**:
   - IPs or device fingerprints added to `ip_bans` are restricted from privileged API execution.
