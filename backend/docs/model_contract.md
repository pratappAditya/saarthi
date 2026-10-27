# Model Provider Contract Specification

## Overview
This document formalizes the HTTP communication, reasoning cleanup, tool call parsing, error handling, and timeout behavior for the Ollama model provider (`NemotronProvider`).

---

## Model Request Pipeline Contract

```
Model Request
→ HTTP POST (/api/chat)
→ Response JSON Inspection
→ Reasoning Cleanup (clean_reasoning)
→ Tool-Call Parsing ([TOOL_CALL] / [TOOL_<NAME>])
→ Malformed Output Handling
→ Timeout & Error Normalization
→ Final Text / Tool Dispatch
```

---

## Error Handling Specifications

1. **Connection Failures**: If Ollama service is offline (`httpx.ConnectError`), raise `ConnectionError` with clear diagnostic message ("Cannot connect to Ollama service...").
2. **Model Not Found**: HTTP 404 response raises `RuntimeError` prompting the user to pull the missing model (`ollama pull <model>`).
3. **HTTP Status Errors**: Non-200 HTTP responses extract the error message from response JSON and raise `RuntimeError`.
4. **Malformed JSON**: Invalid HTTP response bodies raise `RuntimeError("Failed to parse JSON response from local model...")`.
5. **Empty Model Output**: If `message.content` and `message.thinking` are empty, raise `RuntimeError("Received empty response from local model.")`.
6. **Reasoning Leakage**: Raw `<think>`, `<thinking>`, or `"Thinking...done thinking."` text MUST be stripped before returning output to caller.
7. **Model Timeout**: HTTP request uses a generous timeout (180s connect/read). Timeouts raise `TimeoutError`.

---

## Unit Testing Requirement
- Unit tests MUST NOT require a running Ollama server.
- Tests MUST use deterministic mocks (`RecordingMockModelProvider` or `unittest.mock.patch`).
- Live Ollama tests must automatically skip when Ollama is offline.
