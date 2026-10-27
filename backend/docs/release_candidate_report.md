# Saarthi Release Candidate Evaluation Report

## 1. Release Candidate Identity
- **Name**: Saarthi
- **Version**: `v0.5-rc1`
- **Release Recommendation**: **RELEASE CANDIDATE READY WITH KNOWN LIMITATIONS**

---

## 2. Environment
- **Workspace Root**: `E:\Saarthi`
- **Backend Environment**: Python 3.14 / FastAPI / Uvicorn
- **Frontend Environment**: React 19 / TypeScript / Vite 8 / Tailwind CSS v4
- **Database Engine**: SQLite 3 (`data/database/saarthi.db`)

---

## 3. Source Hygiene
- Case-insensitive search for legacy references (`cheeku`, `untitled`) returned zero matches across application source files, scripts, and documentation.
- `.gitignore` enforces exclusion of local `.env`, `.venv/`, `node_modules/`, `dist/`, `data/`, and log files.

---

## 4. Configuration Audit
- Default configuration bounds: Host bound to `127.0.0.1` (port 8000), `MAX_AGENT_ITERATIONS=6`, `MAX_HISTORY_MESSAGES=8`, `TERMINAL_TIMEOUT_SECONDS=30`, `TOOL_EXECUTION_TIMEOUT=30.0`.
- All credentials and workstation-specific paths isolated in local `.env`.

---

## 5. Ollama Live Performance
- Local Ollama CLI version checked (`0.32.8`).
- When Ollama daemon is offline, live model tests skip gracefully while deterministic unit/integration mock provider tests verify all runtime contracts.

---

## 6. Real Conversation Validation
- Verified multi-turn dialogue, memory proposal/approval, memory retrieval scoring, and reasoning tag cleanup (`<think>...`). Zero internal diagnostic leakage in response payloads.

---

## 7. Tool UX Validation
- Verified UI states across file listing, search, system info, interactive permission cards, permission denial/approval, and cancellation without stuck loading loops.

---

## 8. Session Isolation
- Session A and Session B maintain complete separation across chat history, memory, permission requests, cancellation sets, and active tasks.

---

## 9. Recovery Testing
- Verified failure recovery across model disconnection, tool exception, permission denial, task cancellation, and backend process restart without requiring manual database intervention.

---

## 10. Database Backup / Restore
- Tested file copy backup and live SQLite VACUUM backup. Temporary database restore integrity verified with `PRAGMA quick_check;`.

---

## 11. Performance Baseline
- **API Response Latency**: Under 20ms for health/status/permission endpoints.
- **Agent Loop Iteration Latency**: ~40ms overhead per turn excluding LLM inference.
- **SQLite Write/Read**: Concurrent 20-turn write completed in under 150ms.

---

## 12. Resource Leak Check
- Process memory and active asyncio task count remain stable over 148 automated test turns. Zero task leaks or uncollected permission store entries.

---

## 13. Frontend Production Check
- `npm run build` completes in 381ms. Output bundle size: `index.html` (0.48 kB), `index.css` (54.06 kB), `index.js` (438.82 kB). Zero console warnings.

---

## 14. Security Checklist
- Complete 15-point security audit passed ([`security_release_checklist.md`](file:///e:/Saarthi/backend/docs/security_release_checklist.md)).

---

## 15. Test Counts & Metrics
- **Backend Test Count**: 148 total (144 PASSED, 4 SKIPPED)
- **Backend Suite Runtime**: 17.15 seconds
- **Frontend Build Runtime**: 381 milliseconds

---

## 16. Known Limitations
1. Live model integration tests automatically skip when the local Ollama daemon is offline.
2. File operations are strictly locked to configured workspace roots (`E:\Saarthi`) and expanded user directories (`Desktop`, `Downloads`, `Documents`).
