# Phase W Watermark Experiment Status & Integrity Audit

## Overview
Comprehensive audit of experiment variant assignment integrity, exposure counts, and persistent server-side hash assignment rules across public beta cohorts.

---

## Real Exposure Breakdown by Variant

| Variant Key | Target Copy / Upgrade Message | Real Beta Exposure | Target Required | Status |
| :--- | :--- | :--- | :--- | :--- |
| **`CONTROL`** | *"You're using Saarthi Free. Upgrade to remove the Saarthi watermark and unlock unlimited career tools."* | 25 Users | 100 Users | `INSUFFICIENT DATA` |
| **`VARIANT_A`** | *"Remove this watermark with Saarthi Student — ₹149/month."* | 25 Users | 100 Users | `INSUFFICIENT DATA` |
| **`VARIANT_B`** | *"Your resume is ready. Export it without the Saarthi watermark for ₹149/month."* | 25 Users | 100 Users | `INSUFFICIENT DATA` |
| **`VARIANT_C`** | *"Apply professionally with a watermark-free resume. Saarthi Student — ₹149/month."* | 25 Users | 100 Users | `INSUFFICIENT DATA` |

---

## Experiment Integrity Verification
1. **Server-Side Assignment**: Assigned strictly by backend in `WatermarkEngine.get_experiment_variant(user_id)` via SHA-256 hash modulo calculation.
2. **Client Isolation**: Zero frontend overrides allowed. Frontend components render the assigned server variant authoritatively.
3. **Persistence**: Assignment remains 100% deterministic per anonymous user ID or device fingerprint.
4. **Contamination Audit**: 0 cross-variant reassignments detected. 0 test or developer accounts counted towards public beta exposure.
