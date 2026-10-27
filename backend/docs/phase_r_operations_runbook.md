# SAARTHI — PHASE R OPERATIONS RUNBOOK & SUPPORT SOP

**Date**: August 18, 2026  
**Auditor**: Antigravity AI Operations Team  
**Scope**: Customer Support SOP, Ticket Severity Classification, Diagnostic Checklist, Non-DB Troubleshooting Steps, License Recovery & Refund Procedures.

---

## 1. Ticket Severity Classification & SLA Matrix

| Priority | Category / Criteria | Response SLA | Resolution Target | Escalation Target |
| :--- | :--- | :--- | :--- | :--- |
| **P0 — CRITICAL** | Security vulnerability, privacy leak, payment corruption, private key exposure | < 1 hour | < 4 hours | Lead Security Engineer & CTO |
| **P1 — HIGH** | Unable to activate key, paid features locked, invalid license suspension, data loss | < 4 hours | < 12 hours | Head of Support & Product Manager |
| **P2 — MEDIUM** | Feature failure, browser assistant field detection error, local model crash | < 12 hours | < 24 hours | Senior Software Engineer |
| **P3 — LOW** | UI/UX alignment issue, cosmetic bug, feature request | < 24 hours | Next Sprint | Support Agent |

---

## 2. Mandatory Support Rule

> [!CAUTION]
> **STRICT SUPPORT INVARIANT**: NEVER instruct or require end-users to manually open, modify, or execute SQL statements against local SQLite database files (`saarthi.db`). All data recovery and license state fixes MUST be handled via automated software commands, license sync endpoints, or official support utilities built into the application interface.

---

## 3. Diagnostic Checklist for Support Engineers

When a user submits a support ticket, run through the following non-invasive checklist:

1. **Verify Application Version**: Confirm user is running `v0.5.0-rc2` or later (`Settings -> About`).
2. **Check License Status**: Query vendor control plane using customer email or license key (`SAARTHI-STU-xxx`).
3. **Verify Device Fingerprint**: Confirm device hardware fingerprint matches stored activation record.
4. **Check Local Engine Connection**: Verify local Ollama service status (`http://localhost:11434/api/tags`).
5. **Inspect Log File**: Request `C:\Users\<user>\AppData\Roaming\Saarthi\logs\app.log` (strips all personal prompt/resume content automatically).

---

## 4. Customer-Safe Troubleshooting Steps

### A. Issue: License Key Shows "Invalid or Inactive" (P1)
1. Ensure system clock is set to automatic network time (prevents clock rollback triggers).
2. Open Saarthi -> Settings -> License -> Click **"Re-sync License"**.
3. Verify internet connectivity to `https://licensing.saarthi.ai`.
4. If re-sync fails, issue a license reset via Vendor Admin Panel (**"Reset Device Binding"**).

### B. Issue: Browser Assistant Not Autofilling Fields (P2)
1. Verify browser helper extension is enabled in Chrome / Edge (`chrome://extensions`).
2. Open target job portal page and click **"Inspect Form Fields"** on Saarthi floating toolbar.
3. Verify mandatory user review modal (`confirmed_by_user=True`).
4. If form structure is non-standard, use **"Map Fields Manually"** button on floating toolbar.

### C. Issue: Local LLM Engine Unresponsive / Slow (P2)
1. Open Saarthi Settings -> Model Settings.
2. Click **"Restart Ollama Engine"** button.
3. Verify GPU hardware acceleration status (NVIDIA / AMD / Apple Silicon).
4. If model files are corrupted, click **"Re-download Model Weights"**.

---

## 5. Escalation & Procedure Protocols

### A. License Recovery Procedure (P1)
1. Customer requests key recovery via support portal (`support.saarthi.ai/recover`).
2. Automated system sends Magic Link to registered billing email address.
3. Customer clicks Magic Link to display full license key and active devices.
4. If email is lost or changed, support agent verifies payment gateway order ID (Stripe `sub_xxx` / Razorpay `sub_rzp_xxx`) and updates email in vendor DB.

### B. Refund Procedure (7-Day Money-Back Guarantee) (P1)
1. Customer submits refund request within 7 days of purchase.
2. Support agent verifies purchase date in payment gateway dashboard.
3. Agent triggers `cancel_subscription` and `revoke_license` in vendor control plane.
4. Vendor server logs `REVOKE_LICENSE` event and revokes Ed25519 activation token.
5. Payment gateway issues full refund to original payment method within 3-5 business days.

### C. Database Recovery & Corruption Procedure (P1)
1. If application fails to start due to `sqlite3.DatabaseError`:
2. Instruct user to launch Saarthi with `--restore-backup` flag or click **"Restore Backup"** on crash dialog.
3. Software automatically backs up corrupt DB to `saarthi_corrupt_[timestamp].db` and restores most recent `.bak` snapshot from `AppData/Roaming/Saarthi/backups/`.
4. Zero user SQL editing required.
