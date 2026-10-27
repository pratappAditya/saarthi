# Saarthi Adversarial Validation Report

## Baseline (Verified 2026-08-15)

| Component       | Result                    |
|-----------------|---------------------------|
| Backend pytest  | 144 passed, 4 skipped     |
| Frontend build  | SUCCESS (10.09s)          |
| Ollama          | Skipped (daemon offline)  |

---

## Stage 0 — Bootstrap Inspection

### Existing Adversarial Test Files (13 test files)

| File                              | Functions | Param Cases | Import Status | Quality    |
|-----------------------------------|-----------|-------------|---------------|------------|
| test_api_fuzz.py                  | 2         | 125         | ✅ OK          | Good       |
| test_model_fuzz.py                | 1         | 110         | ❌ BROKEN      | Padding    |
| test_tool_fuzz.py                 | 1         | 148         | ❌ BROKEN      | 114 padding|
| test_path_fuzz.py                 | 1         | 106         | ❌ BROKEN      | Padding    |
| test_permission_fuzz.py           | 2         | 101         | ❌ BROKEN      | OK         |
| test_session_fuzz.py              | 1         | 85          | ⚠️ asyncio     | Good       |
| test_memory_fuzz.py               | 1         | 100         | ⚠️ asyncio     | Good       |
| test_state_machine_exhaustion.py  | 2         | 60          | ❌ BROKEN      | Good       |
| test_concurrency_stress.py        | 1         | 50          | ⚠️ asyncio     | Good       |
| test_failure_injection.py         | 1         | 60          | ❌ BROKEN      | Weak       |
| test_prompt_injection.py          | 1         | 50          | ❌ BROKEN      | Padding    |
| test_secret_redaction.py          | 1         | 50          | ✅ OK          | No prod    |
| test_real_ollama_adversarial.py   | 1         | 20          | ✅ OK          | Skippable  |

### Import Breakage Details

| File                         | Broken Import                                              | Actual Location                          |
|------------------------------|------------------------------------------------------------|------------------------------------------|
| test_model_fuzz.py           | `app.agent.reasoning.clean_reasoning`                      | `app.models.ollama.clean_reasoning`      |
| test_tool_fuzz.py            | `ToolExecutor(registry=registry)` — missing 3 req args     | Needs `security_manager`, `allowed_roots`, `log_path` |
| test_path_fuzz.py            | `app.tools.security.SecurityManager, SandboxViolationError`| `app.security.permissions.SecurityManager`; no `SandboxViolationError` exists |
| test_permission_fuzz.py      | `app.tools.permission.PermissionStore, PermissionRequestStatus` | `app.security.permissions.PermissionStore`; no `PermissionRequestStatus` exists |
| test_state_machine_exhaustion.py | `app.agent.state.AgentState, AgentStateMachine`        | Module does not exist                    |
| test_failure_injection.py    | `app.agent.errors.ToolExecutionError`                      | Does not exist; `SaarthiError` constructor requires `category` arg |
| test_prompt_injection.py     | `app.agent.reasoning.clean_reasoning`                      | `app.models.ollama.clean_reasoning`      |

### Additional Issues

- `pytest-asyncio` is NOT installed. Tests using `@pytest.mark.asyncio` will not run. Baseline uses `@pytest.mark.anyio`.
- `test_secret_redaction.py` inlines its own keyword list — does NOT test production code.
- `test_tool_fuzz.py` has 114 padding cases that all call `file_list` with path `"."` and different `extra_param` — meaningless.
- `test_failure_injection.py` only checks `str(error_obj)` — does not inject failures into running code.

---

## Test Accounting

| Metric                      | Count  |
|-----------------------------|--------|
| Test files                  | 13     |
| Test functions              | 16     |
| Total parameterized cases   | 1,065  |
| Cases that can actually run | ~195   |
| Cases blocked by imports    | ~695   |
| Cases blocked by asyncio    | ~175   |
| Meaningful non-padding cases| ~450   |

### Breakdown by Category

| Category                          | Nominal Cases | Actually Runnable | Meaningful |
|-----------------------------------|---------------|-------------------|------------|
| API input fuzzing                 | 125           | 125               | ~35        |
| Model/reasoning parsing          | 110           | 0 (broken import) | ~8         |
| Tool execution fuzzing            | 148           | 0 (broken init)   | ~34        |
| Path security/sandbox             | 106           | 0 (broken import) | ~12        |
| Permission lifecycle              | 101           | 0 (broken import) | ~4         |
| Session isolation                 | 85            | 0 (needs asyncio) | ~85        |
| Memory/secret screening           | 100           | 0 (needs asyncio) | ~5         |
| State machine transitions         | 60            | 0 (broken import) | ~60        |
| Concurrency stress                | 50            | 0 (needs asyncio) | ~50        |
| Failure injection/error sanitize  | 60            | 0 (broken import) | ~3         |
| Prompt injection                  | 50            | 0 (broken import) | ~5         |
| Secret redaction                  | 50            | 50                | ~5         |
| Real Ollama                       | 20            | 20 (skipped)      | 20         |

**Total executed cases: 0** (adversarial suite has never successfully run)

**Passed: 0 | Failed: 0 | Skipped: 0**

---

## Categories Missing Entirely

- Cancellation latency & safety
- Sync tool isolation & timeout contracts
- Database integrity & WAL transactions
- Resource limits (max iterations, max output size)
- Malformed HTTP request bodies
- Frontend/API contract compliance
- Agent loop iteration fuzzing

---

## Stage 1 Status

**NOT STARTED** — Requires import fixes and test quality improvements before execution.
