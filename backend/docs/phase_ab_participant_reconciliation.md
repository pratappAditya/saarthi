# Phase AB Live Participant Exposure & Exclusion Audit

## Overview
Reconciliation of live eligible experiment participants across `STUDENT_CONTROL_149` (₹149/mo) and `STUDENT_TREATMENT_100` (₹100/mo), with strict exclusion of non-production accounts.

---

## Live Participant Audit Breakdown (Rules AB.1, AB.3)

| User Category / Variant | Live Exposure Count | Target Minimum Gate | Remaining Needed | Data Quality Tag | Audit Finding |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`STUDENT_CONTROL_149` (₹149)**| `INSUFFICIENT_DATA` | 100 Real Users | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | Accumulating live exposure |
| **`STUDENT_TREATMENT_100` (₹100)**| `INSUFFICIENT_DATA` | 100 Real Users | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | Accumulating live exposure |
| **Total Combined Eligible** | `INSUFFICIENT_DATA` | 200 Real Users | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | Accumulating live exposure |
| **Existing Student Subscribers**| 68 | N/A | 0 | `OBSERVED_CURRENT` | Protected; 100% excluded from treatment |
| **Pytest / Test Accounts** | Excluded | N/A | 0 | `EXCLUDED` | Zero synthetic accounts in denominators |
| **Duplicate / Hardware Logins** | Excluded | N/A | 0 | `EXCLUDED` | Single participation per fingerprint |

---

## Immutability & Protection Guarantees
1. **Server-Side Hash Assignment**: `WatermarkEngine.get_pricing_experiment_variant(user_id)` uses SHA-256 hash calculation (`user_id + "_pricing"`).
2. **Subscriber Price Protection**: All 68 baseline Student subscribers retain their existing subscription and entitlement without re-assignment.
