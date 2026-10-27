# Saarthi Manual Runtime QA Log & Defect Resolution Report

**Session Date**: 2026-08-26  
**Environment**: Windows 11 (AMD64), Local Python 3.14.6, pywebview native container  
**Host Binding**: `127.0.0.1:8000` (FastAPI) | `127.0.0.1:11434` (Ollama)  
**Database**: `C:\Users\prata\AppData\Local\Saarthi\saarthi.db`  

---

## 1. Verified Runtime Subsystem Status

| Subsystem | Status | Observed Empirical Baseline Data |
| :--- | :---: | :--- |
| **1. Frontend** | **PASS** | HTTP 200 at `http://127.0.0.1:8000/`. Compiled React + Vite production bundle served via FastAPI static mounts. |
| **2. Backend** | **PASS** | FastAPI background process running on `http://127.0.0.1:8000/api/health` returning `{"status": "ok", "service": "saarthi"}`. |
| **3. Ollama Daemon** | **PASS** | `ollama serve` active on `http://127.0.0.1:11434`. Endpoint `/api/tags` responding with `HTTP 200 OK`. |
| **4. Active Nemotron Model** | **PASS** | `nemotron-3-nano:4b` (GGUF Q4_K_M, 4.0B parameters, context 262,144 tokens) verified installed and loaded. |
| **5. Hardware Probing** | **PASS** | Verified CPU: Intel64 Family 6 Model 165 (8 cores), RAM: 23.8 GB (9.4 GB free), GPU: NVIDIA GeForce GTX 1650 Ti (4.0 GB VRAM), Free Storage: 229.4 GB SSD. |
| **6. Database & Local Vault** | **PASS** | SQLite database file active at `%LOCALAPPDATA%\Saarthi\saarthi.db`. Schema migrated with columns: `filename`, `file_type`, `file_path`, `target_role`, `summary`, `skills`, `parsed_facts`, `sections`, `versions`, `active_version_id`. |
| **7. Windows Desktop Container** | **PASS** | `pywebview` window initialized (`Saarthi — AI Career Companion (v1.0.0-beta.1)`), min size 900x600, active resolution 1280x820. |

---

## 2. P0/P1 Defect Investigation & Resolution Report

### Defect Record #01 — Resume Disappeared On Refresh & Corrupted PDF Artifacts
- **Severity**: P0/P1 (Blocker / Critical Data Loss)
- **Exact Screen**: Resume Portfolio (Signature, Forge, Pulse, Aurora views)
- **Exact Action**: Upload/import PDF resume → Refresh browser / restart desktop app.
- **Reported Symptom**:
  1. Imported resume disappeared on reload, reverting to empty/untitled state.
  2. PDF rendering displayed binary garbage such as `" @ Imported Record"`, `"/Title (Resume)"`, `"%PDF-1.7"`, `"endobj"`.
- **Root Cause Analysis**:
  1. **Frontend Hydration Defect**: `AppContext.tsx` initialized `resumes` state with `INITIAL_RESUMES` (from `mockData.ts`) and lacked startup API hydration logic. On mount, `api.listResumes()` was never invoked, causing React state to reset to static mock data upon page refresh.
  2. **Corrupted PDF Parsing Defect**: `useDocumentImport.ts` invoked `FileReader.readAsText(file)` on binary PDF streams. Raw binary PDF syntax reached the frontend state and backend import route without proper PDF text extraction.
  3. **Clean State Impurity**: Default state loaded hardcoded developer names and sample candidate data instead of showing a genuine empty state when no resume was uploaded.

### Summary of Fixes Implemented:
1. **Multipart Local Vault Upload (`POST /api/career/resume/upload`)**:
   - Updated `useDocumentImport.ts` to send binary files directly to the backend via `FormData` multipart upload (`api.uploadResumeFile`).
   - Saved original document files to `%LOCALAPPDATA%\Saarthi\vault\resumes\<timestamp>_<filename>`.
2. **Robust PDF Text Extraction & Sanitization (`DocumentEngine.clean_extracted_text`)**:
   - Added regex sanitization stripping `%PDF-`, `/Title`, `\d+ \d+ obj`, `<<.*?>>`, `endobj`, and control characters `[\x00-\x1F]`.
3. **SQLite Schema & Repository Migration (`backend/app/db/career.py`)**:
   - Extended `resumes` table schema with `filename`, `file_type`, `file_path`, `target_role`, `summary`, `skills`, `sections`, `versions`, `active_version_id`.
   - Added full CRUD (`get_resume`, `list_resumes`, `update_resume`, `delete_resume`, `add_resume_version`).
4. **Startup Resume Hydration (`AppContext.tsx`)**:
   - Added `fetchResumes()` to startup `useEffect` in `AppContext.tsx` querying `/api/career/resumes`.
   - Synchronized `addResume`, `deleteResume`, and version creation directly with SQLite backend storage.
5. **Clean State & Genuine Empty States**:
   - Initialized `resumes = []` and `applications = []` in clean state.
   - Rendered genuine empty state cards (`"No resume uploaded yet."`) across all 4 experience shells when no resume is present and Demo Mode is disabled.

---

## 3. Verified Test Results & Manual QA Audit

### Automated Test Suite (`backend/tests/test_resume_persistence_and_parsing.py`)
- **TEST A (Persistence Across Reloads)**: `PASS`
- **TEST B (PDF Binary Artifact Removal)**: `PASS`
- **TEST C (DOCX/TXT Import & Hydration)**: `PASS`
- **TEST D (Resume Versions Survival)**: `PASS`
- **TEST E (Clean State Without Fake Data)**: `PASS`
- **TEST F (Explicit Demo Mode Toggle)**: `PASS`
- **TEST G (Permanent Resume Deletion)**: `PASS`
- **TEST H (Active Version Restoration)**: `PASS`

### Manual Verification Cycle Results
1. Clean Saarthi Start: **PASS** (Starts in clean state, `resumes: []`).
2. Real Document Upload: **PASS** (Stores in vault, parses clean text).
3. PDF Artifact Inspection: **PASS** (Zero `%PDF-`, `/Title`, or `endobj` artifacts).
4. Browser Refresh (`F5` / Reload): **PASS** (Resume persists from SQLite DB).
5. App Close & Desktop Container Restart: **PASS** (Resume persists).
6. Backend Process Restart: **PASS** (Resume persists).
7. Create Resume Version: **PASS** (Version snapshot stored in DB).
8. Refresh After Version Creation: **PASS** (Active version restored).
9. Delete Resume & Refresh: **PASS** (Resume permanently deleted, clean empty state restored).

---

## 4. Live Feature Test Matrix

| ID | Feature / Screen | Test Description | Status | Verification Result |
| :--- | :--- | :--- | :---: | :--- |
| **SYS-01** | Window Launch | Native container window opens at `1280x820` | **PASS** | Opened via `pywebview` & browser |
| **SYS-02** | Backend Health | `/api/health` loopback binding | **PASS** | `127.0.0.1:8000` status ok |
| **SYS-03** | Local Ollama | GGUF model tag verification | **PASS** | `nemotron-3-nano:4b` responsive |
| **RES-01** | Master Resume | Import PDF/DOCX file | **PASS** | Parses clean text, stores in vault DB |
| **RES-02** | Resume Versioning | Create variant resume snapshot | **PASS** | Version persisted to SQLite DB |
| **RES-03** | Refresh Persistence | State retention across browser/app reload | **PASS** | Hydrated cleanly via `listResumes` |
| **RES-04** | Artifact Stripping| Eliminate binary PDF object noise | **PASS** | Zero PDF syntax leaks |
| **RES-05** | Clean Slate | Initial state without fake candidate data | **PASS** | Shows `"No resume uploaded yet."` |
| **TAIL-01**| JD Matching | Requirement extraction & evidence ranking | **PASS** | Matches JD keywords against resume |
| **TAIL-02**| Truthful Rewrite | Diff review & ATS score updates | **PASS** | User facts preserved |
| **CARE-01**| Application Tracker | Add job dossier & update pipeline stage | **PASS** | Saved to SQLite DB |
| **CARE-02**| STAR Interview Drill | STAR rubric scoring with Nemotron | **PASS** | Evaluated locally |
| **AI-01** | Assistant Drawer | Send prompt (Ctrl+J) and receive local streaming | **PASS** | Nemotron streaming response |
| **AI-02** | Command Palette | Open palette (Ctrl+K) & navigate sections | **PASS** | Keyboard navigation functional |
| **PRIV-01**| Privacy Vault | Purge memory & check zero network leaks | **PASS** | 100% loopback on `127.0.0.1` |
