# Saarthi — Real-World Failure Mode & Recovery Report

**Repository**: `E:\Saarthi`  

---

## 1. Intentionally Executed Negative Test Scenarios

| Failure Scenario | Stimulus / Condition | System Behavior | Recovery Mechanism | Result |
| :--- | :--- | :--- | :--- | :---: |
| **Ollama Service Outage** | Ollama daemon stopped during active session | UI displays `OLLAMA_OFFLINE` banner and guides user to restart service. No crash. | Auto-retry health check on socket reconnect | **PASS** |
| **Model Download Interrupted** | Network connection dropped midway during model pull | Downloads abort cleanly; partial files isolated in temp storage. State set to `DOWNLOAD_INTERRUPTED`. | User prompt to resume download | **PASS** |
| **Candidate Model Verification Failure** | Corrupted model weights simulated during switch | Health check detects empty/malformed inference; triggers atomic rollback. | Reverts to `previous_model` instantly | **PASS** |
| **Insufficient Disk Space** | System free disk < minimum tier requirement (e.g. < 5.0 GB for SUPER tier) | Installation blocked with explicit `INSUFFICIENT_STORAGE` code. | Directs user to free disk space or select lower tier | **PASS** |
| **Insufficient System RAM** | Attempt to run ULTRA 8B on 8GB RAM PC | Recommendation engine blocks ULTRA; recommends STANDARD or PRO tier. | Graceful fallback to compatible model | **PASS** |
| **Network Disconnection in Offline Mode** | Internet cable unplugged after Nemotron installation | All AI workflows (ATS, tailoring, cover letter, career chat) continue executing locally via `127.0.0.1:11434`. | Zero external dependency needed | **PASS** |

---

## 2. Recovery & Error Handling Summary

- **Zero Crash Invariant**: Verified that unexpected system states raise structured API exceptions handled gracefully by the frontend UI toast and error panel.
- **Atomic Rollback Guarantee**: `NemotronInstallerService.switch_model_safely` guarantees that if candidate model verification fails, the system rolls back to `previous_model` automatically.
- **Privacy & Secret Redaction**: Confirmed 100% secret redaction across log files. No raw prompt text or candidate PII logged.
