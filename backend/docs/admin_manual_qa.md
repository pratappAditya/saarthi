# Admin Control Panel Manual QA Verification Checklist

| Module | Verification Step | Expected Outcome | Status |
|---|---|---|---|
| **Admin Auth** | Login via `VENDOR_ADMIN_KEY` | Successfully returns SUPER_ADMIN session token | PASS |
| **Admin Auth** | Login with invalid credentials | Blocked with HTTP 401 Unauthorized | PASS |
| **RBAC Enforcement** | Access endpoint as `ANALYST` role and trigger user suspension | Blocked with HTTP 403 Forbidden | PASS |
| **Dashboard** | View metrics overview | Correctly displays total users, active sessions, running agent tasks, plan breakdown | PASS |
| **User Management** | Search user by email | User listed with details, role, and subscription plan | PASS |
| **User Management** | Update user plan to `POWER` | Plan upgraded cleanly & recorded in audit log | PASS |
| **User Management** | Suspend user account | Status updated to `SUSPENDED`, all user sessions revoked | PASS |
| **Plan Management** | View canonical catalog | Displays FREE, STUDENT, PERSONAL, POWER, TEAMS, ENTERPRISE | PASS |
| **Entitlement Management**| Apply capability override | Override stored in `entitlement_overrides` and reflected in entitlement inspection | PASS |
| **Agent Operations** | List running & failed tasks | Shows task states, execution steps, and error details | PASS |
| **Agent Operations** | Cancel active agent task | Task state updated to `cancelled`, task graph stopped | PASS |
| **Model Operations** | View Ollama status & multimodal engines | Displays Ollama connection status, model list, STT/TTS/OCR/Vision status | PASS |
| **Domain Operations** | Inspect registered domain packs | All 17 domain packs (General, Career, Education, Writing, Research, Business, Software Engineering, Cybersecurity, Computer Science, Mechanical Engineering, Civil Engineering, Electrical Engineering, Biology, Chemistry, Physics, Archaeology, History) listed with status & metrics | PASS |
| **Automation Operations**| Pause / Resume routine | Routine state updated cleanly and logged | PASS |
| **Security & Trust** | Review audit log & security bans | Full timeline shown with secret redaction (`[REDACTED]`) | PASS |
| **System Health** | View hardware profile & DB check | Reports CPU, RAM, disk space, and SQLite PRAGMA integrity status | PASS |
| **Support & Diagnostics**| Lookup user issue & generate bundle | Returns diagnostic summary JSON without sensitive secrets | PASS |
