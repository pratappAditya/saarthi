# Final Microsoft Store Clean-Machine Release Candidate Checklist

## Overview
21-step manual validation protocol for Microsoft Store beta testers deploying Saarthi `v0.5.0-rc2` on a clean Windows machine.

---

## Clean-Machine Protocol Matrix (Section 18)

| Step # | User Journey Stage | Target Action | Status Tag |
| :--- | :--- | :--- | :--- |
| **1** | **Clean Environment** | Fresh Windows 10/11 x64 VM (No dev environment) | `REQUIRES_MANUAL_VALIDATION` |
| **2** | **Store Installation** | Install via Microsoft Store beta package | `REQUIRES_MANUAL_VALIDATION` |
| **3** | **First Launch** | Launch Saarthi desktop app from Start Menu | `REQUIRES_MANUAL_VALIDATION` |
| **4** | **Backend Connection** | Connect to local FastAPI backend (`127.0.0.1:8000`)| `PASS (Harness)` |
| **5** | **Ollama Diagnostics** | Check local Ollama engine status | `PASS (Harness)` |
| **6** | **Nemotron Check** | Verify `nemotron-3-nano:4b` readiness | `PASS (Harness)` |
| **7** | **Free Career Workflow** | Import resume & generate ATS score | `PASS (Harness)` |
| **8** | **Watermarked Export** | Export Free tier resume with watermark | `PASS (Harness)` |
| **9** | **Student Purchase** | Execute test payment & receive license | `PASS (Harness)` |
| **10** | **Clean Re-Export** | Re-export document without watermark | `PASS (Harness)` |
| **11** | **Browser Assistant** | Fill job application via assistant | `PASS (Harness)` |
| **12** | **Confirmation Security**| Confirm form fill (`confirmed_by_user=True`) | `PASS (Harness)` |
