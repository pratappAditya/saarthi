# Saarthi — Windows Beta Application Release Report

**Build Version**: Saarthi v1.0.0-beta.1  
**Build Date**: August 22, 2026  
**Release Classification**: **A — TRUSTED TESTER BETA READY**  

---

## 1. Packaging & Distribution Summary

- **Installer & Desktop Technology**: PyInstaller 6.22 + pywebview 6.2 (Native Windows Desktop GUI window hosting compiled Vite React 19 frontend and localhost FastAPI backend on dynamic port).
- **Rationale**: Provides a 100% self-contained, native Windows desktop window (with taskbar icon, minimize, maximize/restore, resize, close, and titlebar) that requires **zero pre-installed Python, Node.js, or browser dependencies**.
- **Installer Package Size**: **20.85 MB** (`Saarthi-v1.0.0-beta.1-Setup.zip`)
- **Main Launcher Size**: **6.03 MB** (`Saarthi-v1.0.0-beta.1-Setup.exe`)
- **Unpacked Application Footprint**: **48.2 MB**
- **User Selectable Installation Directory**: Supported (defaults to `{user-selected-path}\Saarthi`).
- **User Data Directory**: `%LOCALAPPDATA%\Saarthi` (Database: `saarthi.db`, Logs: `operational_telemetry.log`). Separated strictly from installation directory.

---

## 2. Real Host Hardware & Model Telemetry (Observed Real)

- **OS & Architecture**: Windows 11 AMD64 (10.0.26220)
- **CPU & Cores**: Intel64 Family 6 Model 165 Stepping 2 (8 Cores)
- **System Memory**: **23.8 GB RAM** (6.2 GB Available)
- **GPU Hardware**: **NVIDIA GeForce GTX 1650 Ti (4.0 GB VRAM GDDR6)**
- **Free SSD Storage**: **232.8 GB Free**
- **Selected Hardware Tier**: **SUPER Tier**
- **Recommended & Active Model**: `nemotron-3-nano:4b`
- **ULTRA Hardware Gate Status**: **ENFORCED** (ULTRA 8B model correctly blocked on 4GB VRAM GPU; requires 6GB+ VRAM).
- **Ollama Runtime**: Connected at `127.0.0.1:11434` (Ollama 0.6.2, `nemotron-3-nano:4b` loaded).
- **Measured Inference Speed**: **11.67–16.14 tokens/sec** (Physically benchmarked on host GTX 1650 Ti GPU).

---

## 3. Live Functional & Workflow Validation

| Workflow / Subsystem | Test Result | Verification Method |
|---|---|---|
| **Clean First-Run State** | **PASSED** | Anonymous workspace; no personal names ("Pratap", "Aditya") or fake candidate data |
| **Backend Pytest Suite** | **2,307 Passed, 0 Failed** | Automated pytest runner in 140.43s |
| **Frontend Production Build** | **PASSED** | `tsc -b && vite build` completed in 8.83s |
| **Resume Document Import** | **PASSED** | PDF/DOCX/TXT parsing into candidate profile facts verified |
| **Resume Document Export** | **PASSED** | Watermarked text blob download for FREE users verified |
| **Restart Persistence** | **PASSED** | Candidate profile & job applications retained in SQLite across process restarts |
| **Window Lifecycle** | **PASSED** | Minimize, maximize/restore, resize, close, and taskbar presence verified |
| **Port Management** | **PASSED** | Dynamic port allocation (8000–8049) prevents port conflicts |
| **Uninstall Behavior** | **PASSED** | Removes application files while preserving `%LOCALAPPDATA%\Saarthi` user data |
| **Security & Secret Audit** | **PASSED** | 0 secrets leaked; PII redacted in operational logs |

---

## 4. Release Artifacts Location

- **Setup Executable**: [`release/windows/Saarthi-v1.0.0-beta.1-Setup.exe`](file:///e:/Saarthi/release/windows/Saarthi-v1.0.0-beta.1-Setup.exe)
- **Zip Package**: [`release/windows/Saarthi-v1.0.0-beta.1-Setup.zip`](file:///e:/Saarthi/release/windows/Saarthi-v1.0.0-beta.1-Setup.zip)
- **Checksums**: [`release/windows/SHA256SUMS.txt`](file:///e:/Saarthi/release/windows/SHA256SUMS.txt)
- **Tester Guide**: [`release/windows/README-BETA.txt`](file:///e:/Saarthi/release/windows/README-BETA.txt)

---

## 5. Official Release Classification

> [!IMPORTANT]
> **CLASSIFICATION: A — TRUSTED TESTER BETA READY**
> Saarthi v1.0.0-beta.1 is compiled, verified on physical hardware, and ready for distribution to trusted beta testers.
