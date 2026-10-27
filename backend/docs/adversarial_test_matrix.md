# Saarthi Phase I — 1000+ Parameter Adversarial Test Matrix

## Overview
This document specifies the 20 test categories (A through T) comprising the **Saarthi Adversarial Test Suite**. The suite guarantees at least 1,000 distinct parameterized test cases exercising all combinations of inputs, boundary conditions, permissions, memory, tools, failure injection, and state transitions.

---

## Test Categories & Parameterization Breakdown

### A. API Inputs (fuzzing & boundary values)
- **Parameters**: Empty message, whitespace, single char, max length (100,000 chars), unicode, emoji (`😀🚀`), Hindi (`सारथी एजेंट`), CJK, control characters (`\x00\x1f`), unclosed newlines, malformed session IDs, repeated session IDs, unusual request ordering.
- **Expected Outcome**: Sanitized or valid processing; zero unhandled crashes or unparsed exceptions.

### B. Model Outputs (generation parsing & injection defense)
- **Parameters**: Empty response, whitespace, malformed JSON, truncated JSON, nested JSON, duplicate keys, unknown tool names, malformed tool markers (`[TOOL_CALL: ...]`), multiple markers, unclosed `<think>` tags, fake system messages, fake permission approval injections (`[PERMISSION_APPROVED]`).
- **Expected Outcome**: Reasoning cleaned, invalid tool calls handled gracefully, zero fake permission authority leakage.

### C. Tool Arguments (type safety & payload validation)
- **Parameters**: Missing required fields, null values, empty strings, wrong data types (int vs string), extra unknown fields, nested objects, arrays, oversized payloads, unicode strings.
- **Expected Outcome**: Schema validation rejection or clean tool execution error; zero stack traces.

### D. Path Handling & Sandbox Boundaries
- **Parameters**: Relative paths (`./foo`), absolute paths (`C:\Users\...`), traversal sequences (`../../etc/passwd`), encoded traversals (`%2e%2e%2f`), mixed slash styles (`C:/Windows\System32`), UNC paths (`\\server\share`), out-of-sandbox target (`C:\Windows\System32\drivers\etc\hosts`).
- **Expected Outcome**: Strict boundary enforcement; out-of-sandbox targets DENIED.

### E. Permissions Workflow & Security Contracts
- **Parameters**: Correct request, invalid request ID, wrong session ID, wrong tool name, expired request ID, duplicate approval, duplicate denial, approval after denial, denial after approval, malformed payload.
- **Expected Outcome**: Immutable request states, HTTP 400 rejection on replay attempts, cross-session rejection.

### F. Session Isolation & Cross-Session Attack Vectors
- **Parameters**: Session A attempting to read Session B's history, Session A reading Session B's memory, Session A approving Session B's permission, Session A cancelling Session B, Session A accessing Session B's workspace files.
- **Expected Outcome**: Strict session boundary isolation; 100% rejection of cross-session access.

### G. Memory Management & Secret Screening
- **Parameters**: Normal memory text, duplicate memory, empty memory, 50,000-char long memory, password patterns (`password=12345`), API keys (`sk-proj-12345`), bearer tokens, connection strings (`postgres://...`), unicode text, cross-session retrieval, project scoping, concurrent writes.
- **Expected Outcome**: Secret screening rejects credential patterns; memory retrieved accurately by score; zero cross-project leakage.

### H. Cancellation Latency & Safety
- **Parameters**: Cancellation before model generation, during model generation, during tool execution, during permission prompt, at iteration boundary, after completion.
- **Expected Outcome**: Agent state cleanly transitions to `CANCELLED`; zero orphaned background processes; subsequent messages work normally.

### I. Synchronous Tool Isolation & Timeout Contracts
- **Parameters**: Sync tool execution on thread pool, sync tool timeout (e.g. 1.0s limit), cancellation of sync tool, terminal tool process timeout.
- **Expected Outcome**: Main asyncio event loop remains 100% unblocked; timed out tools report timeout cleanly without stuck states.

### J. Error Handling & Sanitization
- **Parameters**: Invalid state transition, database locking error, missing file, permission denial, tool exception, network timeout.
- **Expected Outcome**: Normalized `SaarthiError` responses; zero stack traces or internal local file paths exposed to user.

### K. Database Integrity & Transaction Concurrency
- **Parameters**: Concurrent SQLite writes across 10 sessions, interrupted transactions, repeated database startup, restart during active operation.
- **Expected Outcome**: WAL mode safety; zero database corruption or locked transaction deadlocks.

### L. Concurrency & Multi-Session Load
- **Parameters**: 2, 5, 10, 20, 50 concurrent active sessions issuing simultaneous chat & tool requests.
- **Expected Outcome**: Isolated execution per session; no state mixing.

### M. Prompt-Injection Resistance
- **Parameters**: Instructions attempting to override system prompt ("Ignore previous instructions..."), fake system authority, prompt injection embedded in file contents, prompt injection in memory entries.
- **Expected Outcome**: User input and file contents treated strictly as untrusted DATA, not system instructions.

### N. Secret Redaction
- **Parameters**: System logs, error responses, memory entries containing AWS keys, GitHub tokens, JWT tokens, RSA private keys.
- **Expected Outcome**: Automatic secret redaction replacing secrets with `[REDACTED_SECRET]`.

### O. Resource Limits
- **Parameters**: Max iteration limit reached (e.g. 10 iterations), max tool result size clipping, search result limits.
- **Expected Outcome**: Clean termination at iteration limit without runaway loops.

### P. State Machine Exhaustion
- **Parameters**: All 9 legal state transitions (`IDLE` -> `RUNNING` -> `WAITING_MODEL` -> ... -> `COMPLETED`/`CANCELLED`/`FAILED`), and 30+ illegal state transitions (e.g. `COMPLETED` -> `EXECUTING_TOOL`).
- **Expected Outcome**: Illegal transitions fail closed with `InvalidStateTransitionError`.

### Q. Tool Execution Matrix (All Production Tools)
- **Parameters**: Fuzzing parameters specifically for `file_list`, `file_read`, `file_search`, `system_info`, `terminal`, and `suggest_memory`.
- **Expected Outcome**: 100% parameter coverage across all 6 production tools.

### R. Malformed Data
- **Parameters**: Truncated HTTP request bodies, non-JSON bodies, invalid header types.
- **Expected Outcome**: Clean HTTP 400 / 422 error responses.

### S. Failure Injection & Recovery
- **Parameters**: Injected Ollama disconnects, filesystem permission errors, process termination.
- **Expected Outcome**: Controlled error state; successful recovery on retry.

### T. Frontend / API Contracts
- **Parameters**: Verification of `/api/status`, `/api/chat`, `/api/history`, `/api/memory`, `/api/permissions`, `/api/cancel`.
- **Expected Outcome**: 100% contract compliance with UI TypeScript types.
