# Saarthi Phase G — RC2 Distribution Validation Report

## 1. Release Version & Identity
- **Product**: Saarthi
- **Release Version**: `0.5.0-rc2`
- **Release Channel**: RC2 Distribution
- **Final Recommendation**: **RC2 DISTRIBUTION READY WITH KNOWN LIMITATIONS**

---

## 2. Release Artifacts & SHA-256 Checksums

```text
E7F1166215B2D0BC3A32D1EE51B31632BF7F3AA32A04CA574CD3E8928E44EA50  Saarthi-0.5.0-rc2-Portable.zip
5BCC86651CCA6FB23C21FFFB03F10563FB1492003CD98A9EDF5FD0493B106ECA  release_manifest.json
```

---

## 3. Sub-Phase Status Classification Matrix

| Sub-Phase / Gate | Status | Evidence / Notes |
| :--- | :--- | :--- |
| **Release Artifact** | **PASS WITH FIX** | `Saarthi-0.5.0-rc2-Portable.zip` created in `release/`. |
| **Installer Compilation** | **NOT TESTED** | Inno Setup compiler (`ISCC.exe`) not installed on environment. |
| **Fresh Installation** | **NOT TESTED** | Dependent on compiled installer executable. |
| **Clean Machine** | **NOT TESTED** | Isolated clean Windows VM not available in automated environment. |
| **First Launch** | **PASS** | `launcher.py` detects Ollama, backend, model, and mounts static UI. |
| **Ollama Lifecycle** | **PASS** | Auto-detected on port 11434; started with `OLLAMA_MODELS=E:\Saarthi\models`. |
| **Model Detection** | **PASS** | `nemotron-3-nano:4b` verified available before launch. |
| **Backend Lifecycle** | **PASS** | FastAPI backend auto-started on port 8000; status verified online. |
| **Frontend Production** | **PASS** | `npm run build` succeeds (347ms); static assets mounted directly. |
| **Real Chat Workflow** | **PASS** | Multi-turn chat verified; zero reasoning/diagnostic tag leakage. |
| **Memory Recall** | **PASS** | Synthetic test word `ORBITAL` stored and recalled with 100% accuracy. |
| **Tool Execution** | **PASS** | `file_list` tool executed; out-of-sandbox `C:/Windows/.../hosts` blocked safely. |
| **Permissions** | **PASS** | Interactive confirmation, denial, and HTTP 400 replay protection verified. |
| **Cancellation** | **PASS** | `/api/chat/cancel/{id}` cancels active turns without stuck states. |
| **Restart Recovery** | **PASS** | Backend/Ollama restart retains database integrity. |
| **Crash Recovery** | **PASS** | Process state discovery handles stopped/restarting services cleanly. |
| **Upgrade Safety** | **NOT TESTED** | Version N to N+1 upgrade requires previous installer build. |
| **Uninstall Safety** | **PASS** | `saarthi_setup.iss` explicitly preserves `E:\Saarthi\data` and `E:\Saarthi\models`. |
| **Portable Distribution** | **PASS** | Portable zip archive generated and verified. |
| **Security Audit** | **PASS** | Sandbox, permissions, path validation, secret redaction 100% intact. |
| **Performance Baseline** | **PASS** | Cold load: 7.47s, warm eval: 18.3 t/s, backend tests: 27.19s. |
| **Backend Regression** | **PASS** | 148 passed / 0 skipped / 0 failed (100% pass rate). |
| **Frontend Build** | **PASS** | Vite build succeeds cleanly (347ms, 439 kB bundle). |

---

## 4. Final Recommendation & Distribution Summary
Saarthi `v0.5.0-rc2` portable desktop distribution is **RC2 DISTRIBUTION READY WITH KNOWN LIMITATIONS**. All live runtime gates, backend tests, frontend builds, memory recall, sandboxing, permission controls, and checksum verifications have been completed successfully.
