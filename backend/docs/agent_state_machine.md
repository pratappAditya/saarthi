# Agent State Machine Architecture Specification

## Overview

The Saarthi Agent Runtime is governed by an explicit, deterministic state machine (`AgentState`). This document defines the lifecycle, valid transitions, invariants, and operational behavior across all execution states.

---

## State Definitions

### 1. IDLE
- **Entry Condition**: Session initialized or previous turn finished.
- **Allowed Transitions**: `RUNNING`, `CANCELLED`
- **Exit Condition**: User dispatches a new message, or cancellation request is issued.
- **Persisted State**: Session history in SQLite DB.
- **User-Visible Behavior**: Ready for user input in chat UI.
- **Cancellation Behavior**: Immediate no-op / marked cancelled.
- **Timeout Behavior**: N/A (passive state).
- **Invalid Transitions**: `WAITING_MODEL`, `WAITING_PERMISSION`, `EXECUTING_TOOL`, `WAITING_TOOL`, `COMPLETED`, `FAILED`, `TIMEOUT`.

### 2. RUNNING
- **Entry Condition**: User message received or execution resumed after permission/memory approval.
- **Allowed Transitions**: `WAITING_MODEL`, `CANCELLED`, `FAILED`
- **Exit Condition**: Agent loop routes request or initiates model call.
- **Persisted State**: User message appended to memory store.
- **User-Visible Behavior**: Processing indicator active.
- **Cancellation Behavior**: Clears task execution, transitions to `CANCELLED`.
- **Timeout Behavior**: N/A.
- **Invalid Transitions**: `IDLE`, `WAITING_PERMISSION`, `EXECUTING_TOOL`, `WAITING_TOOL`, `COMPLETED`.

### 3. WAITING_MODEL
- **Entry Condition**: Prompt, system prompt, and context sent to Ollama/LLM provider.
- **Allowed Transitions**: `RUNNING` (tool call parsed), `COMPLETED` (final text response), `WAITING_PERMISSION` (tool requires confirmation), `WAITING_TOOL` (tool execution starting), `FAILED` (model error), `TIMEOUT` (inference timeout), `CANCELLED` (user cancelled during model call).
- **Exit Condition**: Model returns valid response, times out, or receives cancellation signal.
- **Persisted State**: In-flight HTTP request.
- **User-Visible Behavior**: "Thinking..." or assistant generating indicator.
- **Cancellation Behavior**: Cancels HTTP client request, transitions to `CANCELLED`.
- **Timeout Behavior**: 180s HTTP timeout triggers `TIMEOUT` -> `FAILED` transition with `MODEL_TIMEOUT`.
- **Invalid Transitions**: `IDLE`, `EXECUTING_TOOL`.

### 4. WAITING_PERMISSION
- **Entry Condition**: Model emitted a tool call requiring `USER_CONFIRMATION` permission level.
- **Allowed Transitions**: `RUNNING` (user approved/denied via API), `CANCELLED` (session cancelled).
- **Exit Condition**: Approval or Denial API request received, or session cancelled.
- **Persisted State**: `PermissionRequest` stored in `PermissionStore` with status `pending`. `permission_request` message logged to session memory.
- **User-Visible Behavior**: Interactive permission confirmation card presented to user.
- **Cancellation Behavior**: `PermissionRequest` marked stale/denied, transition to `CANCELLED`.
- **Timeout Behavior**: Indefinite wait until user acts or session is cancelled.
- **Invalid Transitions**: `IDLE`, `WAITING_MODEL`, `EXECUTING_TOOL`, `WAITING_TOOL`, `COMPLETED`, `FAILED`, `TIMEOUT`.

### 5. WAITING_TOOL
- **Entry Condition**: Validated tool call prepared for invocation.
- **Allowed Transitions**: `EXECUTING_TOOL`, `CANCELLED`, `FAILED`
- **Exit Condition**: Tool execution task spawned.
- **Persisted State**: `tool_call` stored in session memory.
- **User-Visible Behavior**: Tool invocation status card displayed.
- **Cancellation Behavior**: Prevents execution launch, transitions to `CANCELLED`.
- **Timeout Behavior**: N/A.
- **Invalid Transitions**: `IDLE`, `WAITING_MODEL`, `WAITING_PERMISSION`, `COMPLETED`.

### 6. EXECUTING_TOOL
- **Entry Condition**: `ToolExecutor.execute_tool` called (sync tools isolated in ThreadPool, async tools awaited).
- **Allowed Transitions**: `RUNNING` (tool completed, loop continues), `FAILED` (uncaught tool exception), `TIMEOUT` (tool execution exceeded per-tool timeout), `CANCELLED` (user cancelled during execution).
- **Exit Condition**: Tool function returns result dict or raises exception/timeout/cancellation.
- **Persisted State**: Active tool process/task.
- **User-Visible Behavior**: Tool executing spinner with tool name and arguments.
- **Cancellation Behavior**: Synchronous sub-process or thread terminated/cancelled, `TOOL_CANCELLED` result recorded, state transitions to `CANCELLED`.
- **Timeout Behavior**: Per-tool timeout (e.g., 30s) enforced, `TOOL_TIMEOUT` recorded, state transitions to `TIMEOUT` -> `RUNNING` or `FAILED`.
- **Invalid Transitions**: `IDLE`, `WAITING_MODEL`, `WAITING_PERMISSION`, `COMPLETED`.

### 7. COMPLETED
- **Entry Condition**: Model returned final textual response without tool calls.
- **Allowed Transitions**: `IDLE` (reset for next user turn).
- **Exit Condition**: Cycle ended.
- **Persisted State**: Final assistant text message persisted to SQLite session history. Diagnostics written to `agent_diagnostics.log`.
- **User-Visible Behavior**: Complete markdown response rendered.
- **Cancellation Behavior**: N/A (already finished).
- **Timeout Behavior**: N/A.
- **Invalid Transitions**: All except transition to `IDLE`.

### 8. FAILED
- **Entry Condition**: Model exception, unrecoverable tool exception, or `MAX_AGENT_ITERATIONS` reached.
- **Allowed Transitions**: `IDLE` (reset for next turn).
- **Exit Condition**: Error message returned to user.
- **Persisted State**: Error message recorded in SQLite session history. Diagnostics written to `agent_diagnostics.log`.
- **User-Visible Behavior**: Sanitized error message rendered.
- **Cancellation Behavior**: N/A.
- **Timeout Behavior**: N/A.
- **Invalid Transitions**: `RUNNING`, `WAITING_MODEL`, `WAITING_PERMISSION`, `EXECUTING_TOOL`, `COMPLETED`.

### 9. CANCELLED
- **Entry Condition**: `cancel_session` invoked or `asyncio.CancelledError` caught during any active phase.
- **Allowed Transitions**: `IDLE` (reset for next turn).
- **Exit Condition**: Cancellation response returned to user.
- **Persisted State**: Cancellation message saved to session memory. Session active tasks cleared.
- **User-Visible Behavior**: "Task execution was cancelled by the user." card rendered.
- **Cancellation Behavior**: Idempotent (subsequent cancellations return True/False safely without side-effects).
- **Timeout Behavior**: N/A.
- **Invalid Transitions**: `RUNNING`, `WAITING_MODEL`, `EXECUTING_TOOL`, `COMPLETED`, `FAILED`.

### 10. TIMEOUT
- **Entry Condition**: Model generation or tool execution exceeds configured timeout limit.
- **Allowed Transitions**: `RUNNING` (recoverable tool timeout fed back to model), `FAILED` (unrecoverable timeout).
- **Exit Condition**: Error result returned to model context or agent loop terminates.
- **Persisted State**: Tool timeout error recorded in session history.
- **User-Visible Behavior**: Warning/Error message in execution card.
- **Cancellation Behavior**: Immediate transition to `CANCELLED`.
- **Timeout Behavior**: N/A.
- **Invalid Transitions**: `IDLE`, `WAITING_PERMISSION`, `COMPLETED`.

---

## State Transition Table

| Current State | Event / Trigger | Next State | Action / Side Effect |
| :--- | :--- | :--- | :--- |
| `IDLE` | User sends message | `RUNNING` | Persist user message, start timer |
| `RUNNING` | History & Prompt built | `WAITING_MODEL` | Send HTTP payload to Ollama |
| `RUNNING` | Session cancelled | `CANCELLED` | Clear active task, persist cancellation msg |
| `WAITING_MODEL` | Model returns final text | `COMPLETED` | Persist text response, write diagnostics |
| `WAITING_MODEL` | Model calls `USER_CONFIRMATION` tool | `WAITING_PERMISSION` | Create `PermissionRequest`, persist request msg |
| `WAITING_MODEL` | Model calls `SAFE` / confirmed tool | `WAITING_TOOL` | Log tool call msg |
| `WAITING_MODEL` | Model HTTP request times out | `TIMEOUT` | Log `MODEL_TIMEOUT`, transition to `FAILED` |
| `WAITING_MODEL` | Model exception / connection error | `FAILED` | Persist model error msg, write diagnostics |
| `WAITING_MODEL` | Session cancelled | `CANCELLED` | Abort HTTP request, persist cancellation msg |
| `WAITING_PERMISSION` | User approves permission | `RUNNING` | Mark request approved, execute tool turn |
| `WAITING_PERMISSION` | User denies permission | `RUNNING` | Mark request denied, feed denial to model |
| `WAITING_PERMISSION` | Session cancelled | `CANCELLED` | Mark request cancelled, persist cancellation msg |
| `WAITING_TOOL` | Tool executor invoked | `EXECUTING_TOOL` | Pass tool args to `ToolExecutor` |
| `EXECUTING_TOOL` | Tool completes successfully | `RUNNING` | Persist `tool_result`, increment iteration |
| `EXECUTING_TOOL` | Tool execution times out | `TIMEOUT` | Format `TOOL_TIMEOUT` error result |
| `EXECUTING_TOOL` | Tool raises exception | `FAILED` / `RUNNING` | Format `TOOL_ERROR` result into context |
| `EXECUTING_TOOL` | Session cancelled | `CANCELLED` | Abort tool thread/task, persist cancellation msg |
| `TIMEOUT` | Recoverable tool timeout | `RUNNING` | Feed timeout result to model to attempt recover |
| `TIMEOUT` | Unrecoverable model/tool timeout | `FAILED` | Persist error message, write diagnostics |
| `COMPLETED` | Reset turn | `IDLE` | Ready for next input |
| `FAILED` | Reset turn | `IDLE` | Ready for next input |
| `CANCELLED` | Reset turn | `IDLE` | Ready for next input |

---

## State Transition Rules & Invariants

1. **No Silent Transitions**: Every state transition MUST update `state.current_state`, refresh `updated_at`, and record the transition in `state.state_history`.
2. **Invalid Transition Protection**: Attempting an illegal transition (e.g., `IDLE` -> `EXECUTING_TOOL`) raises `InvalidStateTransitionError`.
3. **Session Binding**: `AgentState` is strictly bound to a single `session_id` and `request_id`. State is never shared across sessions.
4. **Idempotency**: Retrying a transition to the current state is a no-op and will not execute side-effects twice.
