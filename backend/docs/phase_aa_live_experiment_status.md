# Phase AA Live Pricing Experiment Status & Audit Report

## Overview
Status audit of Saarthi's live real-world pricing experiment evaluating Student ₹149/month Control (`STUDENT_CONTROL_149`) vs Student ₹100/month Treatment (`STUDENT_TREATMENT_100`).

---

## Technical Experiment Baseline Identification
- **Application Version**: `v0.5.0-rc2` (Product Frozen)
- **Public Beta Status**: `PUBLIC BETA OPEN`
- **Experiment Assignment**: Server-side SHA-256 hash assignment (`WatermarkEngine.get_pricing_experiment_variant`)
- **Backend Test Baseline**: **2,224 passed / 0 failed / 1 warning**
- **Frontend Production Build**: Vite v8.2.1 (`dist/assets/index-ChV5oDM3.js`, 508.92 kB)

---

## Live Participant Exposure Summary (Rule AA Continuation)

| Variant Key | Assigned Copy / Price | Live Eligible Participants | Paid Subscribers | Attributable Revenue | Data Quality Tag |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`STUDENT_CONTROL_149`** | Student ₹149 / month | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |
| **`STUDENT_TREATMENT_100`**| Student ₹100 / month | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |
| **International USD** | Student $1.50 / month | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |

---

## Audit Key Findings
1. The pricing experiment endpoints (`GET /api/billing/pricing-experiment` and `POST /api/billing/refund-request`) are live and operational in `v0.5.0-rc2`.
2. Existing ₹149 subscribers (68 paid accounts) are strictly protected and excluded from experiment denominators to preserve data truth.
3. Live organic participant accumulation is active; no synthetic or unit-test payments are allowed into production experiment metrics.
