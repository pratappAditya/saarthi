# Saarthi 2.0 Phased Implementation Plan

## Overview
This document outlines the step-by-step master plan for advancing the Saarthi platform from its current prototype stage to the production-ready Saarthi 2.0 local-AI career operating system.

---

## Phase Breakdown & Detailed Work Streams

### Phase 0: Repository Inspection & Master Architecture Design (COMPLETED)
- **Goal**: Audit existing codebase, identify reusable components, establish architecture and migration strategy without breaking current working functionality.
- **Key Deliverables**:
  - `docs/SAARTHI_2_ARCHITECTURE.md`
  - `docs/SAARTHI_2_IMPLEMENTATION_PLAN.md`

---

### Phase 1: Foundation Hardening & Auth Audit
- **Goal**: Audit & harden server-authoritative account, entitlement, quota, hardware detection, and admin authentication systems.
- **Work Items**:
  1. Rate limiting & brute-force protection in `app/api/auth.py`.
  2. Token-based password reset architecture & email verification status hooks.
  3. Session expiry enforcement & device revocation.
  4. Identity audit: Ensure clean profile state contains zero hardcoded developer placeholders.

---

### Phase 2: Real Payment & Subscription Lifecycle Subsystem
- **Goal**: Complete Razorpay & Stripe payment gateway sandbox integration, subscription lifecycle, and entitlement activation.
- **Work Items**:
  1. Payment provider abstraction supporting Razorpay (India, INR) and Stripe (International, USD).
  2. Subscription status tracking: `CREATED`, `AUTHORIZED`, `PAID`, `FAILED`, `PENDING`, `REFUNDED`, `CANCELLED`, `EXPIRED`, `GRACE_PERIOD`.
  3. Subscription history, payment history, refund, and cancellation endpoints in `app/api/payment.py`.
  4. Comprehensive sandbox test suite in `backend/tests/test_payment_sandboxes.py`.

---

### Phase 3: Transactional Email Subsystem
- **Goal**: Implement transactional email service abstraction with environment configuration.
- **Work Items**:
  1. Email service in `app/services/email.py`.
  2. Environment variables: `EMAIL_PROVIDER`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USERNAME`, `EMAIL_PASSWORD`, `ADMIN_EMAIL`.
  3. Explicit `"EMAIL SERVICE NOT CONFIGURED"` status when unconfigured (no simulated delivery).

---

### Phase 4: Admin Panel Completion & Audit Trail
- **Goal**: Finish isolated admin panel with audit logging.
- **Work Items**:
  1. Admin authentication separate from user authentication.
  2. Endpoints for user management, subscription tracking, payment details, license management, and beta diagnostics.
  3. Audit log recording for all admin actions in `admin_audit_log`.

---

### Phase 5: Windows Native Application Lifecycle
- **Goal**: Complete native Windows application packaging and installer infrastructure.
- **Work Items**:
  1. Audit PyInstaller setup (`Saarthi.spec`) & pywebview launcher (`SaarthiDesktop.py`).
  2. Custom installation path selection (default `%LOCALAPPDATA%\Programs\Saarthi`).
  3. Isolated user data directory (`%LOCALAPPDATA%\Saarthi`).
  4. System tray, global hotkeys, startup with Windows toggle, crash logging.

---

### Phase 6: Hardware Engine & Ollama Lifecycle
- **Goal**: Real hardware detection, inference benchmarking, and model lifecycle management.
- **Work Items**:
  1. Detect CPU, RAM, GPU, VRAM, storage, NVIDIA drivers, CUDA, and Ollama.
  2. Benchmark actual local inference speed (TPS).
  3. Model lifecycle (install, verify, benchmark, switch, rollback) for `nemotron:3b`, `nemotron-mini:4b`, `nemotron-3-nano:4b`, `nemotron-3-8b`.
  4. Mark unverified physical hardware as `NOT PHYSICALLY VERIFIED`.

---

### Phase 7: Agentic Jarvis Orchestration Architecture
- **Goal**: Expand agent loop into a DAG task orchestrator.
- **Work Items**:
  1. Implement `AgentOrchestrator`, `TaskPlanner`, `TaskExecutor`, `TaskStateManager`, `Scheduler`.
  2. Support task states: `QUEUED`, `PLANNING`, `RUNNING`, `WAITING_APPROVAL`, `PAUSED`, `RETRYING`, `COMPLETED`, `FAILED`, `CANCELLED`.
  3. Persist task DAG and step execution history.

---

### Phase 8: Comprehensive Agent Tool Suite
- **Goal**: Expand agent tool registry.
- **Work Items**:
  1. Tool schemas and validation for Browser, Search, Files, PDF, DOCX, OCR, Resume ATS, Interview Coach, Terminal, Windows, Clipboard, Screenshot, Calendar, Email, Notifications, Scheduler, Memory, Nemotron.
  2. Permission requirements and error handling per tool.

---

### Phase 9: Human Confirmation & Approval Engine
- **Goal**: Implement confirmation approval cards for consequential operations.
- **Work Items**:
  1. Differentiate safe operations (analysis, research, local drafting) from consequential operations (sending email, job submission, file deletion, financial actions).
  2. Structured approval card UI payload showing exact action details.

---

### Phase 10: Persistent Local Memory Management
- **Goal**: Local-first career memory management.
- **Work Items**:
  1. View, edit, delete, export, and clear all user career memories locally.
  2. Zero telemetry or server uploading of private memory content.

---

### Phase 11: Automation & Scheduled Workflows
- **Goal**: Background automation and recurring task scheduler.
- **Work Items**:
  1. Support one-time, recurring ("Every Monday find jobs"), and scheduled tasks.
  2. Application restart recovery for scheduled tasks.

---

### Phase 12: Document Engine & Watermark Control
- **Goal**: Document parsing, OCR, and export generation.
- **Work Items**:
  1. Import PDF, DOCX, DOC, TXT, MD, Images (OCR).
  2. Watermarked exports for `FREE` plan, clean exports for verified paid plans.

---

### Phase 13: Four Experience Systems Alignment
- **Goal**: Ensure layout and feature parity across all 4 experience systems.
- **Work Items**:
  1. Feature parity across `SIGNATURE`, `FORGE`, `PULSE`, `AURORA`.
  2. Functional controls without decorative fake buttons.

---

### Phase 14: Professional Billing UX
- **Goal**: Integrated billing and entitlement interface.
- **Work Items**:
  1. Current plan display, daily quota status, 24h cooldown timer, renewal dates, payment history, upgrade/downgrade modals.
  2. Clear hardware capability status for `POWER` users on non-ULTRA hardware.

---

### Phase 15: Security Audit
- **Goal**: Complete security audit across API, payments, auth, and sandboxing.
- **Work Items**:
  1. Audit authentication, authorization, payment webhooks, license signing, device binding, file paths, command execution, SQL parameters, rate limits, CORS.

---

### Phase 16: Comprehensive Real-World Testing
- **Goal**: Automated and physical verification test matrix.
- **Work Items**:
  1. Unit, integration, API, security, entitlement, payment sandbox, agent, and document test suites.
  2. Physical hardware verification matrix (`STANDARD`, `PRO`, `SUPER`, `ULTRA`).

---

### Phase 17: Windows Release Candidate Build
- **Goal**: Package release candidate installer and distribution artifacts.
- **Work Items**:
  1. Windows installer build (`Saarthi-x.x.x-Setup.exe`), SHA256 checksums, release notes, documentation.

---

### Phase 18: Final Audit & Release Verification
- **Goal**: Final audit and release readiness checklist.
- **Work Items**:
  1. Generate `docs/SAARTHI_2_FINAL_AUDIT.md` and `SAARTHI_2_RELEASE_CHECKLIST.md`.
