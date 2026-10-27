# Phase AB RPEU Primary Decision Metric Analysis

## Overview
Detailed formulation and evaluation of the primary decision metric: Revenue per Eligible Exposed User ($\text{RPEU}$).

---

## Mathematical RPEU Formulation
$$\text{RPEU}_{\text{Control}} = \frac{\text{Attributable Subscription Revenue from } \text{STUDENT\_CONTROL\_149}}{\text{Eligible Exposed Users in Control}}$$

$$\text{RPEU}_{\text{Treatment}} = \frac{\text{Attributable Subscription Revenue from } \text{STUDENT\_TREATMENT\_100}}{\text{Eligible Exposed Users in Treatment}}$$

---

## Statistical Decision Rules
- **Rule 1**: The ₹100 treatment price CANNOT be declared a winner based on signup conversion alone. It requires $\text{RPEU}_{\text{Treatment}} > \text{RPEU}_{\text{Control}}$ (or acceptably non-inferior).
- **Rule 2**: Minimum required sample size is **100 eligible real participants per variant** (200 total).
- **Current Finding**: Real participant accumulation is active; metrics are tagged **`INSUFFICIENT_DATA`**.
