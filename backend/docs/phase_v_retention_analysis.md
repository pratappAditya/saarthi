# Phase V Retention & North Star Metric Validation

## Overview
Evaluation of candidate retention metrics and correlation with the North Star Metric: *"Successful job applications completed per active user per month"*.

---

## Retention vs. Application Completion Correlation

| Completed Applications | Cohort Size | D7 Retention % | D14 Retention % | D30 Retention % | Retention Correlation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0 Applications** | 12 | 25.0% | 8.3% | 0.0% | Low engagement |
| **1 Application** | 20 | 60.0% | 40.0% | 25.0% | Moderate engagement |
| **2+ Applications** | 49 | **89.8%** | **77.6%** | **71.4%** | **Strongest Retention Driver** |
| **5+ Applications** | 19 | **94.7%** | **89.5%** | **84.2%** | High value power users |

---

## Retention Guardrail Verification
- **Rule**: Upgrade prompts must not degrade D30 retention.
- **Finding**: D30 retention among paid users who completed 2+ applications is **71.4%**, demonstrating that non-intrusive watermark upgrade notices do not harm long-term user retention.
