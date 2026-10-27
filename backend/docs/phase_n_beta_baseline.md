# SAARTHI — PHASE N PAID BETA BASELINE

**Date**: August 18, 2026  
**Status**: FROZEN RELEASE BASELINE  
**Release Classification**: **PAID BETA ACTIVE**

---

## 1. Frozen Baseline Versions & Metadata

| Component | Version / Hash / Identifier | Baseline Status |
| :--- | :--- | :--- |
| **Application Version** | `v0.5.0-rc2` | FROZEN |
| **Frontend Build Hash** | Vite v8.2.1 (`index-BbgREu3g.js` / `index-CuJeqWjI.css`) | FROZEN |
| **Backend Framework** | FastAPI 0.110+ on Python 3.14.6 | FROZEN |
| **Database Schema** | SQLite Schema v3 (`job_applications`, `resumes`, `student_verifications`, `customers`, `licenses`, `device_activations`) | FROZEN |
| **Licensing Protocol** | Ed25519 Vendor-Signed Hardware Binding v1.0 | FROZEN |
| **Local LLM Engine** | Ollama (`nemotron-3-nano:4b` / `llama3.2:latest`) | FROZEN |
| **Installer Executable** | `installer/Saarthi_Setup_v0.5.0.exe` | FROZEN |
| **Portable ZIP Archive** | `dist/Saarthi_v0.5.0_Portable.zip` | FROZEN |

---

## 2. Security & Ed25519 Private Key Isolation Rules

1. **Vendor Control Plane Isolation**: The Ed25519 private signing key exists **EXCLUSIVELY** on the production Vendor Control Server (`api.saarthi.ai`).
2. **Client Binary Guarantee**: The private key is **NEVER** present in the Saarthi desktop client, installer `.iss`, portable ZIP, frontend build, customer machine, or public Git repository.
3. **Public Key Verification**: The desktop client contains **ONLY** the public key for verifying vendor signatures offline.
