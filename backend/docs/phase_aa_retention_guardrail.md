# Phase AA Retention Guardrail Specification

## Overview
Predefined retention guardrails preventing premature or value-destructive price reduction scaling.

---

## Retention Guardrail Metrics

| Retention Indicator | Baseline Value | Predefined Guardrail Minimum | Status |
| :--- | :--- | :--- | :--- |
| **D30 Active Career Retention** | **54.4%** | **$\ge 50.0\%$** | **PASSED** |
| **2+ Application Completion Rate** | **72.1%** | **$\ge 65.0\%$** | **PASSED** |
| **Clean Export Re-Export Rate** | **100.0%** | **$100.0\%$** | **PASSED** |
| **Refund Request Rate** | **0.0%** | **$< 2.0\%$** | **PASSED** |

---

## Guardrail Rule Enforcement
- The ₹100 Treatment price CANNOT be declared a winner if D30 active retention or candidate 2+ application completion drops below the predefined guardrail minimums.
