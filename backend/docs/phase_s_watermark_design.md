# Phase S Document Watermarking Design & Entitlement Enforcement

## Overview
The free-tier watermark engine (`WatermarkEngine` in `app/licensing/watermark.py`) enforces a subtle, professional watermark on all generated/exported career documents (tailored resumes, cover letters) produced while a user is on the **FREE** plan entitlement.

## Watermark Text & Placement
- **Text**: `"Created with Saarthi • saarthi.ai"`
- **Markdown Format**: Appends `\n\n---\n* Created with Saarthi • saarthi.ai *\n`
- **HTML Format**: Appends a styled low-contrast footer (`<div style="font-size: 10px; color: #94a3b8; border-top: 1px solid #e2e8f0; text-align: center; margin-top: 30px;">...</div>`)
- **Guarantees**:
  - Does NOT cover or distort resume text, body content, contact info, or ATS keywords.
  - Does NOT alter original user source files or imported baseline resumes.
  - Excludes email drafts, calendar `.ics` files, chat messages, application tracker entries, and browser-filled form fields.

## Entitlement Matrix
| Plan | Entitlement `requires_watermark` | Watermark Applied |
| :--- | :--- | :--- |
| **FREE** | `True` | **YES** |
| **STUDENT** | `False` | **NO** |
| **PERSONAL / MONTHLY** | `False` | **NO** |
| **POWER / YEARLY** | `False` | **NO** |
| **CUSTOM** | `False` | **NO** |

## Upgrade & Expiration Behavior
- **FREE → PAID Upgrade**: Future exports are watermark-free. Previously generated content can be re-exported via `/api/career/export-document` without a watermark.
- **PAID → FREE Expiration**: Future exports receive the watermark. Files already saved on disk are never altered.
