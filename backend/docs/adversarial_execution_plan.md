# Saarthi Adversarial Execution Plan

## Pre-Requisite: Fix Existing Suite (Stage 0)

Before any stage can execute, the existing adversarial tests must be repaired:

1. Fix all 7 broken imports (see validation_report.md for details)
2. Replace `@pytest.mark.asyncio` with `@pytest.mark.anyio` (no pytest-asyncio installed)
3. Remove meaningless padding cases (114 identical file_list calls, etc.)
4. Ensure tests exercise actual production code (not inlined logic)
5. Fix ToolExecutor instantiation (needs security_manager, allowed_roots, log_path)
6. Fix SaarthiError constructor usage (requires category arg)

---

## Stage 1: API + Input Fuzzing (Target: 150+)

**Files**: test_api_fuzz.py

**Cases to cover**:
- Empty/whitespace/null message bodies
- Unicode: Hindi, CJK, emoji, RTL, combining chars
- Control characters, null bytes
- Max-length payloads (1K, 5K, 50K, 100K chars)
- XSS/HTML injection payloads
- SQL injection strings in session_id
- Malformed JSON bodies, non-JSON bodies
- Missing required fields, extra fields
- Invalid content-type headers
- Session ID boundary values

**Production code exercised**: app.main (FastAPI routes), app.api.routes

---

## Stage 2: Model/Parser Fuzzing (Target: 150+)

**Files**: test_model_fuzz.py, test_prompt_injection.py

**Cases to cover**:
- Reasoning tag stripping: `<think>`, `<thinking>`, unclosed, nested, empty
- Malformed tool call markers in model output
- JSON extraction from model responses
- Multiple tool calls in single response
- Fake permission approvals in model output
- Prompt injection payloads (override instructions, fake system messages)
- Unicode in model responses
- Empty/whitespace-only model responses
- Extremely long model responses

**Production code exercised**: app.models.ollama.clean_reasoning, agent core parsing

---

## Stage 3: Tools + Path Security (Target: 200+)

**Files**: test_tool_fuzz.py, test_path_fuzz.py

**Cases to cover**:
- All 6 production tools with valid/invalid/boundary args
- Path traversal: ../, encoded %2e%2e, mixed slashes, UNC paths
- Sandbox boundary enforcement (in-workspace vs out-of-workspace)
- File paths with Unicode, spaces, special chars
- Tool argument type mismatches
- Unknown tool names
- Extra/missing tool arguments
- Tool timeout behavior

**Production code exercised**: app.tools.executor, app.security.paths, all tool classes

---

## Stage 4: Permissions + Sessions (Target: 200+)

**Files**: test_permission_fuzz.py, test_session_fuzz.py

**Cases to cover**:
- Permission request lifecycle (create, approve, deny)
- Replay protection (double-approve, approve-after-deny)
- Cross-session permission access attempts
- Invalid request IDs
- Session isolation (history, memory, permissions)
- SecurityManager level checks (READ_ONLY through PRIVILEGED)
- Permission level hierarchy enforcement

**Production code exercised**: app.security.permissions, app.db.sqlite

---

## Stage 5: Memory + Database (Target: 150+)

**Files**: test_memory_fuzz.py, test_concurrency_stress.py

**Cases to cover**:
- Memory CRUD operations
- Secret screening (passwords, API keys, tokens, connection strings)
- Memory category validation
- Concurrent database writes (messages + memories)
- Database schema integrity
- Large content storage
- Unicode content in memories
- Cross-session memory isolation

**Production code exercised**: app.memory.manager, app.memory.sqlite_store, app.db.sqlite

---

## Stage 6: State Machine + Cancellation + Timeout (Target: 150+)

**Files**: test_state_machine_exhaustion.py (requires app.agent.state or equivalent)

**Cases to cover**:
- All legal state transitions
- All illegal state transitions (exhaustive)
- Cancellation from each state
- Error state transitions
- Agent iteration limits

**Production code exercised**: Agent state machine (if exists), app.agent.core

**NOTE**: app.agent.state module does not exist. Must determine if state machine logic is inline in core.py or needs to be tested differently.

---

## Stage 7: Prompt Injection + Secret Redaction (Target: 200+)

**Files**: test_prompt_injection.py, test_secret_redaction.py

**Cases to cover**:
- System prompt override attempts
- Fake tool call injection
- Fake permission approval injection
- Nested reasoning tag attacks
- Secret patterns: AWS keys, GitHub tokens, JWTs, private keys, connection strings
- Secret redaction in error messages
- Secret redaction in tool execution logs
- Secret screening in memory storage

**Production code exercised**: app.models.ollama.clean_reasoning, app.tools.executor._filter_secrets, app.memory.manager

---

## Stage 8: Concurrency + Recovery + Resource Limits (Target: 200+)

**Files**: test_concurrency_stress.py (expanded)

**Cases to cover**:
- Concurrent session writes (2, 5, 10, 20, 50 sessions)
- Concurrent tool executions
- Database WAL mode under load
- Error recovery after failures
- Resource limit enforcement (max iterations, max output)
- Large payload handling

**Production code exercised**: app.db.sqlite, app.tools.executor, app.agent.core

---

## Stage 9: Controlled Real-Ollama Validation

**Files**: test_real_ollama_adversarial.py

**Cases**: 20 (skipped when Ollama offline)

**Execution**: Only when Ollama daemon is confirmed running.

---

## Stage 10: Full Regression + Final Accounting

- Run complete baseline + adversarial suite
- Verify zero regressions
- Produce final case count
- Update adversarial_validation_report.md with final numbers

---

## Targets Summary

| Stage | Category                          | Target Cases |
|-------|-----------------------------------|-------------|
| 0     | Fix imports & quality             | 0 (prep)    |
| 1     | API + input fuzzing               | 150+        |
| 2     | Model/parser fuzzing              | 150+        |
| 3     | Tools + path security             | 200+        |
| 4     | Permissions + sessions            | 200+        |
| 5     | Memory + database                 | 150+        |
| 6     | State machine + cancellation      | 150+        |
| 7     | Prompt injection + secret redact  | 200+        |
| 8     | Concurrency + recovery + limits   | 200+        |
| 9     | Real Ollama                       | 20          |
| 10    | Full regression                   | 0 (verify)  |
| **Total** |                               | **>=1,420** |

**Minimum acceptance: >=1,000 meaningful executed cases**
