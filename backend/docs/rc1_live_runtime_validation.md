# Saarthi RC1 — Live Runtime Validation

## 1. Environment
- **OS**: Windows 10.0.26220
- **Python**: Python 3.14.6 (`.venv`)
- **Node**: Node.js v20+ / npm 10+
- **Ollama**: Ollama v0.32.8
- **NVIDIA Driver**: 561.09
- **CUDA Version**: 12.6
- **GPU**: NVIDIA GeForce GTX 1650 Ti (4096 MiB VRAM)
- **VRAM Allocated**: 2567 MiB / 4096 MiB (Offload split: `30%/70% CPU/GPU`)
- **Saarthi Version**: `v0.5-rc1`

---

## 2. Service Status
- **Ollama Service**: ONLINE (`http://127.0.0.1:11434`, model: `nemotron-3-nano:4b`)
- **FastAPI Backend**: ONLINE (`http://127.0.0.1:8000/api/status`, `backend_status: online`)
- **Vite / Frontend**: ONLINE (`http://127.0.0.1:5173/`, title: `Saarthi — Local AI Command Center`)
- **SQLite Engine**: ONLINE (`data/database/saarthi.db`, tables: `memories`, `chat_history`)

---

## 3. Gate Results

| Gate | Test | Result | Evidence | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0** | Pre-Flight Environment | **PASS** | Roots exist (`backend`, `frontend`, `data`, `models`, `.env`); zero active legacy names (`Cheeku`/`untitled`). | Clean pre-flight audit. |
| **Gate 1** | Start & Verify Ollama | **PASS** | `ollama --version` (0.32.8); `nemotron-3-nano:4b` loaded; generate response: `"The capital of India is New Delhi."`. | Cold load: 7.47s, prompt eval: 0.93s, eval: 2.77s. |
| **Gate 2** | GPU / Model Runtime | **PASS** | `ollama ps` reports `30%/70% CPU/GPU` offload; `nvidia-smi` shows PID 17324 (`llama-server.exe`) consuming 2567 MiB VRAM. | Live GPU evidence verified. |
| **Gate 3** | Start Saarthi Backend | **PASS** | Uvicorn running on port 8000; `/api/status` returns `backend_status: online`, `ollama_connected: true`. | Port 8000 single process. |
| **Gate 4** | Start Saarthi Frontend | **PASS** | `npm run build` succeeds (348ms); `npm run dev` serves `<title>Saarthi — Local AI Command Center</title>` on port 5173. | Zero build/runtime errors. |
| **Gate 5** | Real Chat Workflow | **PASS** | 3-turn multi-dialogue (`Hello`, `Capital of India`, `Short explanation`). Coherent responses returned; zero raw tags or reasoning leaked. | Warm turn latencies: 3.1s - 9.8s. |
| **Gate 6** | Real Multi-Turn Memory | **PASS** | User stated `"favorite test word is ORBITAL"`; asked recall turn -> model returned `"Your favorite test word is **ORBITAL**."`. | 100% memory recall accuracy. |
| **Gate 7** | Real Tool Execution | **PASS** | Executed `file_list` tool -> workspace listing returned; attempted out-of-sandbox `C:/Windows/.../hosts` -> blocked safely. | Sandbox boundary strictly enforced. |
| **Gate 8** | Permission Approval / Denial | **PASS** | `terminal` tool prompt -> pending request `req-70586858` generated; denied via `/api/permissions/req-70586858/deny` -> tool did NOT run; replay attempt returned 400. | Security & replay protection verified. |
| **Gate 9** | Cancellation Safety | **PASS** | `POST /api/chat/cancel/sess_live_gate_9` returned cleanly without stuck states or process crashes. | Session isolation maintained. |
| **Gate 10** | Ollama Failure / Recovery | **PASS** | Offline daemon returns normalized `SaarthiError(MODEL_ERROR)` without infinite loops or stack trace leaks; recovers cleanly when online. | Controlled error handling. |
| **Gate 11** | Performance & Resources | **PASS** | Cold model load: 7.47s, warm eval: 18.3 tokens/sec, API latency: <20ms, backend RSS: ~45 MiB. | Resource bounds verified. |
| **Gate 12** | Final Regression | **PASS** | 148 pytest tests PASSED (0 skipped, 0 failed); Vite build PASSED (348ms); source hygiene clean. | 100% test pass rate. |

---

## 4. Real Model Performance

| Scenario | Runs | Min | Avg | Max | CPU/GPU Split | VRAM Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ollama Cold Start** | 1 | 7.47s | 7.47s | 7.47s | 30% CPU / 70% GPU | 2567 MiB |
| **Ollama Warm Generation** | 3 | 2.77s | 2.95s | 3.20s | 30% CPU / 70% GPU | 2567 MiB |
| **Simple Chat Turn** | 3 | 3.10s | 6.33s | 9.80s | 30% CPU / 70% GPU | 2567 MiB |
| **Tool Execution Turn** | 2 | 12.20s | 13.10s | 14.00s | 30% CPU / 70% GPU | 2567 MiB |
| **Memory Recall Turn** | 2 | 4.80s | 5.05s | 5.30s | 30% CPU / 70% GPU | 2567 MiB |

---

## 5. Real Conversation Validation
- Multi-turn conversation history preserved across turns.
- Memory storage and recall verified with synthetic word `ORBITAL`.
- Tools (`file_list`) called accurately by model with real workspace output returned.
- Permission requests (`terminal`) present confirmation cards and enforce denial.
- All `<think>` reasoning tags and raw tool call tags stripped before rendering to UI.

---

## 6. Security Validation
- Sandbox: Access restricted strictly to `settings.ALLOWED_ROOTS`.
- Path Traversal: Path traversals outside allowed roots blocked with clear error responses.
- Permission Enforcement: `USER_CONFIRMATION` tools strictly require interactive user approval.
- Secret Redaction: Passwords and API keys blocked from storage; diagnostic stack traces sanitized.
- Error Sanitization: Raw exception tracebacks converted to normalized `SaarthiError` instances.

---

## 7. Regression Results
- **Total Tests**: 148
- **Passed**: 148
- **Failed**: 0
- **Skipped**: 0
- **Warnings**: 1
- **Runtime**: 27.24s

---

## 8. Frontend Build
- **Status**: SUCCESS
- **Build Duration**: 348 ms
- **Bundle Sizes**:
  - `dist/index.html` — 0.48 kB
  - `dist/assets/index-C-MqAGZa.css` — 54.06 kB
  - `dist/assets/index-BZN2rgmo.js` — 438.82 kB

---

## 9. Bugs Found
- Fixed minor import name discrepancy in `test_agent_loop_live_reliability.py` (`NemotronProvider`).

---

## 10. Known Limitations
- File operations are restricted strictly to configured workspace roots (`E:\Saarthi`) and expanded user directories (`Desktop`, `Downloads`, `Documents`).

---

## 11. Release Decision
### **RC1 READY**
The complete real system — Frontend, FastAPI backend, AgentCore, Ollama daemon, `nemotron-3-nano:4b` LLM, tools, permissions, memory store, and SQLite database — has been validated end-to-end under real live runtime conditions. 100% of tests are passing.
