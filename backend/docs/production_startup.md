# Saarthi Production Startup & Verification Guide

## Overview
This document specifies the clean startup sequence, environment checks, port bindings, database initialization, and service health checks for Saarthi.

---

## Clean Startup Sequence

### 1. Environment & Process Check
- Ensure no orphaned Python or Node processes occupy backend (port `8000`) or frontend dev ports.
- Verify environment variables in `.env` (`MODEL_PROVIDER`, `OLLAMA_BASE_URL`, `DATABASE_PATH`, `SAARTHI_DATA_DIR`).

### 2. Ollama Service Initialization (Optional / Local Model Mode)
```bash
ollama --version
ollama list
```
- If running in Ollama mode, verify that the configured model (e.g. `qwen2.5-coder:7b-instruct-q4_K_M`) is available in local model store.
- If Ollama is offline, Saarthi gracefully operates in fallback / mock mode without crashing backend endpoints.

### 3. Backend Service Launch
```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
- Database connection initialized cleanly (`data/database/saarthi.db`).
- SQLite migrations / table schemas verified automatically on startup.
- In-memory registries (`ToolRegistry`, `PermissionStore`, `_active_tasks`, `_canceled_sessions`) start in clean empty state.

### 4. Frontend Service Launch
```bash
cd frontend
npm run build
npm run dev
```

---

## Health & Status Endpoints

- **GET `/health`**: Returns `{"status": "ok", "service": "saarthi"}`.
- **GET `/status`**: Returns backend status, model provider, Ollama connection status, and model availability.
- **GET `/tools`**: Returns compact tool registry definitions.
