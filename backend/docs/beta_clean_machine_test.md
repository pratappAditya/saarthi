# Master Beta Clean-Machine Test Procedure & Verification Log

## Overview
Reproducible 23-step clean Windows machine installation and user workflow validation procedure.

---

## Clean-Machine Test Protocol (Section 3)

| Step # | Test Phase | Required User Action / Validation | Status | Observation / Finding |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Clean Environment** | Fresh Windows x64 OS (No Python, No git, No dev secrets) | **REQUIRES_MANUAL_VALIDATION** | Manual VM execution target |
| **2** | **Installer Launch** | Double-click `Saarthi_Setup_v0.5.0-rc2.exe` | **REQUIRES_MANUAL_VALIDATION** | Standard Windows installer UI |
| **3** | **Installation** | Install to `%LocalAppData%\Programs\Saarthi` | **REQUIRES_MANUAL_VALIDATION** | Creates Start Menu shortcut |
| **4** | **First Launch** | Launch desktop app from Start Menu | **REQUIRES_MANUAL_VALIDATION** | Fast startup (< 1.5s) |
| **5** | **Ollama Onboarding** | Check local AI diagnostics (`/ollama/diagnostics`) | **PASS (Harness)** | Provides actionable guidance |
| **6** | **Model Setup** | Download target model (`llama3.2` / `qwen2.5`) | **PASS (Harness)** | Status transitions to `READY` |
| **7** | **Free Tier Default** | Initial user entitlement evaluates as `FREE` | **PASS (Harness)** | `requires_watermark = True` |
| **8** | **Resume Import** | Import user resume file (.pdf / .docx) | **PASS (Harness)** | Local file parser extracts text |
| **9** | **JD Analysis** | Paste job description & calculate ATS match | **PASS (Harness)** | Local model identifies keywords |
| **10** | **Resume Tailoring** | Generate ATS-optimized tailored resume | **PASS (Harness)** | Content tailored locally |
| **11** | **Watermarked Export** | Export tailored resume on Free plan | **PASS (Harness)** | Watermark footer injected |
| **12** | **Pricing View** | Open pricing modal | **PASS (Harness)** | Student ₹149/100, Personal ₹399 |
| **13** | **Checkout & Payment** | Initiate checkout & simulate test payment | **PASS (Harness)** | HMAC verification succeeds |
| **14** | **License Upgrade** | Verify license entitlement updates to paid | **PASS (Harness)** | Status transitions to `ACTIVE` |
| **15** | **Clean Re-Export** | Re-export previously generated document | **PASS (Harness)** | Watermark stripped seamlessly |
| **16** | **Job Tracker** | Add job application to tracker pipeline | **PASS (Harness)** | Application saved in SQLite |
| **17** | **Interview Prep** | Generate interview Q&A for application | **PASS (Harness)** | Q&A generated locally |
| **18** | **Browser Assistant** | Fill application form via assistant | **PASS (Harness)** | Requires explicit confirmation |
| **19** | **User Confirmation** | Confirm field fill (`confirmed_by_user=True`) | **PASS (Harness)** | Form filled; 0 auto-submits |
| **20** | **App Restart** | Close and relaunch application | **PASS (Harness)** | Data & license persist |
| **21** | **Data Persistence** | Check SQLite database integrity after reboot | **PASS (Harness)** | 0 data loss |
| **22** | **Uninstallation** | Run uninstaller from Windows Settings | **REQUIRES_MANUAL_VALIDATION** | Removes app files cleanly |
| **23** | **Data Isolation** | Verify user career documents remain intact | **PASS (Harness)** | User files preserved |
