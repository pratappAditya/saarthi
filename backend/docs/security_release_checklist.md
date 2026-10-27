# Saarthi Security Release Checklist

## Overview
This checklist records the security verification results for the Saarthi v0.5 Release Candidate.

---

## Security Verification Checklist

| Security Control | Verification Status | Verified By | Notes / Test Coverage |
| :--- | :--- | :--- | :--- |
| **Workspace Sandbox** | [X] VERIFIED | `test_tools.py`, `test_tool_adversarial.py` | Access restricted strictly to `settings.ALLOWED_ROOTS`. |
| **Path Traversal Protection** | [X] VERIFIED | `test_v03_loop_fixes.py` | Traversals (`../`, `C:\Windows\...`, symlinks) blocked by `validate_and_normalize_path()`. |
| **Permission Enforcement** | [X] VERIFIED | `test_permission_contract.py` | `USER_CONFIRMATION` tools require interactive user approval. |
| **Privileged Tool Protection** | [X] VERIFIED | `test_permission_adversarial.py` | `PRIVILEGED` safety level tools are strictly rejected. |
| **Cancellation Safety** | [X] VERIFIED | `test_sync_tool_isolation.py` | Cancellation cannot bypass security checks or leave stuck states. |
| **Secret Rejection** | [X] VERIFIED | `test_secret_redaction.py` | Passwords, API keys, and bearer tokens rejected from memory. |
| **Log Sanitization** | [X] VERIFIED | `test_secret_redaction.py` | Stack traces and credentials redacted from diagnostic logs. |
| **Reasoning Leakage** | [X] VERIFIED | `test_model_contract.py` | `<think>` and `<thinking>` blocks stripped from outputs. |
| **Untrusted Data Isolation** | [X] VERIFIED | `trust_boundary.md` | Files, memory, and tool results isolated as passive string DATA. |
| **Prompt Injection Resistance** | [X] VERIFIED | `test_model_adversarial.py` | Prompts cannot modify system permissions or security policy. |
| **Session Isolation** | [X] VERIFIED | `test_session_contract.py` | History, memory, and permissions isolated per `session_id`. |
| **API Contract Validation** | [X] VERIFIED | `test_api_contract.py` | Input types, missing fields, and error codes verified. |
| **Database Integrity** | [X] VERIFIED | `test_database_integrity.py` | Concurrent writes serialized safely without corruption. |
| **No Credentials in Source** | [X] VERIFIED | `release_source_hygiene.md` | `.env` excluded from version control; `.env.example` uses mocks. |
| **Safe Production Defaults** | [X] VERIFIED | `production_configuration.md` | Host bound to `127.0.0.1`; timeout and iteration caps enforced. |
