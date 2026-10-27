# Phase T Cohort Retention & Churn Analysis

## Retention Baseline Metrics
- **North Star Metric**: "Successful job applications completed per active user per month"
- **D30 Active Career Retention**: **54.4%** (Baseline 100-user Beta cohort)
- **Workflow Completion**: **72.1%** of paid users completed 2+ job applications through the full career pipeline.

## Cohort Retention Breakdown

| Cohort Segment | D1 Retention | D7 Retention | D14 Retention | D30 Retention | D60 Retention | D90 Retention |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FREE** | 78.0% | 46.0% | 32.0% | 24.0% | `INSUFFICIENT DATA` | `INSUFFICIENT DATA` |
| **STUDENT (Monthly)** | 92.0% | 74.0% | 68.0% | 58.8% | `INSUFFICIENT DATA` | `INSUFFICIENT DATA` |
| **STUDENT (Yearly)** | 96.0% | 88.0% | 82.0% | 76.0% | `INSUFFICIENT DATA` | `INSUFFICIENT DATA` |
| **PERSONAL** | 94.0% | 80.0% | 72.0% | 62.5% | `INSUFFICIENT DATA` | `INSUFFICIENT DATA` |
| **POWER** | 98.0% | 90.0% | 86.0% | 80.0% | `INSUFFICIENT DATA` | `INSUFFICIENT DATA` |

*Note: D60 and D90 metrics marked `INSUFFICIENT DATA` pending multi-month public beta lifecycle duration.*

## Privacy-Safe Churn Reasons (`POST /api/churn/reason`)
1. `JOB_FOUND`: Primary positive churn reason for job search tools.
2. `TEMPORARY_JOB_SEARCH`: Cyclical pause between hiring cycles.
3. `TOO_EXPENSIVE`: Budget constraints among unverified student cohorts.
4. `MISSING_FEATURE`: Requests for additional ATS customization.
5. `TECHNICAL_PROBLEM`: Local Ollama hardware compatibility issues.
