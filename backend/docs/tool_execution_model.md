# Saarthi Production Tools — Execution Model Audit

This document classifies every production tool registered in Saarthi according to its execution model and runtime behavior.

## Classification Taxonomy

- **Category A: Native Async**: Tool logic uses native Python `async`/`await` primitives and async I/O. Does not block the asyncio event loop thread.
- **Category B: Synchronous but guaranteed fast**: Synchronous operation with strict upper bounds on work and execution time.
- **Category C: Potentially blocking**: Synchronous operation performing disk I/O, directory traversal, or heavy string matching that can stall the asyncio event loop thread if run synchronously on the main thread.
- **Category D: Subprocess-based**: Spawns external processes (`powershell.exe`, `wmic`, `git`, `node`, `docker`, `wsl`). Subject to OS process management and process timeouts.
- **Category E: CPU-intensive**: Performs compute-heavy string search, parsing, or matching in Python.

---

## Tool Execution Matrix

| Tool Name | Class Name | Category | Primary Operations | Execution Strategy |
| :--- | :--- | :--- | :--- | :--- |
| `file_list` | `FileListTool` | **Category C** | `os.scandir`, `os.walk` directory traversal | Offloaded via `asyncio.to_thread()` |
| `file_read` | `FileReadTool` | **Category B & C** | File read capped at 512KB, UTF-8 check | Offloaded via `asyncio.to_thread()` |
| `file_search` | `FileSearchTool` | **Category C & E** | Directory walk, file scanning (up to 1,000 files), text search | Offloaded via `asyncio.to_thread()` |
| `system_info` | `SystemInfoTool` | **Category C & D** | `subprocess.check_output` (`wmic`, `node`, `git`, `docker`, `wsl`) | Offloaded via `asyncio.to_thread()` |
| `terminal` | `TerminalTool` | **Category D & C** | `subprocess.run` (`powershell.exe` with `timeout=30s`) | Offloaded via `asyncio.to_thread()` with OS process timeout |
| `suggest_memory` | `SuggestMemoryTool` | **Category B** | In-memory/SQLite memory request creation | Offloaded via `asyncio.to_thread()` |

---

## Detailed Tool Analysis

### 1. `file_list` (`FileListTool`)
- **Category**: C (Potentially blocking)
- **Rationale**: `FileListTool` uses `os.scandir` for single-level listing or `os.walk` for recursive listing. Traversing deeply nested directory trees or slow disk mounts (e.g. network drives or HDDs) will block the thread executing the loop.
- **Isolation Model**: Wrapped in `asyncio.to_thread()` so filesystem scanning occurs in a worker thread.

### 2. `file_read` (`FileReadTool`)
- **Category**: B (Guaranteed fast) & C (Potentially blocking for I/O)
- **Rationale**: `FileReadTool` enforces a 512KB size limit and binary null-byte check. While reads under 512KB on local SSDs execute in under 1ms, disk I/O remains a blocking OS operation.
- **Isolation Model**: Offloaded to worker thread via `asyncio.to_thread()`.

### 3. `file_search` (`FileSearchTool`)
- **Category**: C (Potentially blocking) & E (CPU-intensive)
- **Rationale**: `FileSearchTool` traverses directory trees (`os.walk`), opening and searching up to 1,000 text files (<128KB each) line-by-line. This combines filesystem I/O with CPU-bound Python string matching.
- **Isolation Model**: Offloaded to worker thread via `asyncio.to_thread()`.

### 4. `system_info` (`SystemInfoTool`)
- **Category**: C (Potentially blocking) & D (Subprocess-based)
- **Rationale**: `SystemInfoTool` executes multiple blocking `subprocess.check_output` calls to WMIC, Node.js, Git, Docker, and WSL. On Windows systems where WSL or Docker daemon is unresponsive, synchronous invocation can block for several seconds.
- **Isolation Model**: Offloaded to worker thread via `asyncio.to_thread()`.

### 5. `terminal` (`TerminalTool`)
- **Category**: D (Subprocess-based) & C (Potentially blocking)
- **Rationale**: Executes arbitrary user-approved PowerShell commands using `subprocess.run(..., timeout=TERMINAL_TIMEOUT_SECONDS)`.
- **Isolation Model**:
  - Main thread isolation: Executed in worker thread via `asyncio.to_thread()` so the main asyncio event loop is not blocked for up to 30 seconds.
  - Process isolation: `subprocess.run(..., timeout=30)` provides real OS process termination via `proc.kill()` when the command times out.

### 6. `suggest_memory` (`SuggestMemoryTool`)
- **Category**: B (Synchronous but guaranteed fast)
- **Rationale**: Creates a pending memory request in SQLite/in-memory store and raises `MemoryApprovalRequiredException`.
- **Isolation Model**: Offloaded to worker thread via `asyncio.to_thread()`.

---

## Architectural Isolation Summary

1. **Event Loop Responsiveness**: Synchronous/blocking tools run on `concurrent.futures.ThreadPoolExecutor` worker threads via `asyncio.to_thread()`, keeping the `AgentCore` main thread loop 100% unblocked and responsive to other coroutines, timers, and cancellation requests.
2. **Timeout Semantics**: `asyncio.wait_for` on the main loop thread controls how long `AgentCore` waits. If a sync tool times out, `ToolExecutor` stops waiting and returns `TOOL_TIMEOUT`. The worker thread running the Python call may continue until completion, but its result is permanently discarded.
3. **Subprocess Termination**: For external commands, `TerminalTool` uses OS process-level timeout (`subprocess.run(timeout=...)`) to ensure process termination.
