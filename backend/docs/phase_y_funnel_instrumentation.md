# Phase Y Funnel Instrumentation & Denominator Specification

## Overview
Instrumentation audit of canonical experiment events and correct variant conversion denominator calculations.

---

## Canonical Experiment Event Stream (Rule Y.5)
The following 10 events are recorded into `operational_telemetry.log`:
1. `EXPERIMENT_ASSIGNED`
2. `DOCUMENT_GENERATED`
3. `DOCUMENT_PREVIEWED`
4. `WATERMARKED_EXPORT`
5. `UPGRADE_PROMPT_SHOWN`
6. `PRICING_VIEWED`
7. `CHECKOUT_STARTED`
8. `PAYMENT_SUCCESS`
9. `LICENSE_ACTIVATED`
10. `CLEAN_EXPORT`

---

## Variant Conversion Denominator Standard (Rule Y.6)
- **Standard**: Variant conversion rates MUST be calculated using eligible exposed participants within that specific variant as the denominator.
- **Formula**:
  $$\text{Variant Paid Conversion} = \frac{\text{Successful Payments in Variant}}{\text{Eligible Exposed Users in Variant}}$$
- **Forbidden Practice**: Calculating variant conversion by dividing variant payments by total overall beta users is explicitly prohibited.
