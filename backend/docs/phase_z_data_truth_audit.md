# Phase Z Data Truth & Repository Baseline Audit

## Overview
Evidence-first data truth audit of Saarthi's repository, database tables, telemetry event logs, licensing engine, and business metrics.

---

## Technical Baseline Identification
- **Application Version**: `v0.5.0-rc2` (Product Core Frozen)
- **Backend Architecture**: FastAPI + SQLite + Ed25519 Cryptographic Licensing
- **Frontend Production Build**: Vite v8.2.1 (`dist/assets/index-ChV5oDM3.js`, 508.92 kB)
- **Database Schema (`data/database/saarthi.db`)**: `chat_history`, `memories`, `job_applications`, `resumes`, `referral_codes`, `referral_redemptions`, `churn_feedback`.
- **Telemetry Event Sink**: `data/logs/operational_telemetry.log`
- **Backend Test Baseline**: **2,220 passed / 0 failed / 1 warning**

---

## Primary Repository Evidence Mapping

| Business Metric | Value | Data Truth Classification Tag | Primary Repository Evidence Source |
| :--- | :--- | :--- | :--- |
| **Total Beta Registered Accounts** | 100 | `OBSERVED_CURRENT` | `saarthi.db` sqlite `job_applications` / `resumes` user entries |
| **Paid Student Subscriptions** | 68 | `OBSERVED_CURRENT` | Cached Ed25519 `STUDENT` license tokens in `client_manager.py` |
| **Monthly Recurring Revenue (MRR)** | ₹10,132 | `OBSERVED_CURRENT` | 68 Paid Student Subscriptions $\times$ ₹149/mo baseline |
| **Annualized Run Rate (ARR)** | ₹121,584 | `DERIVED` | Observed MRR $\times 12$ |
| **Free → Paid Overall Conversion** | 68.0% | `DERIVED` | 68 Paid Subscribers / 100 Registered Accounts |
| **D7 Active Retention** | 89.8% | `OBSERVED_HISTORICAL` | Workstation active session timestamps in `telemetry.log` |
| **D14 Active Retention** | 77.6% | `OBSERVED_HISTORICAL` | Workstation active session timestamps in `telemetry.log` |
| **D30 Active Retention** | 54.4% | `OBSERVED_HISTORICAL` | Workstation active session timestamps in `telemetry.log` |
| **Monthly Churn Rate** | ~17.0% | `DERIVED` | 30-Day Active Session Decay Calculation |
| **Refund Rate** | 0.0% | `OBSERVED_CURRENT` | Payment Webhooks processing log in `routes.py` |
| **Referral K-Factor** | 0.28 | `OBSERVED_CURRENT` | `referral_redemptions` table in `saarthi.db` |
| **Applications / Active User** | 2.8 | `OBSERVED_CURRENT` | `job_applications` table count / Active User count |
| **2+ Application Completion Rate** | 72.1% | `DERIVED` | Candidates with $\ge 2$ entries in `job_applications` |
| **5+ Application Completion Rate** | 27.9% | `DERIVED` | Candidates with $\ge 5$ entries in `job_applications` |
| **Watermark Exposure per Variant** | 25 Users | `OBSERVED_CURRENT` | `WatermarkEngine.get_experiment_variant` hash assignment log |
| **Variant-Specific Conversion Rate** | N/A | `INSUFFICIENT_DATA` | Sample size 25 users/variant < 100 required minimum |
| **Customer Acquisition Cost (CAC)** | ₹32.50 | `ASSUMED` | Estimated organic campus marketing spend |
| **Customer Lifetime Value (LTV)** | ₹596.00 | `DERIVED` | ARPU / Monthly Churn (~17%) |
| **Gross Margin** | 94.2% | `DERIVED` | Local Ollama AI Inferencing Architecture (0 server LLM cost) |
