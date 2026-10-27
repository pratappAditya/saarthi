# Saarthi Routines & Automation Architecture

## 1. System Architecture Diagram

```
Trigger Event / Schedule Timer / Voice Command
                     │
                     ▼
        ┌─────────────────────────┐
        │    RoutineScheduler     │ ──► Polls SQLite saarthi.db for due routines
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │      RoutineEngine      │ ──► Evaluates conditions & retries
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │      ContextEngine      │ ──► Precedence: Task > Project > Domain > Global
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │      AgentRuntime       │ ──► Synthesizes TaskGraph
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │    PermissionEngine     │ ──► Enforces Human Approval for high-risk
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │      ToolExecutor       │ ──► Executes pre-authorized tools
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │    NotificationEngine   │ ──► In-App, Voice, Quiet Hours Digest
        └─────────────────────────┘
```

## 2. Trigger Taxonomy
1. **TIME_TRIGGER**: Scheduled via daily/weekly time-of-day or cron intervals.
2. **CONDITION_TRIGGER**: Triggered by state events (application status changed, project deadline approaching, goal progress stalled).
3. **EVENT_TRIGGER**: Internal workflow events (project created, document imported, milestone achieved).
4. **MANUAL_TRIGGER**: User-initiated immediate execution.
5. **VOICE_TRIGGER**: Voice command execution via VoiceConversationEngine.

## 3. Precedence Hierarchy
- `TASK > PROJECT > DOMAIN > GLOBAL > SYSTEM`
- Explicit routine parameters take precedence over inferred personalization defaults.

## 4. Safety & Permissions
- Personalization and automation NEVER override risk policy.
- Actions with `high` or `critical` risk level prompt the user for explicit approval via `PermissionEngine`.
- Repeated failures automatically pause the routine after `max_retries` is reached, preventing infinite background loops.
