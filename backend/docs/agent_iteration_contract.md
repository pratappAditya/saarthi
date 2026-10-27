# Agent Iteration Contract Specification

## Overview
This document formalizes the exact 13-step sequence executed during each turn of the Saarthi Agent Loop in `AgentCore._run_agent_loop`.

---

## The 13-Step Iteration Contract

```
 1. Check cancellation
 2. Build model context
 3. Invoke model
 4. Clean model output
 5. Parse tool calls
 6. Validate tool schema
 7. Validate permissions
 8. Execute tools
 9. Persist tool results
10. Append results to model context
11. Decide whether to continue
12. Check max iteration limit
13. Produce final response
```

---

## Detailed Step Contract Specifications

### Step 1: Check Cancellation
- **Behavior**: Inspect `self._canceled_sessions`.
- **Contract**: If `session_id` is flagged as cancelled, update state to `CANCELLED`, persist cancellation message to SQLite memory, log diagnostics, and return cancellation JSON immediately.

### Step 2: Build Model Context
- **Behavior**: Query SQLite session history using `self.memory.get_messages(session_id)`.
- **Contract**: Retrieve memories matching query keywords using `_get_relevant_memories()`. Route relevant tools using `_route_tools()`. Construct system prompt and map chat messages into model history format.

### Step 3: Invoke Model
- **Behavior**: Transition state to `WAITING_MODEL` and invoke `await self.model.generate_response(...)`.
- **Contract**: Execute async HTTP POST call to model provider. Catch connection errors, timeouts, or cancellation signals.

### Step 4: Clean Model Output
- **Behavior**: Run `clean_reasoning(response)` on raw model output string.
- **Contract**: Strip `<think>...</think>`, `<thinking>...</thinking>`, and `"Thinking...done thinking."` blocks. Strip unclosed reasoning tags to prevent internal thought leakage.

### Step 5: Parse Tool Calls
- **Behavior**: Scan cleaned text for opening `[TOOL_CALL]` / `[TOOL_<NAME>]` and closing `[/TOOL_CALL]` / `[/TOOL_<NAME>]` tags.
- **Contract**: Validate tag order, matching tag types, and JSON parseability. If malformed tags are detected, record a `MALFORMED_TOOL_CALL` result into context. Transition state to `WAITING_TOOL`.

### Step 6: Validate Tool Schema
- **Behavior**: Lookup tool in `ToolRegistry`. Execute `validate_arguments(tool.input_schema, tool_args)`.
- **Contract**: Ensure all required fields exist and argument types match schema (`string`, `integer`, `boolean`, `array`, `object`). On failure, record `INVALID_ARGUMENT` or `UNKNOWN_TOOL` result.

### Step 7: Validate Permissions
- **Behavior**: Evaluate tool's `permission_level`.
- **Contract**:
  - `READ_ONLY` & `SAFE`: Automatically approved.
  - `PRIVILEGED`: Rejected immediately with security error.
  - `USER_CONFIRMATION`: Transition state to `WAITING_PERMISSION`, persist `PermissionRequest` to `permission_store`, log request message, and raise `PermissionRequiredException`.

### Step 8: Execute Tools
- **Behavior**: Transition state to `EXECUTING_TOOL` and invoke `ToolExecutor.execute_tool()`.
- **Contract**: Execute sync tools in ThreadPoolExecutor to prevent event loop blocking. Enforce per-tool execution timeouts (e.g. 30s) and monitor cancellation flags.

### Step 9: Persist Tool Results
- **Behavior**: Format `tool_result` message structure.
- **Contract**: Persist result JSON (containing `tool`, `success`, `result`/`error`) to SQLite memory store under `"user"` role.

### Step 10: Append Results to Model Context
- **Behavior**: Update `state.tool_results` list and transition state back to `RUNNING`.
- **Contract**: Make results available for the next iteration step.

### Step 11: Decide Whether to Continue
- **Behavior**: Evaluate whether any valid tool calls were processed in the current turn.
- **Contract**: If tool calls were processed, proceed to next iteration loop. If no tool calls were present, clean tags and return text response.

### Step 12: Check Max Iteration Limit
- **Behavior**: Evaluate `state.iteration >= settings.MAX_AGENT_ITERATIONS` (default: 6).
- **Contract**: If limit is reached, set state to `FAILED`, record error message in memory, write diagnostics log, and return max iterations error response.

### Step 13: Produce Final Response
- **Behavior**: Transition state to `COMPLETED`.
- **Contract**: Save assistant response JSON to SQLite memory store, write structured diagnostic entry to `agent_diagnostics.log`, and return final assistant message string to caller.
