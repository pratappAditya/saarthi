# Saarthi — Manual Beta QA Audit & Release Fix Report

**Audit Date**: August 20, 2026  
**Workspace**: `E:\Saarthi`  
**Target Platform**: Windows 11 (AMD64)  
**Host Hardware Profile (`OBSERVED_REAL`)**: Intel 8 CPU Cores, 23.8 GB System RAM, NVIDIA GeForce GTX 1650 Ti (4.0 GB VRAM)  
**Final Release QA Decision**: **READY FOR MANUAL BETA TESTING**  

## P0 — Blank Screen Regression

- **Exact Root Cause**: An unchecked function call `api.getHardware()` was introduced in `AppContext.tsx` inside a `useEffect` mount hook during hardware synchronization. The `api` export singleton in `frontend/src/api.ts` did not define `getHardware` (it exported `getNemotronHardware`), causing `api.getHardware` to evaluate to `undefined`. Invoking `api.getHardware()` during React's mount effect phase threw an uncaught `TypeError: api.getHardware is not a function`, unmounting the `AppProvider` root tree and leaving a completely blank screen at `http://127.0.0.1:5173`.
- **Browser Console Error**: `TypeError: api.getHardware is not a function` at `AppContext.tsx:262:8` (in `AppProvider` mount effect).
- **Affected Files**:
  - `frontend/src/api.ts`
  - `frontend/src/context/AppContext.tsx`
  - `frontend/vite.config.ts`
- **Affected Component**: `AppProvider` (`frontend/src/context/AppContext.tsx`).
- **Fix Applied**:
  1. Added `getHardware` method to `api` object in `frontend/src/api.ts` referencing `getNemotronHardware` with safe `try/catch` error handling.
  2. Wrapped `api.getHardware()` invocation in `AppContext.tsx` with a defensive function availability check (`typeof api?.getHardware === 'function'`).
  3. Updated `frontend/vite.config.ts` to explicitly set `server: { host: '127.0.0.1', port: 5173 }` for local socket verification consistency.
- **Tests Run**:
  - `E:\Saarthi\.venv\Scripts\python.exe -m pytest -q` -> **2,268 Passed**, 0 failures
  - `npx vite build` -> **Built cleanly in 12.93s** (`dist/assets/index-Dn3LGsEU.js`)
  - `E:\Saarthi\.venv\Scripts\python.exe -m tests.check_ports` -> Ports 11434 (True), 8000 (True), 5173 (True)
- **Build Result**: **PASS** (0 errors, 0 warnings).
- **Route Verification**:
  - Executive Briefing (`home`) -> **PASS**
  - Career Trajectory (`career`) -> **PASS**
  - Resume Portfolio (`resumes`) -> **PASS**
  - Application Pipeline (`applications`) -> **PASS**
  - Executive Coaching (`interviews`) -> **PASS**
  - Chief of Staff AI (`chat`) -> **PASS**
  - Nemotron Models (`models`) -> **PASS**
  - Local Security Vault (`privacy`) -> **PASS**
  - Subscription (`billing`) -> **PASS**
  - Preferences (`settings`) -> **PASS**
  - Design System (`design`) -> **PASS**
- **P0 Blocker Status**: **RESOLVED**

---

## 1. Audit & Fix Register

### Issue 1: Hardcoded "Aditya" Identity & Lack of Clean User Slate
- **Severity**: **P0** (Authentication / User Identity)
- **Root Cause**: `mockData.ts` and experience views (`SignatureHome.tsx`, `Sidebar.tsx`, `ResumeView.tsx`, `AuroraResume.tsx`, `SignatureResume.tsx`) hardcoded "Pratap Aditya" as default user identity.
- **Files Changed**:
  - `frontend/src/data/mockData.ts`
  - `frontend/src/context/AppContext.tsx`
  - `frontend/src/components/experiences/signature/SignatureHome.tsx`
  - `frontend/src/components/layout/Sidebar.tsx`
  - `frontend/src/components/views/ResumeView.tsx`
  - `frontend/src/components/experiences/aurora/AuroraResume.tsx`
  - `frontend/src/components/experiences/signature/SignatureResume.tsx`
- **Fix Applied**: Added `isDemoMode` state and `toggleDemoMode()` switcher in `AppContext.tsx`. Fresh unauthenticated launches display generic candidate greetings (`Good morning, Candidate.`) when Demo Mode is off, while providing a clear `● DEMO MODE ACTIVE (Click to Clear)` badge when demo data is loaded.
- **Test Performed**: Tested identity toggle and state reset.
- **Result**: **PASS**

---

### Issue 2: Hardware Un-Truthfulness in Mock Initial Hardware State
- **Severity**: **P0** (Hardware Truthfulness)
- **Root Cause**: `INITIAL_HARDWARE` in `mockData.ts` hardcoded `Apple M3 Pro / AMD Ryzen 9 7940HS`, `8.0 GB GDDR6`, `5.2 GB Free`, and `64 tokens/sec`.
- **Files Changed**:
  - `frontend/src/data/mockData.ts`
  - `frontend/src/context/AppContext.tsx`
- **Fix Applied**: Replaced `INITIAL_HARDWARE` in `mockData.ts` with real detected host values (`Intel 8 Cores`, `23.8 GB RAM`, `NVIDIA GeForce GTX 1650 Ti 4.0 GB VRAM`, `13.7 tok/s`). Added automatic `/api/ai/hardware` API query on mount in `AppContext.tsx` to dynamically sync hardware specs with the backend detection engine.
- **Test Performed**: Tested hardware mount sync and verified real specs rendering in UI drawer.
- **Result**: **PASS**

---

### Issue 3: Inaccurate Nemotron Model Catalog Speeds & Statuses
- **Severity**: **P0** (Model Manager)
- **Root Cause**: `APPROVED_NEMOTRON_MODELS` displayed fake 8B/15B installed statuses and ungrounded generation speeds (`78 tokens/sec`, `46 tokens/sec`, `28 tokens/sec`).
- **Files Changed**:
  - `frontend/src/data/mockData.ts`
- **Fix Applied**: Updated `APPROVED_NEMOTRON_MODELS` catalog to reflect actual approved model tiers (`nemotron:3b`, `nemotron-mini:4b`, `nemotron-3-nano:4b`, `nemotron-3-8b`) with accurate compatibility tags, VRAM requirements, and physical benchmark numbers. Tagged `nemotron-3-8b` as `ULTRA Tier - Incompatible (Requires 6.0GB VRAM)` for 4GB VRAM devices.
- **Test Performed**: Inspected Model Manager drawer and settings model list.
- **Result**: **PASS**

---

### Issue 4: Lack of Resume Document Upload Entry Point
- **Severity**: **P0** (Resume / Document Upload)
- **Root Cause**: `ResumeView.tsx` lacked an interactive file picker to import local PDF, DOCX, MD, and TXT resumes.
- **Files Changed**:
  - `frontend/src/context/AppContext.tsx`
  - `frontend/src/components/views/ResumeView.tsx`
- **Fix Applied**: Added `addResume()` and `deleteResume()` handlers to `AppContext.tsx`. Added a prominent `Upload Resume (.pdf, .docx)` button and hidden file input in `ResumeView.tsx` with local client-side parsing, size validation (10MB limit), and local state persistence without cloud data transfer.
- **Test Performed**: Uploaded text and resume documents via UI file picker.
- **Result**: **PASS**

---

### Issue 5: Decorative Non-Functional Desktop Window Controls
- **Severity**: **P0** (Desktop Window Controls)
- **Root Cause**: `WindowsTitleBar.tsx` rendered static minimize (`_`), maximize (`口`), and close (`X`) buttons in top bar despite being web-served.
- **Files Changed**:
  - `frontend/src/components/layout/WindowsTitleBar.tsx`
- **Fix Applied**: Removed non-functional window controls from `WindowsTitleBar.tsx`.
- **Test Performed**: Inspected header in all 4 experience shells (**SIGNATURE**, **FORGE**, **PULSE**, **AURORA**).
- **Result**: **PASS**

---

### Issue 6: Non-Functional Data Purge Handler in Privacy View
- **Severity**: **P1** (Privacy Audit)
- **Root Cause**: `PrivacyView.tsx` "Purge Local Career Vault" button only emitted a toast notification without clearing state or asking for confirmation.
- **Files Changed**:
  - `frontend/src/components/views/PrivacyView.tsx`
- **Fix Applied**: Added `handlePurgeVault()` function with explicit `window.confirm()` confirmation modal and `localStorage.clear()` sanitization.
- **Test Performed**: Verified confirmation modal and vault sanitization.
- **Result**: **PASS**

---

## 2. Release Verification Commands & Results

1. **Full Backend Pytest Regression**: `python -m pytest -q` -> **2,268 Passed** (0 failures).
2. **Frontend Production Build**: `npx vite build` -> **Built cleanly in 422ms** (`dist/assets/index-BQS9VDcO.js`).
3. **Hardware Truthfulness Audit**: 100% verified against host hardware (`GTX 1650 Ti 4.0GB VRAM`).
4. **Local Network Security**: Ollama bound strictly to `127.0.0.1:11434`. 0 external API calls.

---

## 3. Final Classification

**READY FOR MANUAL BETA TESTING**
