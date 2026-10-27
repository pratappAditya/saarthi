# Saarthi — Closed Beta Installation & Setup Guide

**Version**: `v1.0.0-beta.1`  
**Target OS**: Windows 11 (64-bit AMD64)  

---

## System Requirements

| Component | Minimum Requirement | Recommended Requirement |
| :--- | :--- | :--- |
| **Operating System** | Windows 11 Home / Pro (build 22000+) | Windows 11 Pro (build 22621+) |
| **Processor** | 4-Core Intel or AMD CPU | 8-Core Intel Core i7 / Ryzen 7 CPU |
| **System RAM** | 6.0 GB RAM minimum (`STANDARD` Tier) | 16.0 GB+ RAM (`SUPER` / `ULTRA` Tiers) |
| **GPU / VRAM** | Integrated GPU (Intel UHD / AMD Radeon) | Dedicated NVIDIA GPU (4GB+ VRAM) |
| **Free Storage** | 10.0 GB free SSD storage | 25.0 GB free NVMe SSD storage |

---

## First-Run Setup Walkthrough

1. **Download & Extract**: Extract `saarthi-closed-beta-v1.0.0-beta.1.zip` to a local folder (e.g. `C:\Program Files\Saarthi`).
2. **Launch Application**: Run `Saarthi.exe`.
3. **Onboarding Consent**:
   - Review the **Local AI & Privacy Notice**.
   - Confirm consent for local Ollama engine initialization.
4. **Automated Hardware Scan**:
   - Saarthi automatically inspects your CPU cores, RAM, GPU, VRAM, and storage.
   - Recommends the optimal NVIDIA Nemotron model tier (`STANDARD`, `PRO`, `SUPER`, or `ULTRA`).
5. **Local Nemotron Setup**:
   - Saarthi installs/configures local Ollama if missing.
   - Downloads the recommended Nemotron model with live progress updates.
   - Performs a local health check to verify prompt execution.
6. **Saarthi Ready**: Start optimizing resumes, generating cover letters, and tracking job applications offline!
