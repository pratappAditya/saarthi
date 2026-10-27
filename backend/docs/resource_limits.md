# Saarthi Resource Limits Specification

## Overview
This document specifies all operational resource limits and caps enforced by the Saarthi runtime.

---

## Enforced System Limits

| Boundary Area | Parameter | Config / Constant | Default Limit |
| :--- | :--- | :--- | :--- |
| **Agent Iterations** | Max iterations per user turn | `MAX_AGENT_ITERATIONS` | 6 iterations |
| **History Messages** | Max messages sent to model context | `MAX_HISTORY_MESSAGES` | 10 messages |
| **History Characters** | Max total characters in history | `MAX_HISTORY_CHARS` | 12,000 characters |
| **Memory Results** | Max top memory candidates retrieved | `MAX_MEMORY_RESULTS` | 5 memories |
| **Memory Context Chars** | Max characters for injected memories | `MAX_MEMORY_CONTEXT_CHARS` | 2,000 characters |
| **Tool Description Chars** | Max schema description length | `MAX_TOOL_DESCRIPTION_CHARS` | 1,500 characters |
| **Tool Execution Timeout** | Per-tool execution timeout | `ToolExecutor.timeout` | 30 seconds |
| **Model HTTP Timeout** | Ollama HTTP client timeout | `httpx.Timeout` | 180 seconds |
| **File Read Slice Limit** | Max file size read per turn | `FileReadTool` | 500,000 bytes |
| **Directory Search Cap** | Max file entries returned | `FileListTool` | 200 entries |
