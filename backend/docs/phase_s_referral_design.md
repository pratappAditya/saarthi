# Phase S Referral System Design & Anti-Abuse Controls

## Overview
The referral system (`ReferralManager` in `app/licensing/referral.py`) provides a privacy-safe mechanism for users to invite peers to Saarthi (`REF-XXXXXX`).

## Mechanism
1. User requests code: Unique referral code generated (`REF-XXXXXX`).
2. Friend redeems code: Rejection or activation recorded in SQLite database `referral_redemptions`.
3. Benefit issuance: Successful referral credits extended trial days or bonus features.

## Anti-Abuse Security Controls
- **Self-Referral Prevention**: Blocks redemption if referrer `user_id` matches referee `user_id`.
- **Hardware Fingerprint Matching**: Rejects referral if referrer device fingerprint matches referee device fingerprint.
- **Single Redemption Limit**: Prevents a device or user account from redeeming multiple referral codes.
- **Zero Privacy Exposure**: Referred user emails, names, or resume content are never exposed to the referrer.
