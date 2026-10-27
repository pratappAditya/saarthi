# Saarthi 2.0 Product Architecture & Vision

## 1. Executive Summary & Vision

Saarthi is evolving from a trusted-beta desktop AI prototype into a privacy-first, Windows-native, local-AI career operating system powered by an autonomous Jarvis-like agentic assistant. Saarthi executes multi-step complex workflows (e.g., job search & ranking, resume tailoring, cover letter generation, scheduled follow-ups, interview coaching, document organization) entirely on the user's local hardware without relying on cloud LLMs or compromising user data privacy.

---

## 2. Core Architecture & Subsystem Blueprint

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
|  | (bcrypt, Sessions, Auth,  |  | (24h Cooldown, Token     |  | System         |  |
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

## 3. Subsystem Specifications

### 3.1 Account & Identity Management
- **Authentication**: JWT-based session tokens with HTTP-only security or Authorization headers, password hashing using `bcrypt`.
- **Identity Scope**: User ID, email verification status, device registrations, session management with remote revocation.
- **Privacy & Clean State Guarantee**: Fresh installations strictly display "Welcome to Saarthi Candidate Profile" without hardcoded developer data. Profile metadata populates only upon user sign-up, sign-in, or explicit candidate profile import.

### 3.2 Authoritative Subscription & Entitlement Engine
- **Paid Plans**:
  1. `FREE` (₹0 / $0): Basic assistant, daily usage quota, 24-hour cooldown upon exhaustion, watermarked exports, standard Nemotron models.
  2. `STUDENT` (₹99 / $1.50): ATS resume tools, cover letter generation, career planning, clean exports, expanded memory history, standard/pro models.
  3. `PERSONAL` (₹399 / $5.00): High AI allowance, advanced resume & browser workflows, research automation, multi-step agent tasks, persistent memory, SUPER models.
  4. `POWER` (₹799 / $10.00): Highest AI allowance, autonomous agent orchestration, parallel agents, long-running background tasks, maximum hardware-qualified Nemotron access (including ULTRA when hardware permits).
- **Entitlement Rule**: Entitlement is strictly verified server-side. Frontend state or `localStorage` modifications cannot override entitlements.

### 3.3 Hardware-Aware Nemotron Intelligence System
- **Hardware Capability Detection**: Startup & background diagnostic scans for Windows version, CPU cores, RAM, GPU, Dedicated VRAM, Shared VRAM, storage, CUDA capabilities, NVIDIA drivers, and Ollama status.
- **Inference Benchmarking**: Measures real tokens-per-second (TPS) and VRAM pressure rather than relying solely on static specifications.
- **Hardware Capability Tiers**:
  - `STANDARD`: `nemotron:3b`
  - `PRO`: `nemotron-mini:4b`
  - `SUPER`: `nemotron-3-nano:4b`
  - `ULTRA`: `nemotron-3-8b`
- **Dual Qualification Formula**:
  `Access to Model Tier = (Subscription Plan Permission) AND (Verified Hardware Capability Qualification)`
  - *Example*: Power Subscription + GTX 1650 Ti (4GB VRAM) qualifies for SUPER tier only; Power Subscription + RTX GPU (16GB VRAM) unlocks ULTRA tier.

### 3.4 Production Payment System (Razorpay & Stripe)
- **Architecture**:
  `User -> Saarthi Desktop Client -> Provider Checkout (Razorpay/Stripe) -> Payment -> Webhook -> Backend HMAC Verification -> Entitlement & License Sync -> Client Update`
- **Security**: Webhook signature verification, replay protection (idempotency tokens), refund/cancellation lifecycle handling, zero secrets in frontend assets.

### 3.5 Agentic Jarvis Orchestration Architecture
- **Orchestration**: Task Planner breaks down high-level user directives ("Find jobs, tailor resume, apply, schedule follow-up") into DAG-based task steps.
- **State Machine**: `QUEUED` -> `PLANNING` -> `RUNNING` -> `WAITING_APPROVAL` -> `PAUSED` -> `COMPLETED` / `FAILED` / `CANCELLED`.
- **Human Safety & Confirmation Guard**:
  - *Autonomous Operations*: Document analysis, research, local drafting, local file organization.
  - *Confirmation Required*: Sending emails, submitting job applications, deleting files, financial transactions, modifying system settings.
- **Tools**: Browser automation (Selenium/Playwright/httpx), Document Engine (pypdf, python-docx, pytesseract OCR), Terminal & Windows automation, Resume/ATS scoring, Memory Manager, Scheduler.

### 3.6 Windows Application Packaging & Lifecycle
- **Packaging**: PyInstaller standalone executable with `pywebview` windowing.
- **Installer**: Inno Setup installer supporting custom user install paths (e.g., `%LOCALAPPDATA%\Programs\Saarthi` or `D:\Games\Saarthi`).
- **Data Isolation**: Application binaries stored in install location; user database & logs isolated in `%LOCALAPPDATA%\Saarthi`. Uninstalling application binaries preserves user data unless explicitly opted out by user.

### 3.7 Admin & Telemetry System
- **Admin Portal**: Separate admin authentication (API keys/admin roles).
- **Visibility**: User list, order/payment status, license status, anonymized hardware & beta error diagnostics.
- **Privacy Boundary**: Zero collection or telemetry transmission of user resume content, prompts, cover letters, private documents, or chat transcript histories.

---

## 4. Architectural Non-Negotiables & Guarantees
1. No cloud LLM fallback; AI remains 100% local via Ollama + Nemotron.
2. Server-authoritative security for identity, licensing, entitlements, and admin actions.
3. Strict hardware validation; no spoofed or invented GPU/VRAM capability.
4. Absolute preservation of the 4 experience modes (SIGNATURE, FORGE, PULSE, AURORA) with layout/interaction parity.
