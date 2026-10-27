# Saarthi Billing Architecture Specification

## Overview
Saarthi implements product-side billing state management via `licensing_service.py` and `account_api.py`.

## Canonical Plan Catalog
- `free`: Saarthi Free (₹0)
- `student`: Saarthi Student (₹99/mo)
- `personal`: Saarthi Personal (₹399/mo)
- `power`: Saarthi Power (₹799/mo)
- `teams`: Saarthi Teams (₹699/user/mo, Commercially Frozen)
- `enterprise`: Saarthi Enterprise (Custom, Commercially Frozen)

## Subscription Lifecycle
1. **Plan Hydration**: `GET /api/account/plan` returns active subscription metadata.
2. **Entitlement Refresh**: `POST /api/account/plan/upgrade` refreshes user capability flags upon license key activation.
3. **Usage Enforcement**: Server-side tracking via `UsageService` preventing over-quota requests.
