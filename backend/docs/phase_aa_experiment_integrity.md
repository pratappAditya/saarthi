# Phase AA Pricing Experiment Integrity & Assignment Audit

## Overview
Audit of server-side deterministic assignment, user isolation, and existing customer protection invariants.

---

## Assignment System Architecture (Rule AA.2)
- **Methodology**: `WatermarkEngine.get_pricing_experiment_variant(user_id)` uses SHA-256 hash modulo calculation (`user_id + "_pricing"`).
- **Variants**:
  1. `STUDENT_CONTROL_149` (Student ₹149/mo)
  2. `STUDENT_TREATMENT_100` (Student ₹100/mo)

---

## Existing Customer Protection Invariant (Rule AA.12)
- **Invariant**: Existing ₹149 subscribers retain their existing subscription and entitlement status without automatic price changes.
- **Scope**: The pricing experiment applies strictly to eligible NEW Student pricing exposures.
