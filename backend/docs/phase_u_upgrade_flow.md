# Phase U Upgrade Flow & Entitlement Governance

## Overview
Detailed specification of entitlement state transitions, seamless watermark removal, and authoritative backend licensing evaluation.

---

## Entitlement Transition Matrix

| Current License Plan | `requires_watermark` | Max Applications / Mo | Re-Export Watermark Behavior |
| :--- | :--- | :--- | :--- |
| **FREE** | `True` | 3 | Watermark appended (`Created with Saarthi`) |
| **STUDENT** | `False` | Unlimited (-1) | Seamlessly stripped via `WatermarkEngine.strip_watermark()` |
| **PERSONAL** | `False` | Unlimited (-1) | Seamlessly stripped via `WatermarkEngine.strip_watermark()` |
| **POWER** | `False` | Unlimited (-1) | Seamlessly stripped via `WatermarkEngine.strip_watermark()` |
| **CUSTOM** | `False` | Unlimited (-1) | Seamlessly stripped via `WatermarkEngine.strip_watermark()` |

---

## State Transition Rules
1. **Free → Paid (Student/Personal/Power/Custom)**:
   - License activation token cached locally.
   - Re-exporting previously watermarked documents authoritatively strips the footer without AI text re-generation.
2. **Paid → Expired / Suspended / Revoked**:
   - System reverts immediately to `FREE` entitlement fallback.
   - Export re-applies subtle watermark footer.
