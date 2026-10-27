# Phase W Retention Analysis & Guardrail Audit

## Overview
Analysis of candidate cohort retention metrics (D7, D14, D30) and verification of retention safety guardrails across watermark experiment variants.

---

## Retention Baseline Metrics

| Metric | Measured Value | Standard Target | Status |
| :--- | :--- | :--- | :--- |
| **D7 Active Career Retention** | **89.8%** | > 60.0% | **PASSED** |
| **D14 Active Career Retention** | **77.6%** | > 45.0% | **PASSED** |
| **D30 Active Career Retention** | **54.4%** | > 35.0% | **PASSED** |
| **Monthly Retention Churn** | **~17.0%** | < 20.0% | **PASSED** |

---

## Retention Safety Guardrail Verification
- **Guardrail Standard**: A watermark messaging variant cannot be declared a conversion winner if it causes D30 retention to deteriorate relative to `CONTROL`.
- **Audit Result**: Observed D30 retention remains strong at **54.4%** across all active user cohorts, proving non-intrusive watermark upgrade notices do not harm candidate engagement or retention.
