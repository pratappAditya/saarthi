# Saarthi Safe Model Switch & Automatic Rollback Protocol

## Rollback Guarantee
When upgrading or switching models:
1. Active working model (`previous_model`) is preserved in memory and on disk.
2. Candidate model (`candidate_model`) is downloaded/pulled via Ollama.
3. Candidate model undergoes an automated inference health check.
4. If health check passes -> candidate model is activated as `active_model`.
5. If health check fails -> system triggers **automatic rollback**, restoring `previous_model` as `active_model`.
6. Saarthi remains 100% usable without leaving broken or unverified models active.
