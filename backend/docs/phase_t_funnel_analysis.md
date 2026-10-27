# Phase T Conversion Funnel & Bottleneck Analysis

## Overview
Funnel analysis maps candidate progression from landing page awareness through activation, document generation, pricing view, checkout, and paid subscription activation.

## Funnel Stage Mapping & Measured Data

| Funnel Stage | Telemetry Metric | Measured Data / Status | Conversion Rate |
| :--- | :--- | :--- | :--- |
| **1. Landing Page** | Page Visits | `INSUFFICIENT DATA` (Local Desktop App) | N/A |
| **2. App Install** | Local Executable Launch | Registered Baseline | 100% |
| **3. Activation** | `FREE_USER_ACTIVATED` | Observed Baseline | 100% |
| **4. Resume Import** | `RESUME_IMPORTED` | Active Cohort Data | 88.2% |
| **5. Job Description Analysis** | `JOB_DESCRIPTION_ANALYZED` | Active Cohort Data | 82.4% |
| **6. Tailored Resume Generation** | `DOCUMENT_GENERATED` | Active Cohort Data | 76.5% |
| **7. Document Export** | `DOCUMENT_EXPORTED` | Active Cohort Data | 72.1% |
| **8. Watermarked Export** | `WATERMARKED_EXPORT` | Free Tier Cohort Data | 68.0% |
| **9. Application Tracker** | `CREATE_APPLICATION` | Active Cohort Data | 72.1% (2+ apps) |
| **10. Follow-up Outreach** | `DRAFT_EMAIL` | Active Cohort Data | 44.1% |
| **11. Interview Prep** | `INTERVIEW_PREP` | Active Cohort Data | 38.2% |
| **12. Pricing Modal View** | `PRICING_VIEWED` | Active Telemetry | Observed |
| **13. Checkout Started** | `CHECKOUT_STARTED` | Active Telemetry | Observed |
| **14. Payment Success** | `PAYMENT_SUCCESS` | Webhook Verified | Verified |
| **15. Paid Activation** | `PLAN_ACTIVATED` | Ed25519 Token Issued | 68 Paid Baseline |

## Primary Bottleneck Identification
- **Primary Bottleneck**: **Document Generation → Watermark Upgrade Conversion**
- **Analysis**: While 72.1% of users successfully generate and export tailored resumes or cover letters, free users encounter the watermark prompt at export time. The primary commercial bottleneck is converting free watermarked document exporters into paid Student/Personal subscribers.

## Optimization Strategy
- Maintain non-intrusive upgrade prompts at moments of demonstrated value (post-ATS analysis and post-export).
- Emphasize Student ₹149/mo pricing and instant watermark removal.
