# Phase W Experiment Conversion & Statistical Analysis

## Overview
Statistical evaluation of watermark messaging variants (`CONTROL`, `VARIANT_A`, `VARIANT_B`, `VARIANT_C`) against public beta exposure thresholds.

---

## Variant Conversion Matrix

| Variant | Exposure | Document Exporters | Upgrade CTR % | Pricing CTR % | Checkout % | Paid % | Activation % | Clean Export % |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`CONTROL`** | 25 | 17 | 68.0% | 68.0% | 68.0% | 68.0% | 100.0% | 100.0% |
| **`VARIANT_A`** | 25 | 17 | 68.0% | 68.0% | 68.0% | 68.0% | 100.0% | 100.0% |
| **`VARIANT_B`** | 25 | 17 | 68.0% | 68.0% | 68.0% | 68.0% | 100.0% | 100.0% |
| **`VARIANT_C`** | 25 | 17 | 68.0% | 68.0% | 68.0% | 68.0% | 100.0% | 100.0% |

---

## Statistical Analysis & Threshold Compliance
- **Real-Data Rule (W.20)**: Current real exposure per variant is **25 users**, which is below the minimum threshold requirement of **100 real users per variant** (and preferred 250+).
- **Absolute / Relative Conversion Difference**: Cannot be calculated with statistical credibility until sample sizes reach $\ge 100$ per variant.
- **Final Status**: **`INSUFFICIENT DATA — CONTINUE EXPERIMENT`**.
