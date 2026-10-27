# Saarthi Deep Personalization Architecture

## 1. System Architecture

```
User Turn / Interaction Signal
            │
            ▼
┌───────────────────────┐
│ PersonalizationEngine │ ──► Precedence: Task > Project > Domain > Global
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ PersonalizationContext│ ──► Injected into ContextBundle & System Prompt
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ Orchestrator / Models │ ──► Adapts Tone, Length, Depth, Formatting
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ PersonalizationStore  │ ──► SQLite (user_personalization_profile, preferences,
└───────────────────────┘     domain_expertise, project_overrides)
```

## 2. Preference Classification & Lifecycle
- `USER_EXPLICIT`: Directly configured by user in Dashboard (Confidence: 1.0).
- `USER_CONFIRMED`: Inferred item explicitly confirmed by user (Confidence: 1.0).
- `MODEL_INFERRED`: Automatically inferred from interaction patterns with confidence (0.0 to 1.0) and evidence.
- `SYSTEM_DERIVED`: Derived from non-sensitive system telemetry.

## 3. Precedence Order Hierarchy
1. **Task Prompt Override**: Explicit requests in current turn (e.g. "detailed breakdown").
2. **Project-Scoped Override**: Settings attached to current active project.
3. **Domain-Scoped Override**: Expertise level and depth settings for active domain.
4. **Global User Profile**: Baseline communication and work style settings.
5. **System Defaults**: Built-in fallback parameters.

## 4. Privacy & Team Boundaries
- **No Sensitive Profiling**: Psychological, medical, political, religious, or demographic profiling is strictly prohibited.
- **Team Isolation**: In Team workspaces, private user personalization remains local/private to the individual user. Workspace shared defaults exist separately.
- **Safety Supremacy**: Risk policy, human approvals, and entitlements are never bypassed by personalization.
