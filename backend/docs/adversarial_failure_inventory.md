# Saarthi Adversarial Failure Inventory

## Baseline Failure Summary

| ID | Test | Category | Failure | Root Cause | Classification | Severity |
|----|------|----------|---------|------------|----------------|----------|
| ADV-FAIL-001 | `test_fuzz_concurrent_database_writes`, `test_fuzz_memory_storage_and_screening`, `test_cross_session_history_isolation` (235 cases) | Concurrency / Memory / Session | `ERROR at setup: requested an async fixture 'async_test_db'` | Missing `pytest-asyncio` plugin runner configuration in test execution flags | ENVIRONMENT | ENVIRONMENT |
| ADV-FAIL-002 | `test_fuzz_tool_executor_execution` (148 cases) | Tool Fuzzing | `AttributeError: 'ToolExecutor' object has no attribute 'execute'` | Test function invoked non-existent method `executor.execute` instead of production API `executor.execute_tool` | TEST_DEFECT | TEST_DEFECT |
| ADV-FAIL-003 | `test_fuzz_illegal_state_machine_transitions` (5 cases: `IDLE-IDLE`, `WAITING_MODEL-WAITING_MODEL`, `WAITING_PERMISSION-WAITING_PERMISSION`, `COMPLETED-COMPLETED`, `FAILED-FAILED`) | State Machine | `Failed: DID NOT RAISE InvalidStateTransitionError` | Test parametrized self-transitions (`s1 == s2`) as illegal, but `AgentState.transition_to` is explicitly idempotent for identical state transitions | TEST_DEFECT | TEST_DEFECT |
| ADV-FAIL-004 | `test_cancel_between_iterations` | Recovery / Cancellation | `asyncio.exceptions.CancelledError` | `AgentCore.cancel_session()` called `task.cancel()` on `asyncio.current_task()`, causing self-cancellation of the running task during synchronous loop execution | Genuine Saarthi Production Bug | MEDIUM |
| ADV-FAIL-005 | `test_fuzz_real_ollama_generation_cases` (20 cases) | Real Ollama | `SKIPPED (Ollama server offline)` | Local Ollama daemon instance is offline | ENVIRONMENT | ENVIRONMENT |

---

## Detailed Failure Analysis

### ADV-FAIL-001: Missing Async Test Runner Configuration
- **Symptom**: 235 async test cases in `test_concurrency_stress.py`, `test_memory_fuzz.py`, and `test_session_fuzz.py` failed during setup with `AssertionError` in `pytest_asyncio`.
- **Root Cause**: `pytest-asyncio` package was not installed in `.venv` and `-o asyncio_mode=auto` flag was missing from test invocation command.
- **Resolution**: Installed `pytest-asyncio` and added `-o asyncio_mode=auto` flag to pytest execution.

### ADV-FAIL-002: Incorrect Method Call in Tool Fuzz Tests
- **Symptom**: All 148 test cases in `test_tool_fuzz.py` failed with `AttributeError`.
- **Root Cause**: Test invoked `executor.execute()` instead of the production contract `executor.execute_tool()`.
- **Resolution**: Updated `test_tool_fuzz.py` to call `executor.execute_tool()`.

### ADV-FAIL-003: Idempotent State Transition Parametrization
- **Symptom**: 5 self-transition test cases failed because `InvalidStateTransitionError` was not raised.
- **Root Cause**: In [`backend/app/agent/core.py`](file:///E:/Saarthi/backend/app/agent/core.py#L100-L106), `AgentState.transition_to` is defined as:
  ```python
  if target_state == self.current_state:
      return  # Idempotent transition to same state
  ```
  Self-transitions are valid idempotent operations by design.
- **Resolution**: Filtered out `s1 == s2` self-transitions from `ILLEGAL_TRANSITIONS` in `test_state_machine_exhaustion.py`.

### ADV-FAIL-004: Current Task Cancellation in `AgentCore.cancel_session`
- **Symptom**: `test_cancel_between_iterations` failed with unhandled `asyncio.exceptions.CancelledError`.
- **Root Cause**: When a session was cancelled synchronously within the active event loop task, `cancel_session` invoked `task.cancel()` on `asyncio.current_task()`.
- **Resolution**: Updated [`backend/app/agent/core.py`](file:///E:/Saarthi/backend/app/agent/core.py#L183-L191) so that `cancel_session` sets the cancellation flag in `self._canceled_sessions` and only calls `task.cancel()` if `task != asyncio.current_task()`.
