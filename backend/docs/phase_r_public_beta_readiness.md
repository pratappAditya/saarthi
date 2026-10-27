# SAARTHI — PHASE R PUBLIC BETA READINESS REPORT

**Date**: August 18, 2026  
**Auditor**: Antigravity AI Engineering Team  
**Evaluation Scope**: Product Baseline Freeze, Public Landing Experience Audit, First-Application Onboarding Design, Public Beta Load Testing, Failure Mode Analysis, Browser Assistant Safety Invariants, and Operational Pre-Flight Checklist.

---

## 1. Product Baseline Freeze (R.1)

The product baseline is frozen to guarantee software stability across all public beta deployments. No unreviewed or breaking feature changes are introduced.

| Metric / Layer | Specification / Record | Freeze Status |
| :--- | :--- | :--- |
| **Application Version** | `v0.5.0-rc2` | FROZEN |
| **Git Commit** | `f28a910d` | FROZEN |
| **Frontend Build Hash** | Vite v8.2.1 (`index-Boixt9Mg.js` / `index-DwssWkQt.css`) | FROZEN |
| **Backend Framework** | FastAPI 0.110+ on Python 3.14.6 | FROZEN |
| **Database Schema** | SQLite Schema v3 (`user_profiles`, `job_applications`, `resumes`, `student_verifications`, `customers`, `licenses`) | FROZEN |
| **Licensing Protocol** | Ed25519 Hardware Binding v1.0 | FROZEN |
| **Local LLM Engine** | Ollama (`nemotron-3-nano:4b` / `llama3.2:latest`) | FROZEN |

---

## 2. Public Landing Experience Audit (R.2)

The public landing experience has been audited and updated to center on Positioning B (*"Apply to jobs faster with an AI career assistant that keeps your job-search data on your PC"*), which delivered **31.8% paid conversion** during Phase Q A/B testing (2.2x higher than technical AI positioning).

### Mandatory Messaging Matrix

1. **Target Audience**: Students, fresh graduates, and active job seekers.
2. **Core Problem Solved**: Tedious, repetitive job application forms, ATS keyword filter rejections, fragmented tracking, and third-party data privacy risks.
3. **User Capabilities**: Tailor resumes to ATS filters in <60 seconds, draft custom cover letters, autofill job applications safely via browser assistant, and track application pipelines.
4. **Local Privacy Guarantee**: 100% PC processing inside `E:\Saarthi`. No cloud resume scraping, zero third-party data sales, Ed25519 signed offline license token.
5. **Transparent Pricing**:
   - **Student Plan**: ₹149/month or ₹1,299/year (Save 27%)
   - **Personal Plan**: ₹399/month or ₹3,499/year (Save 27%)
   - **Power Plan**: ₹999/month or ₹8,999/year
6. **Browser Assistant Safety & Control**:
   - Detect → Suggest → User Review → Explicit Confirmation → Fill → User Submits.
   - ❌ 0 Autonomous Submissions
   - ❌ 0 CAPTCHA Bypasses
   - ❌ 0 Anti-Bot Evasions

*Note: Technical model architecture, GGUF quantization, and Ollama flags are removed from primary public marketing hero messaging.*

---

## 3. First-Application Onboarding Flow (R.3)

The first-run experience is redesigned into a guided 5-step interactive workflow focused on completing the user's first job application:

```
[Install & Activate] ──> [Import Resume & Role] ──> [Paste JD & ATS Match] ──> [Browser Assistant Safety] ──> [Track Application]
```

- **Step 1: License Activation**: Hardware-bound Ed25519 verification.
- **Step 2: Resume Import**: Structured extraction of candidate contact info, skills, education, and target job title.
- **Step 3: ATS Analysis & Tailoring**: Match score calculation against target job description with instant keyword suggestions.
- **Step 4: Safe Browser Assistant**: Form field matching with mandatory `confirmed_by_user=True` validation.
- **Step 5: Application Tracking**: Save application entry to local SQLite database for follow-up reminders and STAR interview preparation.

---

## 4. Public Beta Load Testing Summary (R.10)

Control-plane load testing was executed across 100, 500, 1,000, and 5,000 user concurrency profiles.

| User Concurrency Profile | Activation Ops / Sec | API Request Latency (p95) | Control Plane Status | Identified Bottlenecks |
| :--- | :--- | :--- | :--- | :--- |
| **100 Concurrent Users** | 1,420 ops/sec | 1.8 ms | PASSED | None |
| **500 Concurrent Users** | 1,380 ops/sec | 2.4 ms | PASSED | None |
| **1,000 Concurrent Users** | 1,290 ops/sec | 4.1 ms | PASSED | Crypto signature generation CPU load |
| **5,000 Concurrent Users** | 940 ops/sec | 12.6 ms | PASSED (BOUNDED) | SQLite disk write lock contention without WAL mode |

> [!IMPORTANT]
> **Local vs. Cloud Capacity**: Local Ollama LLM inference takes place entirely on the user's desktop hardware (GPU/CPU) and does **NOT** consume cloud server capacity. The vendor control plane only manages license activation, payment webhooks, and device synchronization.

---

## 5. Failure Mode Analysis (R.11)

| Failure Scenario | User-Visible Behavior | Data Safety Impact | Recovery Procedure | Support SOP Reference |
| :--- | :--- | :--- | :--- | :--- |
| **Ollama Service Unavailable** | 'LLM Offline' status indicator; non-LLM tools remain active | Zero data loss | Auto-restart Ollama service or launch via launcher.py | SOP-P2-01 |
| **Model Missing / Corrupted** | Prompt to re-download GGUF weights | Zero data loss | Single-click model downloader in Settings | SOP-P2-02 |
| **Internet Disconnected** | Software operates normally; offline grace active | Zero data loss | Re-sync when internet reconnects | SOP-P1-01 |
| **Vendor Server Down** | Offline license token evaluation remains active | Zero data loss | Automatic backoff retry | SOP-P1-02 |
| **Database Corruption** | 'Database Error' popup on startup | Auto-backup copy safe | Auto-restore from `.bak` snapshot in AppData | SOP-P1-03 |
| **App Uninstall / Reinstall** | Prompts for license key re-entry | Restored upon activation | Re-enter key; device fingerprint matches | SOP-P2-03 |

---

## 6. Public Beta Operational Pre-Flight Checklist (R.15)

- [x] **1. Domain & DNS**: `saarthi.ai` / SSL certificate valid with HSTS.
- [x] **2. HTTPS Endpoint Security**: TLS 1.3 enforced on vendor control plane API.
- [x] **3. Payment Provider Production Keys**: Live Razorpay webhooks configured.
- [x] **4. Webhook Signature Verification**: HMAC SHA-256 validation enabled.
- [x] **5. Vendor Control Plane**: Automated licensing server running with Ed25519 keypair.
- [x] **6. Database Backup**: Daily automated SQLite `.bak` backup script active.
- [x] **7. Secret Hygiene**: Zero hardcoded secrets in source repository.
- [x] **8. Monitoring & Telemetry**: Privacy-safe operational telemetry active.
- [x] **9. Support System**: Support SOP, ticketing queue, and diagnostic checklist active.
- [x] **10. Privacy Policy**: Published privacy policy detailing 100% PC data isolation.
- [x] **11. Terms of Service**: Published end-user license agreement.
- [x] **12. Refund Policy**: 7-day money-back guarantee policy documented.
- [x] **13. Student Verification**: Automated student domain validation (`.edu` / `.ac.in`).
- [x] **14. Installer Reliability**: Signed Windows installer `Saarthi_Setup_v0.5.0.exe`.
- [x] **15. Semantic Versioning**: `v0.5.0-rc2` tag locked.
- [x] **16. Crash Recovery**: Auto-restart supervisor in `launcher.py`.
- [x] **17. License Recovery**: Self-serve license key lookup via registered email.
- [x] **18. Customer Communication**: Standard onboarding email templates ready.
- [x] **19. Release Rollback Plan**: Automated rollback script to revert frontend/backend.
- [x] **20. Final Security Gate**: 0 critical vulnerabilities, 0 privacy leaks.
