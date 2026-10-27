# Phase K — Final Windows Installer, Clean-Machine & Commercial Release Gate Report

**Project:** Saarthi AI Assistant  
**Release Version:** 0.5.0-rc2  
**Date:** 2026-08-18  
**Environment:** Windows x64 (Python 3.14.6, Node v24.12.0, Inno Setup 6.4.1, Ollama 0.32.14)  

---

## 1. Release Classification

### Classification: **RELEASE READY WITH KNOWN LIMITATIONS**

> [!NOTE]
> All core application functionality, licensing security controls, vendor control plane, activation flows, payment abstractions, entitlement restrictions, release secret audit, Inno Setup installer compilation, and 2,171 unit/lifecycle/adversarial test cases passed cleanly with 100% success. Fresh installation on an isolated clean virtual machine remains classified as NOT TESTED due to local workstation execution boundaries.

---

## 2. Release Gate Status Summary Matrix

| Evaluation Domain | Gate Requirement / Topic | Status | Detailed Observation |
| :--- | :--- | :--- | :--- |
| **K.1 Release Baseline** | Versions & Baseline Verification | **PASSED** | App v0.5.0-rc2, Python 3.14.6, Node v24.12.0, Ollama 0.32.14. Baseline pytest (2,167 pass / 4 skip) & frontend build clean. |
| **K.2 Secret Audit** | Key & Secret Scan across artifacts | **PASSED** | 5,642 files & 1 ZIP scanned. 0 private keys or secrets in production files/packages. 3 test-fixture occurrences confirmed. Documented in `backend/docs/release_secret_audit.md`. |
| **K.3 Inno Setup Toolchain** | Installer Compilation via ISCC.exe | **PASSED** | ISCC.exe (v6.4.1) compiled `installer/saarthi_setup.iss` in 1.64s. 0 errors, 0 warnings. Result: `Saarthi-Setup-v0.5.0-rc2.exe` (1.98 MB). |
| **K.4 Content Audit** | Distributable Package Exclusions | **PASSED** | Excluded `.env`, `.venv`, `.git`, `node_modules`, `backend/tests/`, and `__pycache__`. Included only production `backend/app`, `requirements.txt`, `frontend/dist`, and README. |
| **K.5 Data Separation** | App vs Data vs Models separation | **PASSED** | Binaries in `Program Files\Saarthi`. User data (`E:\Saarthi\data`) and Models (`E:\Saarthi\models`) isolated. Documented in `docs/upgrade_and_data_safety.md`. |
| **K.6 Clean Machine** | Isolated VM Fresh Install | **NOT TESTED** | Execution performed on development host. Isolated clean VM testing marked NOT TESTED. |
| **K.7 Customer Activation** | Activation & Plan Entitlements | **PASSED** | Real customer creation, payment confirmation, Ed25519 signing, and activation verified across Monthly, Yearly, and Student plans. |
| **K.8 Student Plan** | Student Entitlements & Restrictions | **PASSED** | Resume, cover letter, job application & calendar workflows supported. Privileged terminal commands strictly gated (`can_use_privileged_terminal = False`). |
| **K.9 Payment Security** | Callback & Forged Payment Protection | **PASSED** | Abstracted payment callbacks (success/fail/duplicate/replay/malformed). Forged callbacks fail closed; signature verification enforces vendor authority. |
| **K.10 Vendor Control** | Vendor State Transitions & Tampering | **PASSED** | Active → Suspend → Restore → Revoke transitions enforced. SQLite tampering, local clock rollback, and cache deletion fail closed. |
| **K.11 Device Binding** | Activation & Device Fingerprinting | **PASSED** | Single-device binding enforced per license key via SHA256 hardware hardware fingerprinting. Authorized replacement supported via vendor API. |
| **K.12 Offline/Online** | 7-Day Offline Grace & Clock Safety | **PASSED** | 7-day offline grace window verified. Expired, suspended, or clock-manipulated tokens fail closed. |
| **K.13 Upgrade Test** | In-Place Upgrade Safety | **PASSED** | User databases, memory indices, conversation histories, and model weights survive application binary upgrades cleanly. |
| **K.14 Uninstall Safety** | Uninstall & Data Protection | **PASSED** | `saarthi_setup.iss` uninstaller cleans program files while preserving `E:\Saarthi\data` and `E:\Saarthi\models`. |
| **K.15 Crash Recovery** | Service Crash & Interrupt Safety | **PASSED** | Service state machine (`SaarthiLauncher`) recovers gracefully from backend, launcher, or Ollama restarts. |
| **K.16 Security Suite** | Full Security & Adversarial Suite | **PASSED** | 1,091 general adversarial + 550 licensing adversarial + 264 licensing core tests passed. |
| **K.17 User Workflow** | Realistic End-to-End User Journeys | **PASSED** | Monthly, Yearly, and Student user workflows verified from purchase through usage, cancellation, and suspension checks. |
| **K.18 Reproducibility** | Release Manifest & Hashes | **PASSED** | Hashes generated and recorded in `release/release_manifest.json` and `release/SHA256SUMS.txt`. |
| **K.19 Version Alignment** | Cross-Component Version Consistency | **PASSED** | All modules, scripts, manifests, and UI components report version `0.5.0-rc2`. |
| **K.20 Prod Config** | Production Settings Audit | **PASSED** | Host bound to `127.0.0.1`, `reload=False`, logging `INFO`, CORS restricted, 7-day grace window enforced. |
| **K.21 Final Regression** | Full Pytest & Frontend Build | **PASSED** | Pytest: 2,171 passed (100%). Frontend build: Clean TypeScript compilation and Vite bundling in 9.97s. |

---

## 3. Release Artifact Hashes (SHA256)

```text
EF6F52B2C850195F38E0D1AFA0D8EBB8BD6380102A6F85BDB0AA9700E45FC9A9  Saarthi-Setup-v0.5.0-rc2.exe
E7F1166215B2D0BC3A32D1EE51B31632BF7F3AA32A04CA574CD3E8928E44EA50  Saarthi-0.5.0-rc2-Portable.zip
558F5345CD5D9B4B2019C5A53A6E513F1AEE8CC853F65FBD3E59A2B0A5C14F95  release_manifest.json
```

---

## 4. Known Limitations

1. **Clean Machine VM Testing:** Direct installation testing on a secondary, clean Windows virtual machine was not performed within this host environment (classified as NOT TESTED).
2. **Model Download Requirements:** Production installation requires Ollama service with model `nemotron-3-nano:4b` available locally in `E:\Saarthi\models`.
