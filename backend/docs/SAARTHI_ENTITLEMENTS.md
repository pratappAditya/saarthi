# Saarthi Entitlements & Enforcement Architecture

## Entitlement Model

```
Plan
  ↓
Entitlements (Capabilities Map & Limits)
  ↓
Capabilities (Enabled / Disabled)
  ↓
Frontend Gating (FeatureGate, PlanGate, Dynamic Sidebar)
  ↓
Backend Server-Side Authorization (require_capability dependency)
  ↓
Usage Limits (UsageService & Limits Map)
```

## Backend Authorization Enforcement

Server-side entitlement enforcement is managed via `app.core.entitlements.require_capability(capability_id)`.

If an account's active plan is not entitled to a capability, the backend returns HTTP 403 Forbidden with a structured error payload:

```json
{
  "detail": {
    "error": "ENTITLEMENT_FORBIDDEN",
    "capability": "tools.terminal",
    "capability_name": "Interactive terminal & shell execution",
    "current_plan": "free",
    "message": "Capability 'tools.terminal' is not included in your 'FREE' plan. Please upgrade to access this feature."
  }
}
```

## Frontend Capability Hydration

The frontend hydrates capabilities once on initialization via `GET /api/account/capabilities` into `EntitlementContext`.

Dynamic sidebar navigation items, feature buttons, and upgrade prompts consume `hasCapability()` and `hasPlan()` from `useEntitlements()`.
