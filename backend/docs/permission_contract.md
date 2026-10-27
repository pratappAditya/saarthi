# Permission Contract Architecture Specification

## Overview
This document defines the security evaluation flow, permission levels, approval storage, and non-reusability guarantees for tool execution.

---

## Safety Level Hierarchy

```
READ_ONLY  (Level 0: Path boundary checked, auto-approved)
SAFE       (Level 1: System/Memory read/suggest, auto-approved)
USER_CONFIRMATION (Level 2: Requires explicit user approval per request)
PRIVILEGED (Level 3: Administrative / dangerous, ALWAYS REJECTED)
```

---

## Security Request Lifecycle Contract

```
User Chat Request
→ Tool Selection & Routing
→ Permission Evaluation (SecurityManager)
→ IF USER_CONFIRMATION:
    1. Create PermissionRequest in PermissionStore
    2. Persist request card to Session Memory
    3. Raise PermissionRequiredException
    4. HTTP Response returns status="pending_confirmation"
→ User Approval / Denial API Call:
    1. Look up request_id in PermissionStore
    2. Verify status == "pending" (Reject if approved/denied/stale)
    3. Mark status = "approved" / "denied"
    4. Resume loop with exact bound tool & arguments
```

---

## Strict Non-Reusability Guarantee

- Approval is strictly bound to: `session_id`, `request_id`, `tool_name`, `arguments`.
- A `PermissionRequest` transitions from `pending` -> `approved` or `denied` exactly ONCE.
- Re-submitting an already approved or denied `request_id` MUST return HTTP 400 Bad Request ("Permission request is already approved/denied").
- An approved `PermissionRequest` cannot be reused for a different tool name, different arguments, or across different sessions.
