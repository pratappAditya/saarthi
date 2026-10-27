# Saarthi — Hardware Diversity Failures & Recovery Report

**Validation Date**: August 20, 2026  
**Repository**: `E:\Saarthi`  

---

## 1. Intentionally Executed Failure Scenarios

| Failure Scenario | Stimulus / Condition | System Behavior | Recovery Mechanism | Result |
| :--- | :--- | :--- | :--- | :---: |
| **Unapproved Model Rejection** | User or API requests non-approved model (e.g. `claude-3-5-sonnet`) | `NemotronModelNotApprovedException` raised immediately at entry boundary. | Requests blocked cleanly; user informed of local Nemotron policy. | **PASS** |
| **Unapproved Model Switch** | Attempting to switch to unapproved string via `/api/nemotron/switch-model` | Blocked at entry boundary before network or Ollama invocation. | Active model remains unchanged (`nemotron-3-nano:4b`). | **PASS** |
| **Failed Model Verification** | Simulated corrupted candidate model weights during tier upgrade | `NemotronInstallerService` health check fails; triggers automatic atomic rollback. | Reverts active model to `previous_model` instantly. | **PASS** |
| **Ollama Outage / Disconnect** | Ollama daemon stopped while application is running | UI displays `OLLAMA_OFFLINE` banner with clear restart guidance. | Auto-retry health check on socket reconnect. | **PASS** |
| **Insufficient VRAM Enforcement** | Attempting to run 8B ULTRA tier on 4GB VRAM GPU | Recommendation engine flags `INSUFFICIENT_VRAM`. | Blocks ULTRA tier; recommends compatible `SUPER` or `PRO` model. | **PASS** |
| **Offline Internet Disconnect** | Internet cable unplugged after setup | All career workflows (ATS, tailoring, cover letter, STAR interview prep, career copilot) continue running locally via `127.0.0.1:11434`. | Zero external dependency needed. | **PASS** |

---

## 2. Beta Telemetry & Privacy Audit

- **Zero Prompt / PII Leakage**: Verified that operational telemetry logs contain ONLY anonymous operational event names (`PRICING_VIEWED`, `UPGRADE_PROMPT_SHOWN`, `CHECKOUT_STARTED`).
- **No Content Collection**: Resumes, cover letters, prompts, interview answers, and chat history are **100% excluded** from telemetry.
- **Local Network Endpoint**: All AI requests bind strictly to `127.0.0.1:11434`. Zero cloud LLM API calls permitted.
