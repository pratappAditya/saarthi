# Phase S Monetization & Funnel Conversion Metrics

## Overview
Saarthi tracks real operational telemetry events to measure free-to-paid conversion and feature usage without logging any sensitive customer content.

## Tracked Events
1. `FREE_USER_ACTIVATED`
2. `RESUME_IMPORTED`
3. `JOB_DESCRIPTION_ANALYZED`
4. `ATS_ANALYSIS_COMPLETED`
5. `DOCUMENT_GENERATED`
6. `DOCUMENT_EXPORTED`
7. `WATERMARKED_EXPORT`
8. `PRICING_VIEWED`
9. `UPGRADE_PROMPT_SHOWN`
10. `CHECKOUT_STARTED`
11. `PAYMENT_SUCCESS`
12. `PAYMENT_FAILED`
13. `PLAN_ACTIVATED`

## Calculated Metrics Formulas
- **Watermark Exposure Rate**: `(WATERMARKED_EXPORT / DOCUMENT_EXPORTED) * 100`
- **Pricing View Rate**: `(PRICING_VIEWED / UPGRADE_PROMPT_SHOWN) * 100`
- **Checkout Conversion**: `(CHECKOUT_STARTED / PRICING_VIEWED) * 100`
- **Payment Conversion**: `(PAYMENT_SUCCESS / CHECKOUT_STARTED) * 100`
- **Free-to-Paid Conversion**: `(PLAN_ACTIVATED / FREE_USER_ACTIVATED) * 100`

## Empirical Data Handling
- Zero synthetic or manufactured historical metrics.
- Calculated directly from `data/logs/operational_telemetry.log` events via `GET /api/vendor/monetization-metrics`.
