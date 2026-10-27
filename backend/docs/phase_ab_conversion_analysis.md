# Phase AB Conversion Funnel Analysis

## Overview
Analysis of production funnel conversion across experiment variants (`STUDENT_CONTROL_149` vs `STUDENT_TREATMENT_100`).

---

## Production Funnel Metrics Matrix

| Funnel Stage | `STUDENT_CONTROL_149` | `STUDENT_TREATMENT_100` | Data Quality Tag |
| :--- | :--- | :--- | :--- |
| **1. Eligible Exposed Participants** | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |
| **2. Pricing Page Views** | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |
| **3. Checkout Starts** | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |
| **4. Payment Successes** | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |
| **5. License Activations** | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |
| **6. Clean Watermark Re-Exports** | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |
| **7. Paid Conversion Rate %** | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` |

---

## Funnel Integrity Guarantees
- Denominators use ONLY eligible exposed participants within that specific variant.
- Synthetic payments and test webhooks are strictly excluded.
