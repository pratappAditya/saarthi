# Saarthi Clean-Machine Validation Record

## Overview
This document records the clean-machine deployment status for Saarthi `v0.5.0-rc2`.

---

## Clean-Machine Test Result
**STATUS: NOT TESTED**

### Explanation
Per Phase G validation guidelines (Sub-phase G.6):
> *"If no clean machine is available: mark: CLEAN MACHINE — NOT TESTED. Do NOT infer PASS from development-machine success."*

Because an isolated clean Windows virtual machine was not available in the current automated environment, this stage is accurately marked **NOT TESTED** to maintain 100% engineering honesty.

---

## Target Clean Machine Prerequisites
- Windows 10/11 64-bit
- Python 3.10+ runtime
- Ollama v0.32+ runtime
- Pre-downloaded model weights `nemotron-3-nano:4b`
