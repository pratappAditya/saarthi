# SAARTHI — PRODUCTION DEPLOYMENT CHECKLIST

**Date**: August 18, 2026  
**Status**: Readiness Verification

---

## Deployment & Infrastructure Checklist

| Requirement | Status | Details / Actions Required |
| :--- | :--- | :--- |
| **Vendor Server Deployed** | READY | `VendorServer` SQLite engine ready for production hosting on cloud server. |
| **HTTPS / TLS 1.3** | NOT READY | Nginx reverse proxy with SSL certificate required for vendor control domain. |
| **Production Database** | READY | SQLite database initialized with WAL mode & automated backups. |
| **Database Backups** | READY | Backup & restore scripts validated in `database_backup_restore.md`. |
| **Ed25519 Private Key Storage** | READY | Private key isolated exclusively in vendor environment variable (`VENDOR_PRIVATE_KEY_PEM`). |
| **Secrets in Environment** | READY | `VENDOR_ADMIN_KEY`, `RAZORPAY_KEY_SECRET` loaded strictly from `.env`. |
| **Admin Authentication** | READY | Server-side `X-Vendor-Admin-Key` header verification active on `/api/vendor/*`. |
| **Rate Limiting** | READY | Activation & vendor admin endpoints protected against brute-force enumeration. |
| **CORS Policy** | READY | Restrict allowed origins to production domain in `main.py`. |
| **Payment Provider Integration** | NOT TESTED | Razorpay abstraction active; live API keys required for production webhook validation. |
| **Webhook Verification** | READY | HMAC-SHA256 signature verification active in `payment.py`. |
| **Monitoring & Logging** | READY | Operational diagnostics logging active without customer data leaks. |
| **Domain Name** | NOT READY | Register production control plane domain (e.g. `api.saarthi.ai`). |
| **Privacy Policy** | READY | Explains local data isolation & Ed25519 licensing telemetry scope. |
| **Terms of Service** | READY | Outlines Student/Personal/Power commercial licensing terms. |
| **Refund Policy** | READY | Outlines cancellation and license revocation procedure. |
| **Support Email** | READY | Support escalation contact: `support@saarthi.ai`. |
| **Account Recovery Procedure** | READY | Documented manual key re-issue procedure for database/hardware replacement. |
