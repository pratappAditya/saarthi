# Microsoft Store Clean-Machine Manual Validation Checklist

## Overview
Reproducible 21-step manual validation checklist for Microsoft Store beta testers deploying Saarthi on a clean Windows VM.

---

## 21-Step Validation Sequence (Section 18)

| Step # | Validation Target | Target Action | Status Tag |
| :--- | :--- | :--- | :--- |
| **1** | Clean Windows OS | Fresh x64 Windows 10/11 VM | `REQUIRES_MANUAL_VALIDATION` |
| **2** | Store App Install | Download & install via Store package | `REQUIRES_MANUAL_VALIDATION` |
| **3** | First Launch | Launch Saarthi from Start Menu | `REQUIRES_MANUAL_VALIDATION` |
| **4** | Backend Startup | Verify local FastAPI background server | `PASS (Harness)` |
| **5** | Ollama Detection | Detect local Ollama engine | `PASS (Harness)` |
| **6** | Nemotron Check | Query model status (`nemotron-3-nano:4b`)| `PASS (Harness)` |
| **7** | Nemotron Setup | Trigger automated model pull if missing | `PASS (Harness)` |
| **8** | Hardware Check | Verify system RAM ($\ge 8\text{ GB}$) | `PASS (Harness)` |
| **9** | Free Career Flow | Import resume & generate ATS score | `PASS (Harness)` |
| **10** | Watermarked Export | Export Free tier document with watermark | `PASS (Harness)` |
| **11** | Student Upgrade | Checkout & activate paid license | `PASS (Harness)` |
| **12** | Clean Re-Export | Re-export document without watermark | `PASS (Harness)` |
