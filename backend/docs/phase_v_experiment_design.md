# Phase V Experiment Design & Statistical Framework

## Overview
Comprehensive statistical and operational architecture for evaluating watermark messaging variants (`CONTROL`, `VARIANT_A`, `VARIANT_B`, `VARIANT_C`) to measure Free → Paid conversion and retention impact without sacrificing user trust or privacy.

---

## 1. Experiment Objective & Hypotheses
- **Primary Objective**: Determine whether watermark-driven upgrade prompts generate meaningful Free → Paid conversion without harming user activation, D30 retention, or workflow completion.
- **Core Hypothesis**: Providing transparent pricing context (`₹149/month Student`) at the moment of document export value completion increases upgrade click-through without increasing churn.

---

## 2. Server-Side Variant Assignment
- **Methodology**: Deterministic SHA-256 hash of anonymous user/device identifier (`WatermarkEngine.get_experiment_variant`).
- **Variants**:
  - **CONTROL**: `Created with Saarthi • saarthi.ai` (Standard upgrade text)
  - **VARIANT_A**: `Created with Saarthi` (*"Remove this watermark with Saarthi Student — ₹149/month."*)
  - **VARIANT_B**: `Created with Saarthi` (*"Your resume is ready. Export it without the Saarthi watermark for ₹149/month."*)
  - **VARIANT_C**: `Created with Saarthi` (*"Apply professionally with a watermark-free resume. Saarthi Student — ₹149/month."*)
- **Invariants**: Server-controlled, mutually exclusive, persistent per session/device, zero frontend override.

---

## 3. Canonical 15-Stage Funnel
1. `USER_ACTIVATED`
2. `CAREER_WORKFLOW_STARTED`
3. `DOCUMENT_GENERATED`
4. `DOCUMENT_PREVIEWED`
5. `WATERMARKED_EXPORT`
6. `UPGRADE_PROMPT_SHOWN`
7. `PRICING_VIEWED`
8. `CHECKOUT_STARTED`
9. `PAYMENT_SUCCESS`
10. `LICENSE_ACTIVATED`
11. `CLEAN_EXPORT`
12. `SECOND_APPLICATION`
13. `INTERVIEW_PREP_USED`
14. `FOLLOW_UP_USED`
15. `ACTIVE_D30`

---

## 4. Statistical Decision Rules & Sample Size Target
- **Sample Size Target**: Minimum 100 real exposed users per variant (Preferred: 250+).
- **Rule**: If real observation count is $< 100$ per variant, report **`INSUFFICIENT DATA`**.
- **Guardrail**: A variant cannot be declared a winner if it increases conversion but causes D30 retention to deteriorate relative to `CONTROL`.
