# Phase Y Experiment Eligibility & Assignment Integrity Audit

## Overview
Audit of experiment participant eligibility criteria, deterministic hash assignment rules, and immutability invariants.

---

## 1. Eligible Experiment Participant Criteria (Rule Y.3)
A user is classified as an eligible experiment participant if and only if all 10 criteria are satisfied:
1. **Genuine External User**: Real public beta candidate (non-synthetic).
2. **Not Internal QA**: Excludes developer/testing accounts.
3. **Not Developer Account**: Excludes local debug instances.
4. **Not Staging Account**: Excludes staging test harnesses.
5. **Not Automated Test**: Excludes pytest or browser test automation sessions.
6. **Not Duplicate Identity**: Excludes multi-account logins on the same device fingerprint.
7. **Exposed to Exactly One Variant**: Assigned to `CONTROL`, `VARIANT_A`, `VARIANT_B`, or `VARIANT_C`.
8. **Document Generated / Exported**: Candidate created or exported a tailored resume or cover letter.
9. **Assignment Persisted**: Server-side hash assignment remained unchanged throughout the session.
10. **Remained Eligible**: Did not trigger security revocation or developer debug flags.

---

## 2. Server-Side Assignment Invariants (Rule Y.4)
- **Methodology**: `WatermarkEngine.get_experiment_variant(user_id)` uses SHA-256 hash modulo calculation.
- **Invariants**:
  - Deterministic and stable per anonymous user ID.
  - Zero reassignment permitted (`Rule Y.11`).
  - Zero frontend-controlled assignment or manual override allowed.
  - Zero cross-variant contamination detected.
