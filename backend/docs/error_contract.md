# Error Contract Architecture Specification

## Overview
This document defines normalized internal error codes, sanitization guidelines, diagnostic reporting, and public API user-facing message mappings.

---

## Internal Error Categories

| Internal Code | Description | User-Facing Sanitized Message |
| :--- | :--- | :--- |
| `MODEL_ERROR` | LLM HTTP/provider error | "I encountered an error communicating with the local AI model." |
| `MODEL_TIMEOUT` | LLM request timed out | "The request timed out while communicating with the local AI model." |
| `MALFORMED_MODEL_OUTPUT` | Output failed tag/JSON parsing | "The local model produced an unexpected or malformed response format." |
| `TOOL_ERROR` | Tool execution exception | "Tool execution error: <sanitized_detail>" |
| `TOOL_TIMEOUT` | Tool exceeded max execution time | "The tool execution timed out." |
| `TOOL_CANCELLED` | Task/tool cancelled by user | "Task execution was cancelled by the user." |
| `PERMISSION_DENIED` | Tool rejected by security policy | "Tool execution was denied due to security policy." |
| `PERMISSION_REQUIRED` | Confirmation needed | "User permission confirmation is required to proceed." |
| `MEMORY_ERROR` | SQLite / memory store failure | "An issue occurred while processing system memory." |
| `SESSION_ERROR` | Session boundary failure | "Session error occurred." |
| `INTERNAL_ERROR` | Unexpected state / core exception | "An internal system error occurred. Please try again." |

---

## Leakage Protection Guarantees

1. **No Stack Traces**: Public HTTP and WebSocket API responses MUST NOT expose internal Python stack traces.
2. **No Secret Leakage**: Errors MUST NOT echo unmasked passwords, environment variables, or private API keys.
3. **No Reasoning Leakage**: Model error handlers MUST clean raw `<think>` blocks before returning messages.
