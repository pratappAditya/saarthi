# Tool Contract Architecture Specification

## Overview
This document formalizes the execution model, input/output schemas, permission levels, validation, timeout, cancellation, error formatting, and registry contracts for all production tools in Saarthi.

---

## Production Tools Inventory

| Tool Name | Permission Level | Risk Classification | Execution Model | Default Timeout |
| :--- | :--- | :--- | :--- | :--- |
| `file_list` | `READ_ONLY` | LOW | Sync (ThreadPool Isolated) | 30 seconds |
| `file_read` | `READ_ONLY` | LOW | Sync (ThreadPool Isolated) | 30 seconds |
| `file_search` | `READ_ONLY` | LOW | Sync (ThreadPool Isolated) | 30 seconds |
| `system_info` | `READ_ONLY` | LOW | Sync (ThreadPool Isolated) | 30 seconds |
| `terminal` | `USER_CONFIRMATION` | HIGH | Sync (Subprocess + Timeout) | 30 seconds |
| `suggest_memory` | `SAFE` | MEDIUM | Async | 10 seconds |

---

## Tool Execution Lifecycle Contract

```
Tool Input
→ Schema Validation
→ Permission Evaluation
→ Task Execution (Async or ThreadPool Sync Isolation)
→ Timeout Enforcement
→ Cancellation Monitoring
→ Result Normalization
→ Persistence to SQLite Memory
→ Model-Visible Result Format
```

---

## Standardized Tool Response Contract

### Success Result Schema
```json
{
  "tool": "file_list",
  "success": true,
  "data": ["file1.txt", "file2.py"],
  "error": null
}
```

### Error Result Schema
```json
{
  "tool": "terminal",
  "success": false,
  "data": null,
  "error": {
    "type": "EXECUTION_ERROR",
    "message": "Command timed out after 30 seconds."
  }
}
```

---

## Registry Duplicate Registration Guarantee

- `ToolRegistry.register(tool)` MUST verify `tool.name` against registered tools.
- Registering a tool with a duplicate `name` MUST raise `ValueError("Duplicate tool registration: A tool with the name '...' is already registered.")`.
- Overwriting existing tool registrations without explicit unregistration is strictly forbidden.
