# Saarthi v0.5-rc1 Release Manifest

## System Identity
- **Project**: Saarthi
- **Version**: `v0.5-rc1`
- **Workspace Root**: `E:\Saarthi`
- **Backend Framework**: FastAPI / Python 3.14
- **Frontend Framework**: React 19 / TypeScript / Vite 8 / Tailwind CSS v4
- **Database Engine**: SQLite 3 (`data/database/saarthi.db`)
- **Default LLM Provider**: Ollama / `nemotron-3-nano:4b` (with deterministic Mock Provider fallback)

---

## Directory Architecture

```text
E:\Saarthi
├── backend
│   ├── app
│   │   ├── agent          # Core AgentState machine & smart tool router
│   │   ├── api            # FastAPI REST routes
│   │   ├── config         # Pydantic configuration settings
│   │   ├── memory         # SQLite memory providers, managers, commands
│   │   ├── models         # LLM providers (Ollama / Nemotron 3 Nano)
│   │   ├── security       # Path checks, permission stores, SecurityManager
│   │   ├── tools          # Workstation filesystem & terminal tools
│   │   └── main.py        # Application entrypoint
│   ├── docs               # Comprehensive architecture specifications
│   └── tests              # Full unit, integration & adversarial test suite
├── data                   # Self-contained SQLite database & logs
└── frontend               # React + TypeScript + Vite workspace
```

---

## Operations & Commands

### 1. Launch Backend
```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Run Test Suite
```powershell
.venv\Scripts\python.exe -m pytest backend\tests -v
```

### 3. Build Frontend
```powershell
cd frontend
npm run build
```

---

## Runtime Dependencies & System Requirements
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ (npm v10+)
- Ollama v0.3+ (optional for live local inference; tests use deterministic mocks when offline)
