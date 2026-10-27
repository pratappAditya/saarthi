# Phase AA RPEU Primary Metric Analysis

## Overview
Analysis of the primary decision metric: Revenue per Eligible Exposed User ($\text{RPEU}$).

---

## RPEU Mathematical Formulation
$$\text{RPEU}_{\text{Control}} = \frac{\text{Realized Revenue from } \text{STUDENT\_CONTROL\_149}}{\text{Eligible Exposed Users in Control}}$$

$$\text{RPEU}_{\text{Treatment}} = \frac{\text{Realized Revenue from } \text{STUDENT\_TREATMENT\_100}}{\text{Eligible Exposed Users in Treatment}}$$

---

## Strategic Decision Rule
- The treatment price (₹100/mo) will ONLY be declared a winner if:
  1. $\text{RPEU}_{\text{Treatment}} > \text{RPEU}_{\text{Control}}$ (or acceptably non-inferior).
  2. Predefined retention guardrails (D30 $\ge 50\%$) are satisfied.
