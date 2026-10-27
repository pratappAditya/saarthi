# Saarthi Tool System Reference Documentation

This document describes the registered tools, their capabilities, permission requirements, and risk levels.

## Tool Registry Matrix

| Tool        | Permission        | Risk | Status     | Input Schema | Output Schema |
| ----------- | ----------------- | ---- | ---------- | ------------ | ------------- |
| `system_info` | `READ_ONLY`         | `LOW`  | Enabled    | `{}` | Returns key-value specs for CPU, OS, RAM, GPU, versions, WSL, etc. |
| `file_list`   | `READ_ONLY`         | `LOW`  | Enabled    | `{path: string, recursive: boolean, max_items: number}` | Returns list of names, sizes, directory indicators. |
| `file_read`   | `READ_ONLY`         | `LOW`  | Enabled    | `{path: string}` | Returns full file content text. |
| `file_search` | `READ_ONLY`         | `LOW`  | Enabled    | `{query: string, path: string, root_path: string, max_results: number, file_pattern: string}` | Returns list of search matches (filename/content). |
| `terminal`    | `USER_CONFIRMATION` | `HIGH` | Restricted | `{command: string}` | Returns stdout, stderr, and exit_code. |

---

## Detailed Tool Specifications

### 1. `system_info`
- **Purpose**: Collect specs about the host computer (OS, CPU cores, RAM size, GPU name, workspace disk space, software versions, and WSL status).
- **Execution Level**: `READ_ONLY` - does not modify system settings.

### 2. `file_list`
- **Purpose**: List directory contents in the configured allowed workspace.
- **Constraints**:
  - Rejects any paths pointing outside the workspace sandbox (`E:\Saarthi` by default).
  - Handles traversal (`..`), symbolic links, junctions, and absolute paths safely.
  - Recursion ignores system and package folders (e.g. `node_modules`, `.venv`, `.git`) to avoid system freezes.

### 3. `file_read`
- **Purpose**: Retrieve full text of a file inside the sandbox.
- **Constraints**:
  - Rejects paths outside the sandbox.
  - Refuses to load files larger than **512 KB** to prevent memory bloat.
  - Automatically screens and blocks binary files (checks for null bytes `\x00` and encoding errors).

### 4. `file_search`
- **Purpose**: Find files or file content matching a string query.
- **Constraints**:
  - Strictly restricted to paths within the workspace sandbox.
  - Screens out binary files.
  - Limits scanning to a maximum of 1,000 files to maintain responsive behavior.
  - Supports glob-like wildcard file pattern filters (e.g. `*.py` or `*.json`).

### 5. `terminal`
- **Purpose**: Runs PowerShell commands in the workspace context.
- **Strict Security Measures**:
  - **PowerShell only** execution.
  - Working directory locked to the sandbox root (`E:\Saarthi`).
  - Strict command timeout (default is **30 seconds**).
  - Truncates standard output/error length to prevent context window saturation.
  - **Chaining Block**: Commands containing chaining characters (`;` or `&`) or multiple lines are blocked.
  - **Interactive Block**: Rejects background processes and commands requiring human prompts.
  - **Destructive Command Rejection**: Any command matching destructive keywords (e.g. `Remove-Item`, `del`, `format`, `shutdown`, `reg`, `net`) is classified as `PRIVILEGED` and blocked immediately.
