# Phase Z Metric Reconciliation & Derivation Documentation

## Overview
Comprehensive metric reconciliation documenting exact source variables, formulas, and data quality tags for all derived and reported commercial metrics.

---

## Derived & Computed Metric Formulas

### 1. Annualized Run Rate (ARR)
- **Tag**: `DERIVED`
- **Formula**:
  $$\text{ARR} = \text{MRR} \times 12 = ₹10,132 \times 12 = ₹121,584 / \text{year}$$
- **Source Variables**: Active paid Student subscriptions count ($N = 68$) in `saarthi.db` $\times$ Student monthly price ($₹149$).

### 2. Free → Paid Conversion Rate
- **Tag**: `DERIVED`
- **Formula**:
  $$\text{Overall Conversion} = \frac{\text{Paid Student Subscriptions}}{\text{Total Registered Beta Accounts}} = \frac{68}{100} = 68.0\%$$
- **Source Variables**: Paid accounts count ($68$) / Total registered accounts ($100$) in `saarthi.db`.

### 3. Customer Lifetime Value (LTV)
- **Tag**: `DERIVED`
- **Formula**:
  $$\text{ARPU} = \frac{\text{MRR}}{\text{Total Users}} = \frac{₹10,132}{100} = ₹101.32$$
  $$\text{LTV} = \frac{\text{ARPU}}{\text{Monthly Churn Rate}} = \frac{₹101.32}{0.17} = ₹596.00$$
- **Source Variables**: ARPU ($₹101.32$) and Monthly Session Decay Rate ($17.0\%$).

### 4. Gross Margin
- **Tag**: `DERIVED`
- **Formula**:
  $$\text{Gross Margin} = \frac{\text{Revenue} - \text{Cloud LLM Inferencing Cost}}{\text{Revenue}} = \frac{₹10,132 - ₹588}{₹10,132} = 94.2\%$$
- **Source Variables**: Revenue ($₹10,132$), Telemetry log server cost ($₹588$), Cloud LLM Inferencing Cost ($₹0.00$ - Local Ollama execution).
