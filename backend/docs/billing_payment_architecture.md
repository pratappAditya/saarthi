# Saarthi Billing, Payment & Subscription Architecture

## Executive Summary
Saarthi implements a multi-provider billing framework designed to support Razorpay and Stripe with backend-enforced entitlement logic. Payments are never trusted from the frontend alone; all plan upgrades, renewals, and feature unlocks require HMAC-SHA256 signature verification and idempotent server-side processing.

---

## 1. Canonical Plan Pricing Catalog

Saarthi operates under six canonical subscription plans:

| Plan Name | Price | Billing Frequency | Seat Limit | Key Capabilities |
|---|---|---|---|---|
| `FREE` | ₹0 | Lifetime | 1 User | Core assistant features, base rate limits |
| `STUDENT` | ₹99 | Monthly | 1 User | Higher context, academic routines, priority queuing |
| `PERSONAL` | ₹399 | Monthly | 1 User | Unlimited automation, custom agent skills, full memory retention |
| `POWER` | ₹799 | Monthly | 1 User | Maximum token context, multi-modal workflows, fast execution |
| `TEAMS` | ₹699 | Per user / month | Custom | Multi-tenant organization workspace, admin governance, shared routines |
| `ENTERPRISE` | Custom | Custom / Annual | Custom | Dedicated infrastructure, custom SLA, high-concurrency autonomy |

---

## 2. Subscription Lifecycle State Machine

```
   [ Checkout Order Created ]
               │
               ▼
   [ Gateway Payment Executed ]
               │
               ▼
   [ Server Verification (HMAC-SHA256) ]
               │
               ├────────────────────────────┐
       Success │                            │ Failure
               ▼                            ▼
      [ Subscription ACTIVE ]       [ Order FAILED ]
               │
   ┌───────────┴───────────┐
   │                       │
Renewal Success      Renewal Failure
   │                       │
   ▼                       ▼
[ ACTIVE ]          [ PAST_DUE ]
                           │
                     7-Day Grace Period
                           │
             ┌─────────────┴─────────────┐
       Payment Recovered           Grace Expired
             │                           │
             ▼                           ▼
        [ ACTIVE ]                  [ CANCELED ]
                                         │
                                         ▼
                               [ Downgraded to FREE ]
```

---

## 3. Idempotent Webhook Reconciliation

To prevent double-billing and duplicate processing during network retries, all webhooks pass through an idempotency gate (`payment_events` table):

1. **Payload Hash & Event ID Check**: Incoming webhook contains a unique provider event ID (`event_id`).
2. **Database Lookup**: `BillingService.process_idempotent_webhook()` queries `payment_events`. If `event_id` exists, processing immediately terminates with `{"status": "duplicate", "processed": false}`.
3. **HMAC Signature Validation**: Webhook signatures are verified against `RAZORPAY_WEBHOOK_SECRET` or `STRIPE_WEBHOOK_SECRET`.
4. **State Transition**: Subscription state is updated, and an entitlement change event is dispatched.

---

## 4. Invoicing & Billing Audit
- **Invoices**: Automatically created upon successful payment verification (`INV-YYYYMM-XXXX`). Invoices record line items, tax components, currency (INR), and plan details.
- **Refunds**: Admin-initiated refunds immediately transition subscription status to `CANCELED` and downgrade user entitlements back to `FREE`.
