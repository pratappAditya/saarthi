# Saarthi Usage & Quota Architecture Specification

## Quota Tracking
Server-side quota tracking via `UsageService` monitors:
- Messages sent per day/month
- Agent TaskGraph executions
- Literature research queries
- Document ingestion & OCR pages
- Cloud AI provider calls vs Local Nemotron calls
- Storage vault utilization (GB)

## Server-Side Gating
When a quota limit is exceeded, the server returns HTTP 429 Too Many Requests with details on required plan upgrades.
