# Phase AA Cohort Retention & Engagement Report

## Overview
Evaluation of cohort active retention (D7, D14, D30) and candidate career engagement metrics.

---

## Retention Baseline Metrics

| Metric | Measured Baseline Value | Data Quality Tag | Audit Source |
| :--- | :--- | :--- | :--- |
| **D7 Active Retention** | **89.8%** | `OBSERVED_HISTORICAL` | Beta Cohort Workstation Telemetry |
| **D14 Active Retention** | **77.6%** | `OBSERVED_HISTORICAL` | Beta Cohort Workstation Telemetry |
| **D30 Active Retention** | **54.4%** | `OBSERVED_HISTORICAL` | Beta Cohort Workstation Telemetry |
| **Applications per User** | **2.8** | `OBSERVED_HISTORICAL` | Database Applications Tracker |
| **2+ Application Completion Rate** | **72.1%** | `DERIVED` | Candidates with $\ge 2$ Applications |
| **D30 Retention for 2+ App Candidates** | **71.4%** | `DERIVED` | High-engagement active cohort |

---

## Predefined Retention Guardrail Rule (Rule AA.11)
- **Guardrail Rule**: The ₹100 treatment price CANNOT be declared a winner if it causes:
  1. D30 active career retention to drop below 50.0%.
  2. Candidate 2+ application completion rate to drop below 65.0%.
