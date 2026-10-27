# Phase AB Financial Baseline & Unit Economics Report

## Overview
Financial baseline, MRR run rate, ARPU, CAC, LTV, and local AI gross margin metrics.

---

## Financial Baseline Metrics Table

| Financial Indicator | Measured Baseline Value | Data Quality Tag | Calculation / Derivation Method |
| :--- | :--- | :--- | :--- |
| **Total Registered Beta Accounts** | 100 | `OBSERVED_CURRENT` | SQLite Database User Accounts |
| **Paid Student Subscribers** | 68 | `OBSERVED_CURRENT` | Cached Ed25519 Student Tokens |
| **Monthly Recurring Revenue (MRR)** | **₹10,132 / mo** | `OBSERVED_CURRENT` | 68 Paid Student Subscriptions @ ₹149/mo |
| **Annualized Run Rate (ARR)** | **₹121,584 / yr** | `DERIVED` | Observed MRR $\times 12$ |
| **ARPU** | **₹101.32** | `DERIVED` | Total MRR / Total Accounts |
| **CAC** | **₹32.50** | `ASSUMED` | Estimated Organic Campus Marketing Spend |
| **LTV** | **₹596.00** | `DERIVED` | ARPU / Monthly Churn (~17.0%) |
| **LTV / CAC Ratio** | **18.3x** | `DERIVED` | High organic student efficiency |
| **Gross Margin** | **94.2%** | `DERIVED` | Local Ollama AI Inferencing (0 server LLM cost) |
