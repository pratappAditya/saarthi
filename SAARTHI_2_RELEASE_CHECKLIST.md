# Saarthi 2.0 Pre-Release Verification Checklist

## 1. Architecture & Security Controls
- [x] Server-authoritative entitlement engine (Frontend localStorage cannot grant paid features).
- [x] Zero cloud LLM fallback; AI inference remains 100% local via Ollama + NVIDIA Nemotron.
- [x] PBKDF2 password hashing & rate-limited authentication.
- [x] Clean candidate profile on fresh install (No hardcoded developer names).
- [x] Local service loopback binding (`127.0.0.1`).
- [x] Secrets isolation (Zero payment keys/DB credentials in frontend bundle).

## 2. Subscription & Payment Gateways
- [x] Paid plans configured: FREE (₹0), STUDENT (₹99), PERSONAL (₹399), POWER (₹799).
- [x] FREE usage quota: 30 requests/day with 24-hour cooldown enforcement.
- [x] Razorpay & Stripe sandbox integration with HMAC signature verification.
- [x] Webhook idempotency logging & duplicate event handling.
- [x] Automatic user entitlement activation upon valid payment verification.

## 3. Hardware & Nemotron System
- [x] Startup hardware detection (CPU, RAM, GPU, VRAM, storage, CUDA).
- [x] Local inference benchmarking (TPS).
- [x] Dual qualification rule: `ULTRA` tier requires BOTH `POWER` subscription AND `ULTRA` hardware.
- [x] Automated Ollama installation wizard & model downloader with rollback.

## 4. Agentic Jarvis Engine & Tools
- [x] Task Orchestrator DAG planner (`QUEUED`, `PLANNING`, `RUNNING`, `WAITING_APPROVAL`, `COMPLETED`, `FAILED`, `CANCELLED`).
- [x] Human confirmation approval cards for consequential operations (email, job applying, file deletion).
- [x] Automation Scheduler daemon for recurring/scheduled tasks.
- [x] Document Engine for PDF, DOCX, OCR, watermarked FREE exports, and clean paid exports.
- [x] Local persistent memory control (view, edit, delete, export, clear all).

## 5. UI Experience Systems Alignment
- [x] 4 distinct experience systems: SIGNATURE, FORGE, PULSE, AURORA.
- [x] Complete feature parity across all 4 layouts.
- [x] Integrated Billing UX, quota indicators, and hardware status cards.

## 6. Windows Application Packaging
- [x] Standalone PyInstaller build configuration (`Saarthi.spec`).
- [x] User-selectable installation path (Inno Setup `saarthi_setup.iss`).
- [x] Isolated user data directory (`%LOCALAPPDATA%\Saarthi`) preserved across uninstalls.
- [x] Desktop tray icon, global hotkeys, crash logging (`logs/desktop.log`).

## 7. Verification Status Summary
- **Backend Test Suite**: 27 / 27 Passed (`.venv\Scripts\python.exe -m pytest`)
- **Frontend Bundle Build**: Passed (`npm run build`, `dist/assets/index-BVTChdyd.js`)
- **Razorpay / Stripe Payments**: `SANDBOX VERIFIED`
- **Email Subsystem**: `NOT CONFIGURED` (Graceful fallback)
- **Physical GPU Matrix**: `NOT PHYSICALLY VERIFIED` (Host workstation tested)
