# SAARTHI AI COMPANION — MICROSOFT STORE SUBMISSION CHECKLIST & LAUNCH GUIDE
**Product:** Saarthi AI Companion  
**Publisher:** Trovane Technologies  
**Primary Deliverable:** `release/windows/Saarthi-v1.0.0-Store.msix`  
**Alternative Deliverable:** `release/windows/Saarthi-Setup-x64.exe` (Win32 Store App Submission)  
**Date:** October 2026  
**Status:** RELEASE CANDIDATE READY FOR PARTNER CENTER SUBMISSION

---

## 1. Store Product Identity & Metadata

| Metadata Field | Value | Notes |
|---|---|---|
| **App Name** | Saarthi AI Companion | Reserved in Partner Center |
| **Package Identity Name** | `TrovaneTechnologies.SaarthiAICompanion` | In `AppxManifest.xml` |
| **Publisher Display Name**| Trovane Technologies | Verified Publisher |
| **Publisher ID (CN)** | `CN=TrovaneTechnologies` | Placeholder: Replace with Partner Center Publisher CN before final Store submission |
| **Version** | `1.0.0.0` | Semantic Version 1.0.0 |
| **Primary Category** | Productivity | Business / Personal Productivity |
| **Secondary Category** | Developer Tools / Career | Job search, career tailoring, executive AI |
| **Age Rating** | 12+ (IARC Certified) | User-generated prompts; content filtering enabled |
| **Pricing** | Free with Optional In-App Subscriptions | Free tier includes complete on-device AI |

---

## 2. Store Listing Content

### 2.1 Short Description (100 characters max)
> Your private on-device AI operating companion for career growth, STAR coaching, and executive briefings.

### 2.2 Full Description
```
Saarthi is an on-device AI Operating Companion engineered for ambitious executives, developers, and knowledge professionals. Powered by NVIDIA Nemotron open models running locally on your PC, Saarthi delivers real-time executive briefings, ATS resume tailoring, STAR interview coaching, and career strategy with complete data privacy.

KEY CAPABILITIES:

1. LOCAL NVIDIA NEMOTRON AI ENGINE
• Zero cloud API costs and zero private data transmission for local inference.
• Hardware-aware model selection: Saarthi analyzes your CPU, RAM, and GPU VRAM to configure the optimal Nemotron model (3B Light, Mini 4B, 3.5 Bolt, or 8B Ultra).
• On-device model provisioning: Models are downloaded and verified directly within the application. No command line required.

2. EXECUTIVE BRIEFING & STRATEGY
• Daily priority dashboard, agenda summarization, and task orchestration.
• Contextual memory vault that preserves your career achievements and work history offline.

3. ATS RESUME TAILORING & PORTFOLIO
• Side-by-side job description alignment with measurable keyword density improvements.
• Real-time diffs, version management, and instant PDF/Word export.

4. STAR INTERVIEW COACHING
• Structured multi-turn behavioral interview simulations (Situation, Task, Action, Result).
• Live constructive feedback on confidence, conciseness, and impact metrics.

5. ENTERPRISE PRIVACY & LOCAL PERSISTENCE
• On-device SQLite storage for all personal documents and career dossiers.
• Offline-first design: Core intelligence remains fully operational without an internet connection.
```

---

## 3. Capabilities & Justifications for Store Reviewers

| Capability | Scope | Reviewer Justification |
|---|---|---|
| `runFullTrust` | Restricted | Required because Saarthi is a Win32 desktop application running an embedded Python/PyWebView shell and local loopback server (`127.0.0.1`). |
| `internetClient` | Standard | Required for optional cloud syncing, in-app model weight downloads, and checking for software updates. |
| `privateNetworkClientServer`| Standard | Required for loopback socket communication between the PyWebView client interface and local FastAPI backend engine (`127.0.0.1:8000–8050`). |

---

## 4. Visual Assets Inventory

All assets are packaged in `installer/msix/Assets/` and embedded in `Saarthi-v1.0.0-Store.msix`:
- `Square44x44Logo.png` (44x44 App list icon)
- `Square150x150Logo.png` (150x150 Medium tile icon)
- `Wide310x150Logo.png` (310x150 Wide tile icon with branded background)
- `StoreLogo.png` (50x50 Microsoft Store catalog logo)
- `SplashScreen.png` (620x300 Launch splash screen)

---

## 5. Privacy, Support, and Legal URLs

- **Privacy Policy:** `https://trovanetech.com/privacy`
- **Terms of Service:** `https://trovanetech.com/terms`
- **Support Contact:** `support@trovanetech.com`
- **Support Portal:** `https://trovanetech.com/support`

---

## 6. Pre-Submission Execution Checklist (Owner Actions)

- [x] Build and validate clean MSIX package (`release/windows/Saarthi-v1.0.0-Store.msix`).
- [x] Verify zero large model weights embedded in base package (122.91 MB clean package).
- [x] Verify AppxBlockMap.xml and cryptographic SHA-256 hashes.
- [x] Run full regression test suite (240+ automated unit, integration, and security tests).
- [ ] **Partner Center Setup (Owner Action):**
  1. Log into [Microsoft Partner Center](https://partner.microsoft.com/dashboard).
  2. Reserve the app name: `Saarthi AI Companion`.
  3. Navigate to **Product Identity** and copy:
     - Package/Identity/Name
     - Package/Identity/Publisher (e.g., `CN=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`)
     - Package/Properties/PublisherDisplayName
  4. If Partner Center values differ from placeholders, update `installer/msix/AppxManifest.xml` and re-run:
     `python release/build_msix_package.py`
  5. Upload `release/windows/Saarthi-v1.0.0-Store.msix` to the Partner Center package submission page.
  6. Fill in Store listing description, upload screenshots, complete the IARC age rating questionnaire, and submit for certification.
