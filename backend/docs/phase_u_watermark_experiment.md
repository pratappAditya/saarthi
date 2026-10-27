# Phase U Watermark Experiment Architecture & Messaging Framework

## Overview
Server-side experiment framework evaluating 4 watermark messaging variants to optimize Free → Paid conversion without dark patterns or deceptive claims.

---

## Variant Definitions & Messaging Matrix

| Variant Key | Watermark Footer Text | Upgrade Banner Message |
| :--- | :--- | :--- |
| **CONTROL** | `Created with Saarthi • saarthi.ai` | *"You're using Saarthi Free. Upgrade to remove the Saarthi watermark and unlock unlimited career tools."* |
| **VARIANT_A** | `Created with Saarthi` | *"Remove this watermark with Saarthi Student — ₹149/month."* |
| **VARIANT_B** | `Created with Saarthi` | *"Your resume is ready. Export it without the Saarthi watermark for ₹149/month."* |
| **VARIANT_C** | `Created with Saarthi` | *"Apply professionally with a watermark-free resume. Saarthi Student — ₹149/month."* |

---

## Technical Architecture & Assignment Rules
- **Server-Side Assignment**: Assigned authoritatively by backend in `WatermarkEngine.get_experiment_variant(user_id)` via SHA-256 hash modulo calculation.
- **Client Non-Interference**: Frontend components do **not** select their own experiment variant.
- **Persistence**: Variant assignment remains deterministic per user session or device fingerprint.

---

## Operational Telemetry Tracking
Events logged to `operational_telemetry.log`:
- `WATERMARK_EXPERIMENT_ASSIGNED`
- `WATERMARK_UPGRADE_PROMPT_SHOWN`
- `PRICING_VIEWED`
- `CHECKOUT_STARTED`
- `PAYMENT_SUCCESS`
- `LICENSE_ACTIVATED`
- `CLEAN_EXPORT`

---

## Statistical Safety Governance
- **Current Observation Status**: `INSUFFICIENT DATA — CONTINUE EXPERIMENT`.
- **Governance**: Statistical significance will be declared strictly after live public beta traffic accumulates $\ge 100$ observations per variant.
