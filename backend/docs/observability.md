# Observability & Logging Architecture Specification

## Overview
This document specifies structured diagnostic logging, telemetry schemas, privacy rules, and secret redaction policies.

---

## Structured Diagnostic Schema

Diagnostics are appended as structured JSON to `data/logs/agent_diagnostics.log`:

```json
{
  "request_id": "req-a1b2c3d4",
  "session_id": "default_session",
  "model": "qwen2.5-coder:7b-instruct-q4_K_M",
  "prompt_token_estimate": 142,
  "selected_tools": ["file_list"],
  "tool_execution_duration": 0.042,
  "model_duration": 1.23,
  "total_duration": 1.35,
  "iteration_count": 1,
  "error_status": false
}
```

---

## Privacy & Redaction Rules

1. **No `<think>` Content**: Raw model reasoning trace (`<think>...</think>`) MUST NOT be written to diagnostics logs or persistent chat histories.
2. **No Secret Arguments**: Sensitive tool arguments (e.g. passwords, secrets) MUST NOT be logged in plaintext.
3. **Restricted User Data**: Unrestricted raw user prompt strings are excluded from diagnostic logs; only token estimates, tool names, timing, and error booleans are recorded.
4. **Log Path Isolation**: Log files are stored strictly under `data/logs/`.
