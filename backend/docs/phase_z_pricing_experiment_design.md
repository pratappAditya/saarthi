# Phase Z Locked Pricing Experiment Architecture & Design

## Overview
Design specification for the upcoming multi-region pricing experiment.
*Important Notice*: In accordance with Phase Z rules, this pricing experiment architecture is prepared for experiment readiness ONLY and is **NOT active in production** during Phase Z.

---

## Locked Commercial Pricing Matrix (Hypothesis Target)

### 1. India Region (INR)
- **FREE**: ₹0 / month (Watermarked document exports)
- **STUDENT (Control)**: ₹149 / month | ₹1,299 / year
- **STUDENT (Treatment)**: ₹100 / month | ₹899 / year
- **PERSONAL**: ₹399 / month | ₹3,499 / year
- **POWER**: ₹799 / month | ₹6,999 / year

### 2. International Region (USD)
- **FREE**: $0 / month (Watermarked document exports)
- **STUDENT**: $1.50 / month | $12.99 / year
- **PERSONAL**: $5 / month | $44.99 / year
- **POWER**: $10 / month | $89.99 / year

---

## Primary Business Metric (Rule Z.7)
- **Primary Metric**: **Revenue per Eligible Exposed User** ($\text{RPEU}$)
  $$\text{RPEU} = \frac{\text{Total Revenue Generated in Variant}}{\text{Eligible Exposed Users in Variant}}$$
- **Strategic Purpose**: Evaluates whether lowering the Student price to ₹100 / $1.50 generates higher overall economic volume than ₹149 without damaging cohort LTV or retention.

---

## Retention Guardrails & Decision Rules (Rule Z.8)
- **Guardrail**: The treatment pricing (₹100 Student) cannot be declared a winner if it causes:
  1. Material deterioration in D30 active career retention.
  2. Drop in candidates completing 2+ job applications.
