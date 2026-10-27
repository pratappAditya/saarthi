# Saarthi v0.5 — Personal Agent Core

Saarthi is an extensible, modular personal computer assistant built for Windows. This codebase represents **Saarthi v0.5**, featuring a stateful Agent Loop, smart tool schema routing, an upgraded SQLite-based memory system, a power-sensitive terminal executor, human-in-the-loop permission approvals, and structured JSON diagnostics logging.

---

## Folder Architecture

```text
.
│   .env
│   .env.example
│   .gitignore
│   README.md
│
├── backend
│   │   requirements.txt
│   │
│   ├── app
│   │   ├── agent          # Core Agent loop, AgentState, and smart routing
│   │   ├── api            # REST routers and permission approval handlers
│   │   ├── config         # Pydantic environment configurations
│   │   ├── memory         # SQLite memory providers, managers, and command parsers
│   │   ├── models         # Model providers (Ollama / Nemotron 3 Nano)
│   │   ├── security       # Path checks, permission levels, and stores
│   │   ├── tools          # Secure filesystem & terminal tools implementation
│   │   └── main.py        # FastAPI entrypoint
│   │
│   └── tests              # Pytest verification, mock, and integration suites
│
├── data                   # Self-contained SQLite database, tools.log, and diagnostics
│
├── docs
│   ├── ARCHITECTURE.md    # In-depth architectural flow diagram
│   └── TOOLS.md           # Specifications of registered tools
│
└── frontend               # React + TypeScript + Vite + Tailwind CSS v4 chat interface
```

---

## Core Capabilities

1. **AI Studio UI Integration:** A premium, dark graphite visual workspace with subtle amber/saffron highlights, tabbed navigation, right context panel, and collapsible reasoning logs.
2. **Stateful Agent Loop:** Processes requests using an explicit `AgentState` object tracking execution state, called tools, retrieved memories, errors, and progress over a safe iteration limit (defaulting to 6 steps).
3. **Smart Tool Schema Routing:** Dynamically matches user intent keywords (e.g., list, search, run) to selectively include detailed tool schemas in the prompt context, dramatically saving token context and speed.
4. **Relevance-Scoring Memory Store:** SQLite memory managing categories (`PREFERENCE`, `FACT`, `INSTRUCTION`, `WORKFLOW`, `OTHER`, `USER`, `PROJECT`, `TASK`, `SYSTEM`) using keyword matching, context category boosting, and metadata-based confidence scoring.
5. **Observability and Diagnostics:** Logs structured JSON telemetry for every request to `data/logs/agent_diagnostics.log` (duration, tool execution, model latencies, token estimates, and success metrics).
6. **Safe Workspace Sandbox:** Strictly restricts file operations (`file_list`, `file_read`, `file_search`) to `.` and its descendants. Symlinks and traversals outside are blocked.
7. **Human-in-the-Loop Permissions:** Halts execution when a `USER_CONFIRMATION` tool is requested, presenting permission request cards to the frontend for interactive allow/deny.
8. **Sensitive Credentials Shield:** Automatically scans all memory storage requests, rejecting credentials, tokens, keys, and passwords. Sanitizes log entries to keep parameters secure.

---

## Development Setup

### Prerequisite Checks
Ensure you have the following installed on your machine:
- Python 3.12+
- Node.js (v18+) & npm
- Ollama running locally with `nemotron-3-nano:4b`

### 1. Backend Setup
1. Open a terminal in the root directory:
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate.ps1
   pip install -r backend/requirements.txt
   ```
2. Copy the configuration file:
   ```powershell
   copy .env.example .env
   ```
3. Start the FastAPI server:
   ```powershell
   .venv\Scripts\uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   *Health endpoint:* [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 2. Frontend Setup
1. Navigate to the `frontend` folder:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
2. Open [http://localhost:5173/](http://localhost:5173/) in your web browser.

### 3. Run Tests
Verify backend correctness and regression safety:
```powershell
.venv\Scripts\pytest backend\tests
```

---

## Safety and Auditing Philosophy

Saarthi is built to operate under high-integrity safety boundaries:
- **Sandbox**: No tool can view, list, or search paths outside of `.` or configured roots.
- **Audit Logs**: All tool executions are recorded to `data/logs/tools.log` including timing, parameters, and statuses.
- **Diagnostics**: Model latency, iteration count, and execution metrics are logged for performance monitoring.
- **Confirmations**: High-risk actions require user approval before the script executes, preventing prompt injection bypasses.
- **Privilege Blocking**: Destructive commands are classified as privileged and rejected prior to dispatch.
- **Secret Shield**: Credentials and keys are blocked from being stored in permanent memory or printed to execution logs.
