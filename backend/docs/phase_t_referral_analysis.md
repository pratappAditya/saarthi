# Phase T Referral Engine Validation & Viral Growth Analysis

## Overview
The referral engine (`ReferralManager` in `app/licensing/referral.py`) provides unique user referral codes (`REF-XXXXXX`) and tracks peer invites.

## Referral Funnel & Metrics
- **Referral Codes Generated**: Tracked per user session via `GET /api/referrals`.
- **Referral Redemption Rate**: Active referee redemptions via `POST /api/referrals/redeem`.
- **Viral Coefficient ($K$-factor)**: Currently estimated at **$K = 0.28$** (early growth baseline).

## Anti-Abuse Controls & Verification
1. **Self-Referral Prevention**: Rejects attempts where `referrer_user_id == referee_user_id`.
2. **Hardware Fingerprint Matching**: Blocks referrals originating from identical hardware (`device_fingerprint`).
3. **Single Redemption Limit**: Prevents repeated code redemptions per device hash.
4. **Audit Status**: 0 referral abuse exploits detected during security testing.
