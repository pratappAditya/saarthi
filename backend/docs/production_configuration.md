# Saarthi Production Configuration Audit

## Overview
This document audits all configuration settings and default parameters used by Saarthi in production.

---

## Production Configuration Matrix

| Config Key | Production Default | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | FastAPI HTTP listener port |
| `HOST` | `"127.0.0.1"` | Loopback interface binding (local workstation only) |
| `APP_NAME` | `"Saarthi"` | System application identifier |
| `MODEL_PROVIDER` | `"ollama"` (or `"mock"` fallback) | LLM provider backend |
| `MODEL_NAME` | `"nemotron-3-nano:4b"` (or env override) | Target LLM model name |
| `OLLAMA_BASE_URL` | `"http://127.0.0.1:11434"` | Ollama service endpoint |
| `MODEL_TEMPERATURE` | `0.7` | Inference temperature setting |
| `MODEL_MAX_TOKENS` | `512` | Max generated tokens per request |
| `OLLAMA_THINK` | `False` | Thinking trace toggle |
| `DATABASE_PATH` | `"E:/Saarthi/data/database/saarthi.db"` | SQLite database file location |
| `SAARTHI_DATA_DIR` | `"E:/Saarthi/data"` | Data directory for logs and storage |
| `TOOL_ENABLED` | `True` | Global tool system toggle |
| `TOOL_ROOT_PATH` | `"E:/Saarthi"` | Workspace root path for filesystem tools |
| `MAX_TOOL_ITERATIONS` | `8` | Maximum tool execution loop cap |
| `MAX_TOOL_OUTPUT_CHARS` | `12000` | Maximum character length for tool output |
| `TERMINAL_TIMEOUT_SECONDS` | `30` | Per-command terminal execution timeout |
| `TOOL_EXECUTION_TIMEOUT` | `30.0` | Global per-tool async/sync timeout |
| `MAX_AGENT_ITERATIONS` | `6` | Agent loop iteration limit |
| `MAX_HISTORY_MESSAGES` | `8` | Context window history message count |
| `MAX_HISTORY_CHARS` | `6000` | Context window history character cap |
| `MAX_MEMORY_RESULTS` | `5` | Candidate memories retrieved per turn |
| `MAX_MEMORY_CONTEXT_CHARS` | `3000` | Max characters for injected memory context |
| `TRUSTED_PATHS` | `"E:\\Saarthi;%USERPROFILE%\\..."` | Workstation paths allowed for file access |

---

## Security Verification
- **Host Binding**: Host is bound to `127.0.0.1` (loopback only) to prevent unauthorized remote network exposure.
- **No Cloud API Keys**: Configuration relies entirely on local models and local SQLite storage.
