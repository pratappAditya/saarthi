# Saarthi Backend Architecture Documentation Index

This directory contains the canonical architectural specifications, runtime state machine documentation, execution contracts, security models, and observability standards for the Saarthi AI Assistant backend.

---

## Master Architecture Index

1. [agent_loop_audit_report.md](file:///e:/Saarthi/backend/docs/agent_loop_audit_report.md) — Comprehensive Phase A Agent Loop Audit Report.
2. [agent_loop_diagram.md](file:///e:/Saarthi/backend/docs/agent_loop_diagram.md) — Architectural Sequence & Loop Flow Diagram.
3. [agent_state_machine.md](file:///e:/Saarthi/backend/docs/agent_state_machine.md) — Runtime State Machine Specifications (`AgentState`).
4. [agent_iteration_contract.md](file:///e:/Saarthi/backend/docs/agent_iteration_contract.md) — Formal 13-Step Iteration Contract.
5. [tool_execution_model.md](file:///e:/Saarthi/backend/docs/tool_execution_model.md) — Async/Sync Tool Execution & ThreadPool Isolation Model.
6. [tool_contract.md](file:///e:/Saarthi/backend/docs/tool_contract.md) — Production Tool Execution & Registry Duplicate Prevention Contract.
7. [model_contract.md](file:///e:/Saarthi/backend/docs/model_contract.md) — LLM Provider HTTP, Timeout, & Reasoning Cleanup Contract.
8. [permission_contract.md](file:///e:/Saarthi/backend/docs/permission_contract.md) — Security Hierarchy, Approval Scope, & Non-Reusability Contract.
9. [memory_contract.md](file:///e:/Saarthi/backend/docs/memory_contract.md) — Memory Pipeline, Secret Screening, Scoring, & Context Injection.
10. [session_contract.md](file:///e:/Saarthi/backend/docs/session_contract.md) — Multi-Session Concurrency & State Isolation Contract.
11. [error_contract.md](file:///e:/Saarthi/backend/docs/error_contract.md) — Normalized Internal Error Categories & Sanitization Contract.
12. [observability.md](file:///e:/Saarthi/backend/docs/observability.md) — Telemetry Logging Policy, Privacy Standards, & Diagnostic Schemas.
