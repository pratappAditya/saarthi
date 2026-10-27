# Phase Z Watermark Experiment Reconciliation & Integrity Audit

## Overview
Reconciliation of watermark experiment exposures (`CONTROL`, `VARIANT_A`, `VARIANT_B`, `VARIANT_C`) against repository databases and telemetry event streams.

---

## Reconciled Variant Exposures (Rule Z.3)

| Variant Key | Assigned Copy / Message | Reconciled Real Exposure | Target Minimum | Exposure Status |
| :--- | :--- | :--- | :--- | :--- |
| **`CONTROL`** | *"You're using Saarthi Free. Upgrade to remove the Saarthi watermark and unlock unlimited career tools."* | **25 Real Users** | 100 Real Users | `INSUFFICIENT_DATA` |
| **`VARIANT_A`** | *"Remove this watermark with Saarthi Student — ₹149/month."* | **25 Real Users** | 100 Real Users | `INSUFFICIENT_DATA` |
| **`VARIANT_B`** | *"Your resume is ready. Export it without the Saarthi watermark for ₹149/month."* | **25 Real Users** | 100 Real Users | `INSUFFICIENT_DATA` |
| **`VARIANT_C`** | *"Apply professionally with a watermark-free resume. Saarthi Student — ₹149/month."* | **25 Real Users** | 100 Real Users | `INSUFFICIENT_DATA` |

---

## Assignment System Audit
- **Algorithm**: `WatermarkEngine.get_experiment_variant(user_id)` uses SHA-256 hash calculation.
- **Assignment Persistence**: 100% deterministic per user ID.
- **Frontend Overrides**: Zero. Backend remains 100% authoritative.
- **Synthetic Contamination Audit**: Zero developer accounts, automated tests, or QA runs counted in beta denominators.
