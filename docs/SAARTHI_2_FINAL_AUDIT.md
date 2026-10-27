# Saarthi 2.0 Product Audit & System Specification

## 1. Executive Overview & System Architecture

Saarthi 2.0 is a privacy-first, Windows-native, local-AI career operating system powered by an autonomous Jarvis-like agentic assistant. Saarthi executes multi-step complex workflows (job search, resume tailoring, ATS matching, cover letter generation, scheduled follow-ups, interview coaching, and document organization) entirely on the user's local hardware without relying on cloud LLMs or transmitting private career documents to external servers.

```
+-----------------------------------------------------------------------------------+
|                            SAARTHI NATIVE WINDOWS GUI                             |
|    (pywebview Desktop Window / System Tray / Global Hotkeys / Window Controls)   |
|   +---------------------------------------------------------------------------+   |
|   |         React + TypeScript Experiences (SIGNATURE, FORGE, PULSE, AURORA)  |   |
|   +---------------------------------------------------------------------------+   |
+------------------------------------------+----------------------------------------+
                                           | HTTP / REST API (Loopback 127.0.0.1)
                                           v
+-----------------------------------------------------------------------------------+
|                             SAARTHI FASTAPI BACKEND                               |
|                                                                                   |
|  +---------------------------+  +--------------------------+  +----------------+  |
|  | Server-Authoritative      |  | Hardware-Aware           |  | Production     |  |
|  | Entitlements & Licensing  |  | Nemotron Selector        |  | Payment Engine |  |
|  | (FREE, STUDENT, PERSONAL, |  | (STANDARD, PRO, SUPER,   |  | (Razorpay &    |  |
|  |  POWER Tiers)             |  |  ULTRA Tiers)            |  |  Stripe Sandbox|  |
|  +---------------------------+  +--------------------------+  +----------------+  |
|                                                                                   |
|  +---------------------------+  +--------------------------+  +----------------+  |
|  | Auth & Account System     |  | Daily Usage Quota        |  | Admin & Audit  |  |
|  | (PBKDF2, Sessions, Auth,  |  | (24h Cooldown, Token     |  | System         |  |
|  |  Device Fingerprint)      |  |  Accounting)             |  | (Separate Auth)|  |
|  +---------------------------+  +--------------------------+  +----------------+  |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                        AGENTIC ORCHESTRATION ENGINE                         |  |
|  |                                                                             |  |
|  |  [Task Orchestrator] <---> [Task Planner] <---> [Task Executor / State]   |  |
|  |          |                      |                       |                   |  |
|  |          v                      v                       v                   |  |
|  |  [Permission Manager]   [Memory Manager]        [Task Scheduler]            |  |
|  |  (Human-in-the-Loop)   (Local Vector/SQLite)   (Background Tasks)          |  |
|  |                                                                             |  |
|  |  +-----------------------------------------------------------------------+  |  |
|  |  | Tool Registry: Browser, Document (PDF/DOCX/OCR), Terminal, Windows,  |  |  |
|  |  |                Search, Resume ATS, Interview Coach, Memory, Mail      |  |  |
|  |  +-----------------------------------------------------------------------+  |  |
|  +-----------------------------------------------------------------------------+  |
+------------------------------------------+----------------------------------------+
                                           | HTTP IPC (Loopback 127.0.0.1:11434)
                                           v
+-----------------------------------------------------------------------------------+
|                        LOCAL OLLAMA INFERENCE DAEMON                              |
|           NVIDIA Nemotron Models: nemotron:3b | nemotron-mini:4b |                    |
|                   nemotron-3-nano:4b | nemotron-3-8b                                |
+-----------------------------------------------------------------------------------+
```

---

## 2. Database Schema & Data Models

Database Engine: **SQLite** (`%LOCALAPPDATA%\Saarthi\saarthi.db`)
Key Tables:
- `users`: User identity, PBKDF2 password hashes, verification tokens, reset tokens, subscription plan.
- `sessions`: Session tokens, user_id, device_id, expiration timestamps.
- `devices`: Registered device hardware fingerprints, OS info, binding status.
- `free_usage_quota`: Request accounting, daily allowance (30 requests), 24-hour cooldown timestamps.
- `payment_orders`: Provider order ID, Razorpay/Stripe metadata, amount, currency, status (`CREATED`, `PAID`, `REFUNDED`, `CANCELLED`).
- `webhook_events`: Webhook event IDs for idempotency and duplicate prevention.
- `agent_tasks`: Task IDs, user_id, title, prompt, DAG step JSON, status (`QUEUED`, `PLANNING`, `RUNNING`, `WAITING_APPROVAL`, `COMPLETED`, `FAILED`, `CANCELLED`).
- `task_approvals`: Human confirmation approval requests, action titles, details, status (`PENDING`, `APPROVED`, `REJECTED`).
- `scheduled_jobs`: Recurring ("Every Monday find jobs") & scheduled automation jobs.
- `admin_audit_log`: Audit trail for all administrator actions (suspend, restore, delete, refund).
- `memories`: Local career facts, skills, goals, preferences.

---

## 3. Account, Authentication & Entitlements

- **Password Security**: PBKDF2 HMAC SHA-256 (100,000 iterations + 16-byte random salt).
- **Brute-force Guard**: Login attempt tracking in `login_attempts` table (5 failed attempts -> 15-minute lock).
- **Clean State Guarantee**: Fresh state displays "Welcome to Saarthi Candidate Profile" without hardcoded developer data.
- **Authoritative Plans & Pricing**:
  - `FREE`: ₹0 / $0 — 30 requests/day, 24-hour cooldown, watermarked exports.
  - `STUDENT`: ₹99 / $1.50 — Clean exports, ATS tools, cover letters.
  - `PERSONAL`: ₹399 / $5.00 — Browser & file automation, research workflows.
  - `POWER`: ₹799 / $10.00 — Autonomous agent orchestration, parallel agents, maximum Nemotron model access.

---

## 4. Payment Gateway Subsystem

- **Providers**: Razorpay (India, INR) & Stripe (International, USD).
- **Development Mode**: `SANDBOX VERIFIED`.
- **Security**: HMAC SHA-256 signature verification (`x-razorpay-signature` and `stripe-signature`), webhook idempotency logging, automatic entitlement activation upon valid signature. Zero client-side paid status trust.

---

## 5. Hardware-Aware Nemotron Intelligence

- **Model Tiers**:
  - `STANDARD`: `nemotron:3b` (6GB RAM min)
  - `PRO`: `nemotron-mini:4b` (8GB RAM min)
  - `SUPER`: `nemotron-3-nano:4b` (8GB RAM min, 4GB VRAM rec)
  - `ULTRA`: `nemotron-3-8b` (16GB RAM min, 6GB+ VRAM)
- **Dual Qualification Rule**: Access to `ULTRA` model tier strictly requires **BOTH** a `POWER` subscription **AND** `ULTRA`-qualified hardware.
- **Physical Verification**: Unverified hardware is flagged as `NOT PHYSICALLY VERIFIED`.

---

## 6. Transactional Email Subsystem

- **Configuration**: Environment variables (`EMAIL_PROVIDER`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `ADMIN_EMAIL`).
- **Unconfigured State**: When unconfigured, returns explicit status `"EMAIL SERVICE NOT CONFIGURED"` without simulating false delivery.

---

## 7. Windows Native Packaging & Data Isolation

- **Packaging**: PyInstaller standalone executable with `pywebview` windowing.
- **Installer**: Inno Setup (`saarthi_setup.iss`) supporting user-selectable install directory (default `%LOCALAPPDATA%\Programs\Saarthi`).
- **Data Isolation**: Application binaries in installation path; user data & logs isolated in `%LOCALAPPDATA%\Saarthi`. User data preserved across uninstalls.

---

## 8. Agentic Jarvis Engine & Automation Tools

- **Orchestration**: DAG Task Planner & State Machine (`QUEUED`, `PLANNING`, `RUNNING`, `WAITING_APPROVAL`, `PAUSED`, `RETRYING`, `COMPLETED`, `FAILED`, `CANCELLED`).
- **Tool Suite**: Browser Automation, PDF/DOCX Parser, pytesseract OCR, Terminal & Windows Automation, Memory Manager, Task Scheduler.
- **Human Confirmation Cards**: Consequential operations (sending email, job submission, file deletion, financial transactions) require explicit inline user approval.

---

## 9. Security & Privacy Audit Findings

- **Secrets Isolation**: No secret keys, database credentials, or private keys present in frontend assets (`frontend/src` or `frontend/dist`).
- **Loopback Binding**: Local backend services bind exclusively to loopback interface `127.0.0.1`.
- **SQL Parameterization**: All SQL queries use prepared parameterized queries.
- **Privacy Boundary**: Zero telemetry transmission of user resume contents, prompts, cover letters, or conversation histories.

---

## 10. Automated Test Results & Verification Matrix

- **Backend Pytest Suite**: `27 / 27` passed (`test_saarthi_2_foundation.py`, `test_saarthi_2_advanced.py`, `test_api_contract.py`, `test_payment_reliability.py`, `test_hardware_detection.py`, `test_career.py`, `test_browser_assistant.py`).
- **Frontend Production Build**: `npm run build` passed cleanly (`1623 modules transformed`, `dist/assets/index-BVTChdyd.js`).
- **Verification Status Labels**:
  - Auth, Entitlement & Quota: `CODE VERIFIED` & `TEST VERIFIED`
  - Razorpay & Stripe Gateways: `SANDBOX VERIFIED`
  - Email Service: `NOT CONFIGURED` (Graceful fallback)
  - Physical GPU Hardware Matrix: `NOT PHYSICALLY VERIFIED` (Tested on host workstation)
  - Agent DAG Orchestration: `CODE VERIFIED` & `TEST VERIFIED`
