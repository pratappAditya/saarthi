# Session Contract Architecture Specification

## Overview
This document formalizes multi-session concurrency and state isolation boundaries in Saarthi.

---

## Session Isolation Guarantees

Every session (identified by `session_id`) is strictly isolated from all other concurrent sessions.

### Isolated Session Boundaries:
1. **Chat History**: Messages stored in SQLite database are strictly filtered by `session_id`.
2. **Memory Context**: Memory retrieval and updates scope to the active session and active project boundary.
3. **Permissions**: `PermissionRequest` instances in `PermissionStore` are bound to `session_id`. Approvals in Session A cannot approve tools in Session B.
4. **Cancellation Flags**: `cancel_session(session_id)` populates `_canceled_sessions` set for that specific `session_id`. Cancelling Session A never affects Session B.
5. **Active Tasks**: `_active_tasks` dictionary maps `session_id` to its running `asyncio.Task`.
6. **Tool Results**: In-memory `tool_results` and `called_tools` lists belong strictly to the individual `AgentState` instance.

---

## Concurrent Multi-Session Test Contract
- The test suite MUST execute multi-session concurrent workloads using `asyncio.gather()`.
- Session A and Session B running simultaneously MUST maintain complete isolation without data race, crosstalk, or shared mutable state contamination.
