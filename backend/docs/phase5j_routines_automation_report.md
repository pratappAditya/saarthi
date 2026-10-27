# Phase 5J — Routines & Automation for Saarthi Report

## Overview
Phase 5J transforms Saarthi's Goals, Proactive Intelligence, Agent Runtime, Personalization Engine, and Voice Engine into a unified, reliable, persistent automation engine (`RoutineEngine` & `RoutineScheduler`). Saarthi remains ONE universal AI operating companion across Signature, Forge, Pulse, and Aurora, executing recurring time-based and condition-triggered workflows under local-first persistence, entitlement control, and safety supremacy.

## Key Capabilities Implemented

### 1. Persistent Routine Model & SQLite Store
- Persistent `Routine` model saved in `saarthi.db`.
- SQLite tables: `routines`, `routine_conditions`, `routine_actions`, `routine_executions`, `routine_approvals`, `routine_notifications`.
- Scopes: `GLOBAL`, `PROJECT`, `DOMAIN`, `TASK`.
- Precedence hierarchy: `TASK > PROJECT > DOMAIN > GLOBAL > SYSTEM`.

### 2. Trigger Types Supported
- `TIME_TRIGGER`: Daily, weekly, specific time-of-day, days-of-week, cron intervals.
- `CONDITION_TRIGGER`: Application status changed, deadline approaching, goal progress stalled.
- `EVENT_TRIGGER`: Application updated, project created, task completed, milestone reached.
- `MANUAL_TRIGGER`: Immediate manual execution.
- `VOICE_TRIGGER`: Speech commands ("run morning briefing", "pause weekly review").

### 3. Natural Language Routine Parser & Previews
- `RoutineParser`: Converts prompts like *"Every Monday at 9 AM review my active projects"* or *"When an interview is scheduled, prepare questions"* into structured `RoutineDefinition` previews before user activation.

### 4. Routine Execution Engine & Autonomy Levels
- `RoutineEngine`: Evaluates triggers, assembles `ContextBundle` with `PersonalizationContext`, dispatches task graphs to `AgentRuntime`, manages risk policy checks via `PermissionEngine`, executes tool steps, and logs execution audit history.
- Autonomy Levels: `OBSERVE`, `SUGGEST`, `ASK`, `ACT`, `HIGH_RISK_ALWAYS_ASK`. Consequential actions prompt for explicit human approval.

### 5. Background Scheduler & Failure Recovery
- `RoutineScheduler`: Background daemon thread polling due routines, handling timezone-aware schedules, execution locking (duplicate prevention), and restart recovery.
- Missed Run Policies: `SKIP`, `RUN_ONCE_AFTER_START`, `CATCH_UP`, `ASK_USER`.
- Retry Policy: Exponential backoff with auto-pause after max retry limit.

### 6. First-Class Templates & Notification System
- First-class templates: Morning Briefing, Evening Review, Weekly Review, Goal Progress Review, Project Health Check, Career Progress Review, Research Digest.
- Notification Engine: In-app alerts, voice alerts during active voice sessions, quiet hours handling, and digest mode.

### 7. UI Components & Command Bar
- `RoutineManagerView.tsx`: Dashboard with active, paused, failed routines, upcoming runs, and execution history timeline.
- `RoutineBuilderView.tsx`: Dual-mode builder (Natural Language prompt parser + Visual WHEN/IF/THEN/WITH builder).
- `TrustCenterView.tsx`: Routines Audit section.
- `GlobalCommandBar.tsx`: Shortcuts for routine creation and execution.

## Verification Evidence
- **Live 20-Step E2E Script**: `python scratch/verify_phase5j_end_to_end.py` (`ALL PHASE 5J END-TO-END VERIFICATIONS PASSED!`).
- **Automated Pytest Suite**: `pytest backend/tests/test_phase5j_routines_automation.py ...` (39/39 tests passing).
- **Frontend Build**: `npm run build` passed with zero errors (`✓ built in 4.52s`).
