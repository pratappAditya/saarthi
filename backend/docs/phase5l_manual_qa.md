# Phase 5L Manual QA Protocol & Scenario Guide

## 16 End-to-End Test Scenarios

1. **Scenario 1: Simple Question → Direct Answer**:
   - Query: *"What is the capital of France?"* -> Instant response from local Nemotron core.

2. **Scenario 2: Question → Research → Cited Result**:
   - Query: *"Research solid state battery technology developments"* -> Searches literature, maps citations, returns evidence summary.

3. **Scenario 3: File → Analysis → Report**:
   - Upload PDF -> Extract facts -> Generate structured markdown report.

4. **Scenario 4: Voice → Task → Agent Execution**:
   - Voice: *"Saarthi, research battery technology"* -> Triggers task graph, executes tools, speaks response.

5. **Scenario 5: Multi-Domain Research Workflow**:
   - Query spanning Archaeology, History, Research, Writing -> Multi-domain task graph executed with explicit handoffs.

6. **Scenario 6: Project → Goal → Routine → Agent**:
   - Goal: *"Master Embedded Systems"* -> Linked Project -> Weekly Routine -> Agent Execution -> Milestone progress update.

7. **Scenario 7: Permission Approval Flow**:
   - High-risk tool invocation -> Intercepted with approval request -> Click Approve -> Execution resumes.

8. **Scenario 8: Permission Rejection Flow**:
   - High-risk tool invocation -> User rejects -> Safe termination without state corruption.

9. **Scenario 9: Agent Failure Recovery**:
   - Tool step fails -> Dynamic re-plan -> Corrective fallback step appended -> Execution completes.

10. **Scenario 10: Long-Running Task Resume**:
    - Task interrupted/cancelled -> Click Resume -> Execution restores from last completed step.

11. **Scenario 11: Proactive Suggestion Acceptance**:
    - Notice: *"Cross-Domain Handoff Optimization"* -> Accept -> Triggers automated pipeline.

12. **Scenario 12: Personalization & Tone Adaptation**:
    - Change technical depth preference -> Responses automatically shift to advanced technical depth.

13. **Scenario 13: Entitlement Upgrade Gate**:
    - Click locked capability -> UpgradeModal opens showing plan requirement (`POWER`/`TEAMS`).

14. **Scenario 14: Prompt Injection Document Defense**:
    - Upload document containing hidden injection prompts -> Parsed safely as data without executing instructions.

15. **Scenario 15: Cross-Domain Voice Directives**:
    - Voice: *"Why did you switch domains?"* -> Explains specialized domain expertise required for artifact observation.

16. **Scenario 16: Four-Shell Theme Parity**:
    - Switch themes between Signature, Forge, Pulse, and Aurora -> Identical tasks, memories, routines, and goals rendered in all 4 views.
