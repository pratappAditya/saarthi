# Phase AA Conversion Analysis

## Overview
Analysis of signup-to-paid conversion across experiment variants.

---

## Variant Conversion Audit
- **Standard**: Paid conversion rate is computed as:
  $$\text{Variant Conversion} = \frac{\text{Attributable Paid Subscriptions in Variant}}{\text{Eligible Exposed Users in Variant}}$$
- **Current Findings**: Real exposure accumulation is ongoing; conversion rates are tagged **`INSUFFICIENT_DATA`**. Synthetic test payments and unit tests are strictly excluded from production denominators.
