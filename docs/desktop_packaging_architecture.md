# Saarthi Desktop Packaging Architecture

## Overview
This document specifies the Windows desktop packaging architecture, process lifecycle graph, and service orchestration strategy for Saarthi.

---

## 1. Selected Architecture: Python Native Lifecycle Manager + Embedded WebView / FastAPI SPA
- **Frontend Architecture**: React + TypeScript + Vite (`frontend/dist` static assets served directly via FastAPI `StaticFiles`).
- **Backend Architecture**: Python 3.14 + FastAPI + Uvicorn (`http://127.0.0.1:8000`).
- **LLM Runtime Architecture**: Local Ollama v0.32.8 daemon (`http://127.0.0.1:11434`, model `nemotron-3-nano:4b`).
- **Database Architecture**: SQLite 3 (`E:\Saarthi\data\database\saarthi.db`).

---

## 2. Process Lifecycle Graph

```
[Saarthi Desktop Launcher]
     │
     ├── 1. Check & Start Ollama Daemon (OLLAMA_MODELS=E:\Saarthi\models)
     ├── 2. Verify nemotron-3-nano:4b Model Availability
     ├── 3. Check & Start FastAPI Uvicorn Backend (Port 8000)
     ├── 4. Mount Frontend Static Assets (frontend/dist)
     └── 5. Open Desktop Window / Browser App Canvas
```

---

## 3. Data & Directory Isolation Strategy
- **Application Binaries**: `{autopf}\Saarthi` (Executable launcher, python runtime environment, backend code, frontend build).
- **User Data**: `E:\Saarthi\data` (SQLite database `saarthi.db`, memory tables, chat history, diagnostic logs).
- **Model Storage**: `E:\Saarthi\models` (GGUF weights and manifests).
- **Workspace Sandbox**: `E:\Saarthi` (Sandboxed project workspace).

*Invariant: Reinstalling or upgrading Saarthi application binaries MUST NEVER modify or delete `E:\Saarthi\data` or `E:\Saarthi\models`.*
