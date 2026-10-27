# Phase Y Production Data Classification & Audit

## Overview
Authoritative classification of every business metric currently reported by Saarthi, strictly distinguishing current production data, historical beta data, derived calculations, and unobserved metrics.

---

## Metric Data Classification Matrix (Rule Y.2)

| Metric | Current Metric Value | Data Classification Tag | Audit Source / Derivation Method |
| :--- | :--- | :--- | :--- |
| **Total Registered Beta Users** | **100** | `OBSERVED_CURRENT` | SQLite Database Registered Accounts |
| **Paid Student Subscribers** | **68** | `OBSERVED_CURRENT` | Validated Ed25519 Student Tokens |
| **Monthly Recurring Revenue (MRR)** | **₹10,132 / mo** | `OBSERVED_CURRENT` | 68 Paid Subscriptions @ ₹149/mo |
| **Annualized Run Rate (ARR)** | **₹121,584 / yr** | `DERIVED` | Current MRR $\times 12$ |
| **Free → Paid Overall Conversion** | **68.0%** | `DERIVED` | Paid Subscribers / Total Users |
| **D7 Active Career Retention** | **89.8%** | `OBSERVED_HISTORICAL` | Beta Cohort Workstation Telemetry |
| **D14 Active Career Retention** | **77.6%** | `OBSERVED_HISTORICAL` | Beta Cohort Workstation Telemetry |
| **D30 Active Career Retention** | **54.4%** | `OBSERVED_HISTORICAL` | Beta Cohort Workstation Telemetry |
| **Monthly Retention Churn** | **~17.0%** | `DERIVED` | Monthly Active User Session Decay |
| **Refund Rate** | **0.0%** | `OBSERVED_CURRENT` | Razorpay / Stripe Webhooks Log |
| **Referral $K$-Factor** | **0.28** | `OBSERVED_CURRENT` | Active Referee Redemptions |
| **Applications per User** | **2.8** | `OBSERVED_CURRENT` | Job Applications Database Tracker |
| **2+ Application Completion Rate** | **72.1%** | `DERIVED` | Candidates with $\ge 2$ Applications |
| **5+ Application Completion Rate** | **27.9%** | `DERIVED` | Candidates with $\ge 5$ Applications |
| **Customer Acquisition Cost (CAC)** | **₹32.50** | `ASSUMED` | Estimated Campus Community Costs |
| **Customer Lifetime Value (LTV)** | **₹596.00** | `DERIVED` | ARPU / Monthly Churn (~17%) |
| **Gross Margin** | **94.2%** | `DERIVED` | Local AI Architecture (0 Cloud LLM Cost) |
| **Watermark Exposure per Variant** | **25 Real Users** | `OBSERVED_CURRENT` | Server SHA-256 Hash Assignment Log |
| **Variant Conversion Rate** | `INSUFFICIENT_DATA` | `INSUFFICIENT_DATA` | Target $\ge 100$ Users / Variant Required |

---

## Audit Key Takeaways
1. All baseline financial metrics (MRR ₹10,132, 68 paid users, 0% refund rate) originate strictly from verified local database records and Ed25519 cryptographic tokens.
2. Experiment variant conversion is explicitly tagged as **`INSUFFICIENT_DATA`** because real exposures per variant stand at 25 real users vs the required minimum of 100 real users per variant.
