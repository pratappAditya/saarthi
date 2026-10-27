# Phase AB Cohort Retention & Guardrail Audit

## Overview
Audit of cohort active retention (D7, D14, D30) and predefined retention guardrail compliance.

---

## Retention Baseline & Guardrail Thresholds

| Retention Indicator | Baseline Observed Value | Predefined Guardrail Threshold | Audit Status |
| :--- | :--- | :--- | :--- |
| **D7 Active Retention** | **89.8%** | N/A | `OBSERVED_HISTORICAL` |
| **D14 Active Retention** | **77.6%** | N/A | `OBSERVED_HISTORICAL` |
| **D30 Active Retention** | **54.4%** | **$\ge 50.0\%$** | **PASSED** |
| **2+ Application Completion Rate** | **72.1%** | **$\ge 65.0\%$** | **PASSED** |
| **2+ Application Candidate D30** | **71.4%** | **$\ge 65.0\%$** | **PASSED** |

---

## Predefined Guardrail Rule
- A cheaper Student price (₹100/mo) CANNOT be declared successful if it causes D30 active retention or candidate 2+ application completion rates to fall below the guardrail thresholds.
