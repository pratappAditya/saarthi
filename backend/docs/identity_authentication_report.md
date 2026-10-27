# Saarthi User Identity & Authentication Architecture Report

## Executive Summary
Saarthi now features an enterprise-grade user identity and session management architecture built with strict separation between standard user credentials and administrative access controls. The identity system provides registration, secure password hashing, email verification, session inspection, single and multi-device revocation, and optional 2FA architecture.

---

## 1. Core Identity & Authentication Capabilities

### Registration & Verification
- **Registration**: Users register via `/api/auth/register` with validated email addresses and high-entropy passwords. Password complexity is enforced server-side.
- **Password Hashing**: Utilizes SHA-256 with unique per-user cryptographic salts (`salt` + `password`), preventing rainbow table lookups and credential exposure.
- **Email Verification**: Generates single-use 64-character verification tokens stored in `email_verifications`. Verification is completed via `/api/auth/verify-email`.

### Session Management & Inspection
- **Session Tokens**: High-entropy 64-character session tokens (`sess_<hex>`) generated with 30-day sliding expiration limits.
- **Session Inspection**: `/api/auth/sessions` returns active devices, client IP addresses, user agents, creation timestamps, and expiration metadata.
- **Revocation**:
  - `/api/auth/sessions/{session_id}`: Revokes an individual session/device.
  - `/api/auth/logout-all`: Instantly revokes all active sessions for a user across all devices.

### Security Controls & Rate Limiting
- **Brute-Force Protection**: `login_attempts` table tracks failed authentication attempts. After 5 consecutive failures, the account key is locked out for 15 minutes.
- **Strict Data Redaction**: Passwords, password hashes, reset tokens, and session secrets are NEVER returned in API payloads or exposed via the Admin Control Panel.
- **Admin vs. User Identity Separation**: Admin authentication (`/api/admin/auth/*`) is maintained in distinct tables (`admin_users`, `admin_sessions`) and enforced via independent RBAC dependencies (`verify_admin_access`). Normal user sessions cannot access admin endpoints unless granted explicit elevated admin roles (`ADMIN`, `SUPER_ADMIN`).

---

## 2. API Endpoint Matrix

| Method | Endpoint | Description | Access |
|---|---|---|---|
| POST | `/api/auth/register` | Register new user account | Public |
| POST | `/api/auth/login` | Authenticate user & receive session token | Public (Rate-limited) |
| POST | `/api/auth/logout` | Revoke current session token | Authenticated |
| POST | `/api/auth/logout-all` | Revoke all active user sessions | Authenticated |
| POST | `/api/auth/verify-email` | Verify email via token | Public |
| POST | `/api/auth/reset-password/request` | Request password reset token | Public |
| POST | `/api/auth/reset-password/confirm` | Reset password using valid token | Public |
| GET | `/api/auth/sessions` | List active sessions & devices | Authenticated |
| DELETE | `/api/auth/sessions/{session_id}` | Revoke target session | Authenticated |
| POST | `/api/auth/2fa/setup` | Generate TOTP secret & QR uri | Authenticated |
| POST | `/api/auth/2fa/verify` | Enable/verify 2FA TOTP code | Authenticated |

---

## 3. Security Audit & Redaction Verification
- **Automated Verification**: Verified via `backend/tests/test_identity_billing_teams.py` (Scenarios 1-5).
- **Audit Logging**: All identity status changes emit secret-sanitized audit events.
