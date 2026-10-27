# Phase AB Live Pricing Experiment Progress & Participant Audit

## Overview
Evidence-first audit of Saarthi's live real-world pricing experiment evaluating Student ₹149/month Control (`STUDENT_CONTROL_149`) vs Student ₹100/month Treatment (`STUDENT_TREATMENT_100`).

---

## Participant Progress & Sample Gate Reconciliation (Rules AB.1, AB.3)

| Metric / Variant Key | Current Real Exposure | Target Threshold | Remaining Users Needed | Paid Subscribers | Attributable Revenue | Data Quality Tag |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`STUDENT_CONTROL_149`** | `INSUFFICIENT_DATA` | 100 Real Users | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |
| **`STUDENT_TREATMENT_100`**| `INSUFFICIENT_DATA` | 100 Real Users | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |
| **Total Combined Eligible**| `INSUFFICIENT_DATA` | 200 Real Users | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |
| **International USD** | `INSUFFICIENT_DATA` | N/A | N/A | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |

---

## Key Invariants Verified
1. **Existing Subscriber Protection**: All 68 historical Student subscribers remain protected at ₹149/mo and are 100% excluded from experiment treatment denominators.
2. **Synthetic Data Exclusion**: Zero pytest test accounts, synthetic loads, or test webhooks enter production experiment metrics.
3. **Immutability Guarantee**: Server-side SHA-256 hash assignment (`user_id + "_pricing"`) ensures 100% persistent, deterministic assignment per participant.
