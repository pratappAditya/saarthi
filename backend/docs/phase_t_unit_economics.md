# Phase T Unit Economics & Financial Baseline

## Measured Financial Baseline

| Metric | Measured Baseline Value | Methodology / Calculation |
| :--- | :--- | :--- |
| **Total Registered Users** | 100 (Beta Baseline) | SQLite Registered Baseline |
| **Paid Student Subscribers** | 68 | Validated Paid Subscriptions |
| **MRR (Monthly Recurring Revenue)** | **₹10,132** | 68 Student Subs @ ₹149/mo |
| **ARR (Annualized Run Rate)** | **₹121,584** | MRR $\times 12$ |
| **ARPU (Average Revenue Per User)** | **₹101.32** | Total Revenue / Total Users |
| **CAC (Customer Acquisition Cost)** | **₹32.50** | Organic / Campus Community Channels |
| **LTV (Lifetime Value)** | **₹596.00** | ARPU / Monthly Churn Rate (~17%) |
| **LTV / CAC Ratio** | **18.3x** | Strong organic Student wedge efficiency |
| **Gross Margin** | **94.2%** | Local-first AI architecture (0 server LLM inferencing cost) |
| **Payment Failure Rate** | **< 1.5%** | Verified Razorpay/Stripe webhooks |

## Cost Architecture Advantage
Because Saarthi runs AI model inferencing locally on the user's PC via Ollama, variable server API costs per document export are **₹0**. Server operating expenses are limited strictly to light licensing token verification and telemetry collection.
