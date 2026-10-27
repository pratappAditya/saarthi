# Saarthi AI Operating Companion — Windows Release & Operations Guide

**Release Version:** 1.0.0-beta.1 (Build x64)  
**Distribution Target:** Windows 10/11 64-bit  
**Publisher:** Trovane Technologies  
**Artifact Package:** `release/windows/Saarthi-Setup-x64.exe`  

---

## 1. System Requirements & Baseline

| Component | Minimum Requirement | Recommended Specification |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 64-bit (Version 1803 / Build 17134+) | Windows 11 64-bit (Latest update) |
| **Architecture** | x86_64 / x64 | x86_64 / x64 |
| **System Memory (RAM)**| 6 GB | 16 GB+ |
| **Storage Space** | 600 MB for application binaries | 10 GB+ (if hosting local 8B LLM models) |
| **Web Runtime** | Microsoft Edge WebView2 Evergreen Runtime | Pre-installed on Windows 10/11 |
| **Optional Local GPU** | None (CPU inference supported) | NVIDIA RTX (4GB+ VRAM) for local Nemotron |

---

## 2. Installation Procedures

### 2.1 Interactive Graphical Setup Wizard
1. Double-click `Saarthi-Setup-x64.exe` (or `Saarthi-v1.0.0-beta.1-Setup.exe`).
2. If Windows SmartScreen displays an *Unrecognized App* banner (expected for initial beta releases prior to commercial EV code-signing), click **More Info** -> **Run anyway**.
3. Choose the destination directory (Default: `%LOCALAPPDATA%\Programs\Saarthi`).
4. Select optional shortcuts (Desktop and Start Menu).
5. Click **Install**. The wizard unpacks the distribution binaries, configures runtime paths, and sets up Add/Remove Programs registration.
6. Upon completion, choose **Launch Saarthi**.

### 2.2 Unattended / Silent Installation (For Enterprise & Automated QA)
Run from PowerShell or Command Prompt:
```powershell
# Default destination (%LOCALAPPDATA%\Programs\Saarthi)
.\Saarthi-Setup-x64.exe /S

# Or custom destination
.\Saarthi-Setup-x64.exe /S /DIR="C:\Tools\Saarthi"
```

---

## 3. Data Isolation, Upgrade Safety & Uninstallation

### 3.1 Data Isolation Architecture
All user-specific data is strictly isolated from application binaries:
- **Application Binaries:** `%LOCALAPPDATA%\Programs\Saarthi\` (read-only execution)
- **User Data & Databases:** `%LOCALAPPDATA%\Saarthi\`
  - `saarthi.db`: SQLite database storing candidate resumes, parsed facts, STAR stories, application pipeline stages, and local preferences.
  - `logs\desktop.log`: Local runtime logs with automated credential redaction.
  - `resumes\`: Locally uploaded PDF and DOCX resume source documents.

### 3.2 Upgrade Procedure
Upgrading Saarthi is seamless and non-destructive:
1. Run the newer version installer (`Saarthi-v1.X.X-Setup.exe`).
2. Install over the existing directory.
3. The installer overwrites application binaries only.
4. On first launch, Saarthi inspects the existing `saarthi.db` and applies non-destructive column migrations automatically. **No user career data, star answers, or settings are ever lost.**

### 3.3 Uninstallation
Saarthi can be uninstalled via Windows **Settings -> Apps -> Installed Apps** or by running `uninstall.bat`:
- **Default Behavior (Data Preservation):** Deletes application binaries, registry entries, and shortcuts. Preserves `%LOCALAPPDATA%\Saarthi` so candidate career history is not accidentally destroyed.
- **Complete Purge:** To remove all application files AND all local databases/user history, run:
  ```cmd
  "%LOCALAPPDATA%\Programs\Saarthi\uninstall.bat" --delete-data
  ```

---

## 4. AI Inference Configuration

### 4.1 Local-First Privacy Engine (Ollama / Nemotron)
Saarthi natively prioritizes local privacy without requiring cloud API keys or external transmission:
1. Install [Ollama for Windows](https://ollama.com/download/windows).
2. Pull the recommended local model:
   ```cmd
   ollama run nemotron-mini:latest
   ```
3. Saarthi automatically probes `http://127.0.0.1:11434`. When detected, local model cards appear in the UI under **Model Hub**. All cover letter generation, resume tailoring, and interview simulations execute 100% locally on your hardware.

### 4.2 Cloud AI Provider Configuration (BYOK Mode)
If the user prefers cloud intelligence (OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet, Google Gemini 1.5 Pro):
1. In the Saarthi desktop interface, navigate to **Settings -> AI Intelligence Vault**.
2. Input the user-owned API key (`sk-...` or Gemini key).
3. The key is encrypted locally using the Windows Data Protection API (DPAPI) and never transmitted to Trovane Technologies servers.

---

## 5. Billing Sandbox & Entitlement Verification

### 5.1 Architecture & Anti-Tamper Shield
Paid tier access (e.g. Pro, Executive) is governed by server-signed entitlement certificates:
- Editing local SQLite fields (`UPDATE users SET subscription_plan = 'pro'`) is rejected by the licensing engine.
- Checkout is initiated via the Saarthi secure billing bridge:
  1. Desktop requests checkout session -> Backend generates Razorpay Order with server-side secret.
  2. The secure checkout URL opens in the user's default browser.
  3. Razorpay webhooks post signed HMAC-SHA256 events to `https://api-staging.saarthi.trovanetech.com/api/billing/webhook`.
  4. The backend verifies payment and issues an Ed25519-signed license certificate to the desktop client.

### 5.2 Sandbox Verification Workflow
To verify billing in staging sandbox mode:
- Test Card: Razorpay standard test credentials (e.g. `4111 1111 1111 1111`, any future expiry, OTP `123456`).
- Webhook signature validation test: `backend/tests/test_razorpay_verification.py` validates that forged signatures and tampered amounts immediately fail closed.

---

## 6. Clean-Machine Validation Checklist

For QA engineers validating the installer on a fresh Windows system:

1. **Clean Baseline:** Ensure Python, Node.js, and git are NOT in the system PATH.
2. **Execute Installer:** Run `Saarthi-Setup-x64.exe /S` (silent) or via GUI.
3. **Verify Installation:**
   - Shortcut exists on Desktop: `%USERPROFILE%\Desktop\Saarthi.lnk`
   - Registry registered: `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\Saarthi`
4. **Launch Application:**
   - Launch via shortcut or run `"%LOCALAPPDATA%\Programs\Saarthi\Saarthi.exe"`.
   - Verify native WebView2 window renders Saarthi UI.
   - Verify `saarthi.db` is created in `%LOCALAPPDATA%\Saarthi\`.
5. **Headless Smoke Test:**
   ```cmd
   "%LOCALAPPDATA%\Programs\Saarthi\Saarthi.exe" --smoke-test
   ```
   *Expected Output:* `SMOKE TEST PASSED: Saarthi Desktop backend and database initialized successfully.`
6. **Graceful Shutdown & Single Instance:**
   - Close window -> backend thread shuts down cleanly.
   - Double-launching while running pops single-instance informational notice.
7. **Clean Uninstallation:**
   - Run `uninstall.bat` -> binary directory is removed, shortcuts removed.
   - Verify `%LOCALAPPDATA%\Saarthi\saarthi.db` is preserved.

---

## 7. Troubleshooting & FAQ

- **Q: SmartScreen warning "Windows protected your PC"?**  
  *A:* This is standard behavior for newly compiled beta executables before EV code-signing reputation is accumulated. Click **More Info** -> **Run anyway**.
- **Q: "Saarthi requires Microsoft Edge WebView2 Runtime"?**  
  *A:* Download and run the Evergreen Bootstrapper from [Microsoft's official portal](https://developer.microsoft.com/en-us/microsoft-edge/webview2/).
- **Q: Port 8000 is occupied by another tool?**  
  *A:* Saarthi features automated port-hunting (testing 8000–8050) and will automatically bind to the first unallocated TCP port.
