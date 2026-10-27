# Saarthi Desktop Architecture & System Boundary Decision Record (ADR-004)

**Document Version:** 1.0.0-beta.1  
**Author:** Trovane Technologies Engineering Team  
**Date:** October 25, 2026  
**Status:** Approved & Implemented  

---

## 1. Executive Summary & Core Product Direction

**Saarthi AI Operating Companion is distributed primarily as an installable Windows x64 Desktop Application (`.exe`).**  
The React web interface runs embedded within a native Microsoft Edge WebView2 shell (managed by `pywebview`), powered by an in-process local Python backend and local SQLite database engine.

The hosted Saarthi cloud infrastructure (PostgreSQL, Redis, cloud AI routing, Razorpay billing webhooks, and the administrative control plane) serves strictly as **supporting cloud services** for authentication, multi-device synchronization, heavy AI routing, and subscription entitlement issuance.

---

## 2. Desktop vs. Cloud Boundary Matrix

| Component / Functionality | Execution Location | Storage / Persistence | Network Dependency | Security & Secret Boundary |
| :--- | :--- | :--- | :--- | :--- |
| **User Interface (React + Tailwind/Vite)** | Embedded Microsoft Edge WebView2 window via `pywebview` | Memory / Local Asset Cache | Completely Offline Capable | Zero client secrets; connects to `127.0.0.1:{local_port}` |
| **Local Desktop Server (`SaarthiDesktop.py`)** | In-process Python daemon running Uvicorn + FastAPI | Memory / Process Lifetime | None (binds to loopback `127.0.0.1`) | Redacting log formatter; runs under user permissions |
| **Candidate Resumes & Facts** | Local Desktop Backend | `%LOCALAPPDATA%\Saarthi\saarthi.db` (SQLite) | None (Local-First) | Local user isolation; zero unauthorized cloud transmission |
| **Job Applications & Pipeline** | Local Desktop Backend | `%LOCALAPPDATA%\Saarthi\saarthi.db` (SQLite) | None (Local-First) | Never transmitted to cloud unless user initiates sync |
| **STAR Stories & Mock Interviews** | Local Desktop Backend | `%LOCALAPPDATA%\Saarthi\saarthi.db` (SQLite) | None (Local-First) | Personal career history remains entirely on host machine |
| **Local AI Inference (Nemotron 8B/70B)** | Local Ollama Service (`127.0.0.1:11434`) | Host GPU VRAM / System RAM | Completely Offline Capable | Free; zero provider API keys required; 100% private |
| **Cloud AI Inference (OpenAI, Gemini, Anthropic)** | Hosted Saarthi Gateway or User-Configured BYOK | Cloud Provider Servers | Internet Required | **No provider API keys inside `.exe`**; keys stored in secure backend vault or user DPAPI |
| **Billing & Checkout (Razorpay)** | Initiated by Desktop via Browser; Processed by Backend | Cloud DB (PostgreSQL) + Razorpay Vault | Internet Required | **Razorpay Secret Key resides ONLY on trusted backend**; never in desktop binaries |
| **Entitlement Verification** | Issued by Cloud Backend; Verified Cryptographically | Signed Token in `%LOCALAPPDATA%\Saarthi` | Periodic Check (grace period offline) | **Tamper-Proof:** Local SQLite `pro` edits are ignored without valid backend signature |
| **Admin Control Plane** | Hosted Cloud Service (`admin-staging` / `admin`) | Cloud PostgreSQL | Staging VPS Only | Zero administrative tokens or bypasses bundled in client `.exe` |

---

## 3. Storage Hierarchy & Data Preservation Guarantees

### 3.1 Paths and Directories
1. **Application Binaries Directory:**  
   Default: `%LOCALAPPDATA%\Programs\Saarthi` (or `{autopf}\Saarthi` for system-wide installs).  
   *Contents:* `Saarthi.exe`, `_internal` runtime DLLs, Python libraries, compiled React static assets (`frontend/dist`), and `uninstall.bat`.  
   *Rule:* **Never store writable databases or user state here.**

2. **Per-User Persistent Data Directory:**  
   Path: `%LOCALAPPDATA%\Saarthi\`  
   *Subdirectories:*
   - `saarthi.db`: SQLite database holding resumes, applications, STAR interview questions, local memories, and user preferences.
   - `logs\desktop.log`: Local application and backend execution logs with automatic credential redaction.
   - `resumes\`: Locally parsed candidate resume documents (PDF, DOCX, TXT).
   - `vault\`: DPAPI-encrypted user tokens and locally stored BYOK keys.

### 3.2 Upgrade & Uninstallation Safety
- **Upgrades:** When an installer or patch runs, it replaces ONLY the application binary files in the installation folder. The database schema runs automatic non-destructive column migrations (`PRAGMA table_info` / `ALTER TABLE ADD COLUMN IF NOT EXISTS`) without dropping tables or clearing records.
- **Uninstallation:** The standard `uninstall.bat` or Add/Remove Programs action deletes only application binaries and shortcuts. `%LOCALAPPDATA%\Saarthi` is preserved by default to protect the user's hard-earned career records. A full wipe requires passing the `--delete-data` flag explicitly.

---

## 4. Cryptographic Licensing & Entitlement Model

### 4.1 Anti-Tampering Guarantee
A frequent vulnerability in local-first desktop apps is users editing SQLite (`UPDATE users SET subscription_plan = 'pro'`). Saarthi implements cryptographic immunity against this:
1. Paid features (e.g. unwatermarked PDF export, multi-application bulk auto-tailor, premium Nemotron-Ultra cloud routing) require an **Ed25519-signed Entitlement Certificate**.
2. When the user purchases a Pro or Career tier via Razorpay, the Saarthi cloud backend generates an HMAC/Ed25519 payload containing:
   ```json
   {
     "user_id": "usr_948f2...",
     "tier": "PRO",
     "valid_until": "2027-10-25T00:00:00Z",
     "device_fingerprint": "win-64-f982a...",
     "signature": "3f82a901c..."
   }
   ```
3. The local client verifies the cryptographic signature against the public key embedded in the binary. If the signature is absent or invalid, the desktop automatically falls back to the **Free Plan**, regardless of what local SQLite contains.

### 4.2 Offline Grace Period
If a licensed Pro user is offline (e.g. during a flight or interview preparation with no internet):
- The signed certificate remains valid until its embedded expiry date.
- No network call is required to unlock local features during this period.

---

## 5. Security & Secret Redaction Standard

1. **Zero Secret Bundling:**  
   The PyInstaller compilation bundle and `.exe` binaries are audited to ensure zero instances of:
   - OpenAI API keys (`sk-...`)
   - Anthropic API keys (`sk-ant-...`)
   - Google Gemini API keys (`AIza...`)
   - Razorpay Key Secrets (`rzp_secret_...`)
   - JWT Master Secrets
   - Cloud DB connection strings (`postgresql://...`)

2. **Secret Redaction in Logging:**  
   All local log entries written to `%LOCALAPPDATA%\Saarthi\logs\desktop.log` pass through `SecretRedactingFormatter`, which scrubs bearer tokens, password fields, API key patterns, and credit card numbers before writing to disk.

---

## 6. Environment Separation

To prevent accidental production pollution:
- **Development:** Uses local SQLite, local Ollama, and loopback mock providers.
- **Closed Beta (Current Release):** Uses local SQLite for career features, local Ollama for privacy, points to `api-staging.saarthi.trovanetech.com` for optional cloud AI sync and Razorpay sandbox testing.
- **Production (Post-Launch Gate):** Uses isolated production domain `api.saarthi.trovanetech.com` backed by dedicated PostgreSQL, production Razorpay credentials, and signed release certificates.
