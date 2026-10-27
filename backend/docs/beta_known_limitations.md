# Master Beta Known Limitations & User Troubleshooting Guide

## Overview
Documented operational limitations and support troubleshooting procedures for Saarthi `v0.5.0-rc2` beta testers.

---

## Documented Operational Limitations (Section 17, 22)
1. **Local Ollama Setup Latency**: First-time local AI model download (`llama3.2`) depends on user internet bandwidth. Actionable diagnostic state provided via `GET /api/ollama/diagnostics`.
2. **Hardware RAM Requirement**: Local AI inferencing requires $\ge 8\text{ GB}$ system RAM for optimal resume tailoring latency.
3. **Manual VM Validation Target**: Physical clean-machine deployment on un-configured Windows VMs requires manual tester verification (`B. CONDITIONALLY BETA READY`).
