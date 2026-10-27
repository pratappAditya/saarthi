# Agent Loop Audit Report

## Overview
This document summarizes the audit and regression validation of the Saarthi v0.7 agent loop architecture (`backend/app/agent/core.py`).

- Verified the end‑to‑end call graph from API entry point through memory handling, tool routing, permission workflow, and final response generation.
- Confirmed that the maximum iteration count defaults to `settings.MAX_AGENT_ITERATIONS` (currently 6) and respects the `MAX_TOOL_ITERATIONS` safety limit.
- Validated that tool call parsing uses strict JSON schema validation and that malformed calls are recorded as errors.
- Ensured permission requests are created via `permission_store` and that privileged tools are blocked unless the permission level is elevated.
- Checked that memory retrieval respects project scoping and respects `settings.MAX_MEMORY_RESULTS` and context size limits.
- Confirmed that diagnostics are logged in JSON‑Lines format under `settings.SAARTHI_DATA_DIR/logs/agent_diagnostics.log`.
- No concurrency changes introduced beyond the existing async model.

---

# Phase A.1 Regression Validation

## Tests Implemented
The regression test suite has been implemented in `backend/tests/test_agent_loop_audit.py` containing 15 comprehensive unit & system tests using a controllable `RecordingMockModelProvider`:

1. `test_simple_response`: Direct Q&A without tool invocation.
2. `test_tool_loop`: Complete tool call request, execution, result injection, and final response.
3. `test_multiple_tool_calls_unsupported`: Verification that multiple tool call tags in a single iteration trigger controlled malformed error handling.
4. `test_malformed_tool_calls`: Coverage for invalid JSON, unknown tool, missing tool name, invalid arguments, and mismatched tag markers.
5. `test_tool_exception`: Containment of exceptions during tool execution.
6. `test_tool_timeout_absence`: Verification that execution timeout is currently absent in production `ToolExecutor`.
7. `test_max_iterations`: Bounded iteration execution matching `settings.MAX_AGENT_ITERATIONS`.
8. `test_empty_model_response`: Graceful handling of empty or whitespace-only model outputs.
9. `test_reasoning_cleanup`: Verification that `<think>`, `<thinking>`, `Thinking...`, and unclosed reasoning tags are stripped from output.
10. `test_permission_flow`: Permission request creation (`pending`), user denial, and user approval workflows.
11. `test_session_isolation`: Total isolation of history, tool calls, and memory between sessions.
12. `test_memory_behavior`: Deterministic memory retrieval, project scoping, and secret screening.
13. `test_model_call_counting`: Explicit baseline model invocation assertions.
14. `test_termination_paths`: Verification of all loop termination branches (normal completion, memory shortcut, model error, max iterations).
15. `test_cancellation_absence`: Verification that task cancellation tokens are currently absent in production.

## Coverage Matrix

| Area | Status / Classification | Description |
|---|---|---|
| Simple Response | WORKING AS DESIGNED | 1 model call, direct text output, stored in history |
| Tool Execution Loop | WORKING AS DESIGNED | Tool call -> execute -> feedback loop -> final response |
| Multiple Tool Calls | KNOWN LIMITATION | Single tool tag pair per turn contract; multiple tags return malformed tool call error |
| Malformed Tool Calls | WORKING AS DESIGNED | Returns structured error without crash or unhandled exception |
| Tool Exception Containment | WORKING AS DESIGNED | Tool errors returned as error results to model context safely |
| Tool Execution Timeout | KNOWN LIMITATION | Timeout is currently absent in `ToolExecutor` |
| Max Iteration Guard | WORKING AS DESIGNED | Bounded strictly by `MAX_AGENT_ITERATIONS` (6) |
| Empty Model Response | WORKING AS DESIGNED | Handled cleanly as empty text response without crashing |
| Reasoning Cleanup | WORKING AS DESIGNED | All `<think>`, `<thinking>`, `Thinking...` tags stripped before delivery |
| Permission Request Flow | WORKING AS DESIGNED | Rejects PRIVILEGED, yields `PermissionRequiredException` for USER_CONFIRMATION |
| Session Isolation | WORKING AS DESIGNED | History and session parameters strictly isolated per session ID |
| Memory Handling & Secrets | WORKING AS DESIGNED | Project scoped, secret keywords blocked from storage |
| Model Call Counting Baseline | WORKING AS DESIGNED | Simple = 1 call, Tool Loop = 2 calls, Permission Pause = 1 call, Max Iter = N calls |
| Termination Paths | WORKING AS DESIGNED | All 5 loop exit conditions terminate predictably |
| Task Cancellation | KNOWN LIMITATION | Asynchronous task cancellation hooks absent in `AgentCore` |

## Model Call Baseline
- **Simple Response:** Exactly 1 invocation.
- **One Tool Call Loop:** Exactly 2 invocations (Invocation 1 requests tool; Invocation 2 consumes result & answers).
- **Permission-Required Tool:** Exactly 1 invocation (Pauses at pending permission request before second invocation).
- **Max Iterations:** Exactly $N$ invocations where $N = \text{MAX\_AGENT\_ITERATIONS}$.
- **Memory Command Shortcut:** Exactly 0 invocations (Handled deterministically by `MemoryCommandProcessor`).

## Tool Execution
- `ToolExecutor` screens paths against `settings.ALLOWED_ROOTS` and redacts secrets from diagnostic logs.
- Tools execute asynchronously via `await tool.execute(**kwargs)`.
- Results are stored as structured JSON messages (`type: tool_result`) in SQLite memory.

## Permission Flow
- `READ_ONLY` & `SAFE` tools: Executed automatically.
- `USER_CONFIRMATION` tools: Pause execution, register request in `permission_store`, raise `PermissionRequiredException`.
- `PRIVILEGED` tools: Rejected immediately with `PERMISSION_DENIED`.

## Session Isolation
- SQLite memory queries filter strictly by `session_id`.
- Messages, tool invocations, and permission requests from Session A are unreachable by Session B.

## Memory
- Secret keywords (`password`, `key`, `token`, `secret`, `auth`, `credential`, `private`) raise `ValueError` on write attempt.
- Context is retrieved based on query relevance scoring and fitted under `MAX_MEMORY_CONTEXT_CHARS`.

## Error Handling
- Invalid JSON in tool call -> returns `MALFORMED_TOOL_CALL` error to model.
- Unknown tool name -> returns `UNKNOWN_TOOL` error to model.
- Missing/invalid argument -> returns `INVALID_ARGUMENT` error to model.
- Exceptions inside tools -> caught, logged, returned as `EXECUTION_ERROR` to model context.

## Timeout / Cancellation
- **Execution Timeout:** KNOWN LIMITATION (Currently absent in `ToolExecutor`).
- **Task Cancellation:** KNOWN LIMITATION (Currently absent in `AgentCore`).

## Reasoning Cleanup
- Verified using `app.models.ollama.clean_reasoning`:
  - `<think>...</think>` -> Stripped
  - `<thinking>...</thinking>` -> Stripped
  - `Thinking... ...done thinking.` -> Stripped
  - `<think>unclosed...` -> Truncated cleanly
  - Natural prose containing the word `"thinking"` -> Preserved

## Confirmed Bugs
- **None.** The existing `AgentCore` implementation operates strictly as designed according to specifications.

## Known Limitations (Resolved in Phase A.2)
1. **Multiple Tool Calls:** (Resolved in Phase A.2) Multiple tool call blocks in a single model response are now parsed and executed sequentially with aggregated results.
2. **Tool Execution Timeout:** (Resolved in Phase A.2) Configurable `TOOL_EXECUTION_TIMEOUT` (default: 30.0s) enforced in `ToolExecutor`.
3. **Task Cancellation:** (Resolved in Phase A.2) Active task registry and `cancel_session(session_id)` added to `AgentCore` and exposed via `POST /chat/cancel/{session_id}`.

---

# Phase A.2 — Agent Loop Reliability Hardening

## Overview
Phase A.2 resolved all three previously identified architectural limitations in the Saarthi agent loop without modifying production UI or model configuration:

1. **Sequential Multi-Tool Call Support:** Updated `AgentCore._run_agent_loop` regex parsing to extract multiple `[TOOL_CALL] ... [/TOOL_CALL]` blocks from a single model iteration, validate schemas individually, execute tools sequentially, store structured tool result cards for each tool, and pass aggregated tool results to the next model step. Backward compatibility with single-tool calls is 100% preserved.
2. **Tool Execution Timeout:** Added `TOOL_EXECUTION_TIMEOUT: float = 30.0` to `backend/app/config/settings.py`. Updated `ToolExecutor` to wrap tool execution in `asyncio.wait_for(tool.execute(...), timeout=self.timeout)`. Handled `asyncio.TimeoutError` by returning structured `TOOL_TIMEOUT` error cards (`code: "TOOL_TIMEOUT"`) to allow the model loop to recover or terminate cleanly.
3. **Task Cancellation Mechanism:** Added `_active_tasks` mapping and `_canceled_sessions` set to `AgentCore`. Implemented `cancel_session(session_id: str) -> bool` to cancel active asyncio tasks and flag cancelled sessions. Added checks for cancellation before model generation, after model generation, and before/during tool execution. Exposed API endpoint `POST /chat/cancel/{session_id}` in `backend/app/api/routes.py`.

## Reliability Test Suite (`backend/tests/test_agent_loop_reliability.py`)
A comprehensive 15-test reliability suite was created and verified:

1. `test_single_tool_backward_compatibility`: Verified 1 tool call per turn remains 100% backward compatible.
2. `test_multiple_tool_calls`: Verified multiple tool call blocks execute sequentially and aggregate results.
3. `test_multiple_tool_call_failure`: Verified partial failure handling when one tool succeeds and another fails in the same iteration.
4. `test_tool_timeout`: Verified structured `TOOL_TIMEOUT` error returned when tool execution exceeds timeout limit.
5. `test_tool_timeout_recovery`: Verified model receives timeout error and can recover to provide a final response.
6. `test_tool_timeout_termination`: Verified repeated timeouts respect `MAX_AGENT_ITERATIONS` limit.
7. `test_permission_tool_timeout`: Verified permission-required tools still pause for confirmation without timing out prematurely.
8. `test_cancel_before_model`: Verified pre-invocation cancellation returns a clean cancelled response without calling the model.
9. `test_cancel_during_model`: Verified cancellation during model execution stops model call cleanly.
10. `test_cancel_during_tool`: Verified cancellation during tool execution stops tool task cleanly.
11. `test_cancel_between_iterations`: Verified cancellation between iterations stops the loop safely.
12. `test_cross_session_cancellation_isolation`: Verified cancelling Session A leaves Session B unaffected.
13. `test_cancel_after_completion`: Verified cancelling a completed session is safe and idempotent.
14. `test_repeated_cancellation`: Verified multiple calls to `cancel_session` are idempotent.
15. `test_no_stuck_agent_state`: Verified agent state transitions cleanly between `success`, `error`, `pending_permission`, or `cancelled` and never remains stuck in `running`.

---

# Phase A.2.1 — Real-World Reliability Verification

## Overview
Phase A.2.1 verified that the multi-tool execution, tool timeout, and task cancellation mechanisms function reliably against Saarthi's production tools (`file_list`, `file_search`, `system_info`, `terminal`, `suggest_memory`) and API surface.

## Key Findings

### 1. Production Multi-Tool Verification
- Verified sequential execution of read-only production tools (`file_list`, `file_search`, `system_info`).
- Confirmed deterministic execution order, single execution per tool, distinct history entry generation (`type: "tool_result"`), and clean aggregation into final assistant responses.
- Verified partial failure policy: If Tool #1 fails due to invalid parameters/paths, Tool #1 is not retried, Tool #2 executes safely, and both results are passed to the model.

### 2. Real Tool Timeout Verification
- **Async Tools:** Natively async coroutines yielding via `await` are cancelled cleanly by `asyncio.wait_for(tool.execute(...), timeout=...)`, returning a structured `TOOL_TIMEOUT` error result.
- **Synchronous Blocking Tools:** Python functions running synchronous blocking calls (e.g. `time.sleep` or heavy C routines) directly on the main event loop thread block the thread. `asyncio.wait_for` evaluates timeout status only after the synchronous call finishes.
- **Subprocess Tools:** `TerminalTool` enforces `settings.TERMINAL_TIMEOUT_SECONDS` (30.0s) inside `subprocess.run(..., timeout=...)`. If `subprocess.run` times out, Python catches `subprocess.TimeoutExpired`, terminates the process, and returns `exit_code: -1` with `[Command timed out...]` stderr.

### 3. Task Cancellation Verification (`POST /api/chat/cancel/{session_id}`)
- Verified all cancellation branches A–G via FastAPI `TestClient`:
  - Cancel before model execution -> Returns cancelled response immediately without calling model.
  - Cancel during model execution -> Cancels `asyncio.Task`, sets `completion_state = "cancelled"`.
  - Cancel during tool execution -> Cancels tool coroutine, returns cancelled response.
  - Cancel between iterations -> Detected at loop boundary, exits cleanly.
  - Cancel completed / non-existent session -> Returns HTTP 200 `{"session_id": "...", "cancelled": false}` safely without error.
  - Cross-session cancellation -> Session A cancellation does not affect Session B.

### 4. Ollama Verification
- Client Version: Ollama 0.32.8.
- Status: Daemon server offline during test run (`http://localhost:11434` inactive).
- Live Ollama tests were configured to check availability dynamically and skip cleanly when offline.

### 5. Security & Permission Verification
- Cancellation cannot approve permissions, bypass safety checks, or grant elevated access.
- Cancelled requests cannot execute privileged tools.
- Stale cancellation tokens are cleared when a new request is initialized on the session.

### 6. Performance & Latency Measurements
| Workload | Average Latency (Mock Model) | Result / Status |
|---|---|---|
| Simple Response | 0.002s | Clean direct text |
| Single Tool Call | 0.008s | 2 model turns + tool exec |
| Multi-Tool Call (3 Tools) | 0.015s | 2 model turns + 3 tool execs |
| Async Tool Timeout | 0.052s | `TOOL_TIMEOUT` returned |
| Task Cancellation | 0.001s | Instant cancellation |

### 7. Bugs Discovered & Fixes Applied
- **Bug Fix:** Fixed task registry lifecycle in `AgentCore.handle_message` by wrapping the full message handler in a single outer `try...finally` block to ensure `_active_tasks[session_id]` is not prematurely popped before `_run_agent_loop` finishes.
- **Bug Fix:** Updated API endpoint cancellation test routes to use `/api/chat/cancel/{session_id}` prefix matching FastAPI router configuration.

### 8. Full Verification Results
- **Live Reliability Suite (`test_agent_loop_live_reliability.py`):** 9 passed, 1 skipped in 4.64s.
- **Unit & System Audit Suite (`test_agent_loop_audit.py`):** 15 passed in 1.75s.
- **Hardening Reliability Suite (`test_agent_loop_reliability.py`):** 15 passed in 1.43s.
- **Complete Backend Test Suite:** 92 passed, 4 skipped in 13.98s.
- **Frontend Build (`npm run build`):** Built successfully in 467ms (`dist/assets/index-BZN2rgmo.js` 438.82 kB).

---

# Phase A.3 — Synchronous Tool Isolation

## Overview
Phase A.3 prevents synchronous/blocking production tools from stalling the `AgentCore` asyncio event loop thread. All registered production tools were audited and classified, and synchronous execution paths were offloaded to worker threads via `asyncio.to_thread()`.

## 1. Production Tool Classification Matrix

| Tool Name | Class Name | Category | Primary Operations | Execution Strategy |
| :--- | :--- | :--- | :--- | :--- |
| `file_list` | `FileListTool` | **Category C** | Directory scanning (`os.scandir`/`os.walk`) | Worker thread via `asyncio.to_thread()` |
| `file_read` | `FileReadTool` | **Category B & C** | Read file (<512KB cap), UTF-8 check | Worker thread via `asyncio.to_thread()` |
| `file_search` | `FileSearchTool` | **Category C & E** | Directory walk & string search (up to 1,000 files) | Worker thread via `asyncio.to_thread()` |
| `system_info` | `SystemInfoTool` | **Category C & D** | `subprocess.check_output` (`wmic`, `node`, `git`, `docker`, `wsl`) | Worker thread via `asyncio.to_thread()` |
| `terminal` | `TerminalTool` | **Category D & C** | `subprocess.run` (`powershell.exe` with OS process timeout) | Worker thread via `asyncio.to_thread()` + process timeout |
| `suggest_memory` | `SuggestMemoryTool` | **Category B** | SQLite memory request store | Worker thread via `asyncio.to_thread()` |

## 2. Chosen Execution Strategy
- **Worker Thread Offloading**: `ToolExecutor.execute_tool` inspects tool definitions (`is_synchronous` flag or non-coroutine `execute`). For synchronous tools, `asyncio.to_thread` dispatches execution to `concurrent.futures.ThreadPoolExecutor` worker threads.
- **Event Loop Responsiveness**: While the worker thread executes synchronous filesystem or OS operations, the main asyncio event loop yields control immediately. Other coroutines, timers, background tasks, and cancellation handlers run unhindered.
- **Backward Compatibility**: Production tools implement `is_synchronous = True` and delegate `async def execute(...)` to `asyncio.to_thread(self._execute_sync, ...)`. Direct invocations via `await tool.execute(...)` (e.g. in tests) automatically run in worker threads without modifying any caller code.

## 3. Timeout Semantics
- **Async Tools**: `asyncio.wait_for` cancels the coroutine on timeout.
- **Synchronous Tools**: `asyncio.wait_for` stops awaiting the worker thread result on timeout and returns structured `TOOL_TIMEOUT` failure to `AgentCore`.
- **Worker Thread Behavior**: The underlying Python function running in the worker thread may continue executing until completion, but its return value is permanently discarded. Tool results are never reported as successful after a timeout.

## 4. Cancellation Semantics
- Task cancellation on the main event loop thread (`task.cancel()`) cancels awaiting the `to_thread` worker.
- `AgentCore` handles `CancelledError` cleanly, updates state to `completion_state = "cancelled"`, and exits the loop.

## 5. Thread / Process Limitations
- **Thread Cancellation Limitation**: CPython standard library threads cannot be forcefully terminated from outside. If a synchronous tool performs heavy computation or blocking I/O, cancelling the agent task stops `AgentCore` from waiting, but the worker thread will continue running until the synchronous call returns naturally.
- **OS Process Termination (`TerminalTool`)**: External command execution via `TerminalTool` uses `subprocess.run(..., timeout=TERMINAL_TIMEOUT_SECONDS)` inside the worker thread. When the timeout expires, `subprocess.run` sends `proc.kill()`, providing true OS process-level termination.

## 6. Security & Permission Verification
- Permission verification (`USER_CONFIRMATION`, `PRIVILEGED`, `SecurityManager.is_allowed`), path normalization, path sandbox checks (`is_path_allowed`), secret screening, and logging occur in `ToolExecutor` on the main thread **BEFORE** worker thread dispatch.
- Worker threads cannot bypass permission checks or sandbox constraints.
- Session isolation remains strictly maintained; session parameters and logs are tracked per session ID.

## 7. Performance & Latency Measurements

| Workload / Tool Type | Pre-Isolation Latency | Post-Isolation Latency | Main Event Loop Status |
| :--- | :--- | :--- | :--- |
| Native Async Tool | 0.021s | 0.021s | Unblocked |
| Sync Tool (`file_list`) | 0.005s | 0.006s | **Unblocked** (was blocked) |
| Sync Tool (`file_search`) | 0.045s | 0.046s | **Unblocked** (was blocked) |
| Sync Subprocess (`system_info`) | 0.320s | 0.322s | **Unblocked** (was blocked) |
| Sync Tool Timeout (0.1s limit) | 0.500s (delayed firing) | 0.101s (instant firing) | **Unblocked** |
| Task Cancellation | 0.001s | 0.001s | Unblocked |

## 8. Confirmed Bugs & Fixes Applied
- **Fixed Event Loop Thread Stall**: Synchronous production tools previously ran directly on the event loop thread, preventing `asyncio.wait_for` from interrupting execution until the synchronous function returned. Thread offloading completely resolved event loop blocking.

## 9. Remaining Architectural Limitations
- Python CPython worker threads running synchronous code cannot be forcibly killed upon cancellation or timeout; for hard termination of destructive operations, OS process boundary isolation is required.

## 10. Complete Test Results
- **Synchronous Isolation Suite (`test_sync_tool_isolation.py`):** 11 passed in 1.90s.
- **Full Backend Test Suite:** 103 passed, 4 skipped in 17.51s.
- **Frontend Production Build (`npm run build`):** Built successfully in 548ms (`dist/assets/index-BZN2rgmo.js` 438.82 kB).

