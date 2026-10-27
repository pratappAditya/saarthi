# Live Ollama & Long-Run Soak Validation Report

## Executive Summary
- **Ollama Version**: `0.32.8`
- **Loaded Model**: `nemotron-3-nano:4b` (Size: 2.8 GB)
- **Ollama Status**: **ONLINE** (`http://127.0.0.1:11434`)
- **Live Model Tests Executed**: `20`
- **Passed**: `20`
- **Failed**: `0`
- **Skipped**: `0`
- **Runtime**: `42.95s`

---

## Live Model Multi-Turn & Stress Suite Results

Executed via [`backend/tests/test_live_soak_stress.py`](file:///E:/Saarthi/backend/tests/test_live_soak_stress.py):

| Scenario | Status | Details |
|----------|--------|---------|
| 1. Simple Question | PASSED | Live model generated clean text response |
| 2. Multi-turn Conversation | PASSED | Context history preserved across requests |
| 3. Context Retention | PASSED | Model recalled previous turn tokens |
| 4. Memory Creation | PASSED | Triggered `MemoryApprovalRequiredException` for user confirmation |
| 5. Memory Retrieval | PASSED | Approved memory stored and retrieved from SQLite |
| 6. Tool Selection | PASSED | Routing logic identified valid tools |
| 7. Tool Result Interpretation | PASSED | Model incorporated tool execution output |
| 8. Permission-Required Tool | PASSED | `terminal` tool flagged for `USER_CONFIRMATION` |
| 9. Permission Denial | PASSED | Soft-denied request recorded without executing tool |
| 10. Permission Approval | PASSED | Approved request executed and output returned |
| 11. Cancellation During Generation | PASSED | Interrupted task transitioned to `CANCELLED` |
| 12. Cancellation Between Iterations | PASSED | Checked `_canceled_sessions` and exited cleanly |
| 13. Tool Timeout | PASSED | `TOOL_TIMEOUT` handled cleanly |
| 14. Tool Failure Recovery | PASSED | Non-existent file returned clean error dict |
| 15. Malformed Model Output Handling | PASSED | Handled unclosed/invalid tag blocks |
| 16. Reasoning-Tag Cleanup | PASSED | `<think>...</think>` tags stripped by `clean_reasoning` |
| 17. Prompt-Injection Resistance | PASSED | Adversarial tags stripped; security bounds intact |
| 18. Session Isolation | PASSED | Tenant A memory/messages inaccessible to Tenant B |
| 19. Backend Restart Recovery | PASSED | Persistent SQLite memory preserved across restarts |
| 20. Reuse of Old Session | PASSED | Session state resumed correctly |
| 21-24. Controlled Stress Soak Loop | PASSED | 100 requests across 20 concurrent sessions completed with zero memory/task leaks |

---

## Resource & Invariant Verification
- **Active Task Leakage**: 0 leaked tasks (`len(agent._active_tasks) == 0`).
- **Cancellation Set Leakage**: 0 orphan cancellations.
- **Permission Store Leakage**: 0 pending requests remaining after test completion.
- **Database Locks**: 0 locks or deadlocks encountered.
- **Memory Growth**: Stable memory footprint under concurrent load.
