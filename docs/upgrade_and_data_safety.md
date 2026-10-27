# Upgrade and Data Safety Architecture

**Project:** Saarthi AI Assistant  
**Version:** 0.5.0-rc2  
**Last Updated:** 2026-08-18  

---

## 1. Directory & Storage Separation

Saarthi strictly decouples immutable application binaries from mutable persistent state, user data, models, and license caches.

| Storage Domain | Target Directory Path | Deletion on Uninstall? | Overwritten on Reinstall/Upgrade? |
| :--- | :--- | :--- | :--- |
| **Application Binaries** | `C:\Program Files\Saarthi` | **YES** | **YES** (Overwritten cleanly) |
| **User Data & SQLite DB** | `E:\Saarthi\data` | **NO** (Preserved) | **NO** (Schema migrated safely) |
| **Local LLM Models** | `E:\Saarthi\models` | **NO** (Preserved) | **NO** (Intact) |
| **System & App Logs** | `E:\Saarthi\data\logs` | **NO** (Preserved) | **NO** (Appended) |
| **License State Cache** | `E:\Saarthi\data\license_cache.json` | **NO** (Preserved) | **NO** (Follows Recovery Policy) |

---

## 2. Safety Mechanisms

### 2.1 Installer / Uninstaller Guarantees
Inno Setup (`installer/saarthi_setup.iss`) manages binary files under `{app}` (`C:\Program Files\Saarthi`).
The uninstall procedure (`usPostUninstall`) explicitly excludes `E:\Saarthi\data` and `E:\Saarthi\models` from removal. Uninstalling Saarthi removes only the program executable, dependencies, and desktop shortcuts.

### 2.2 Upgrade Workflow
When upgrading from an earlier build (e.g., RC1/RC2 to final distribution):
1. The installer replaces application files in `{app}` cleanly.
2. The FastAPI backend starts and checks `E:\Saarthi\data\database\saarthi.db`.
3. Database migrations run safely without clearing existing tables or chat logs.
4. User memory embeddings and conversation histories remain 100% available.

### 2.3 Reinstall Safety
Reinstalling over an existing installation replaces binary files but leaves user databases, settings, license tokens, and downloaded model weights untouched.

### 2.4 License Cache Recovery Policy
If local license state files or database caches are deleted:
- The customer can re-enter their valid License Key.
- Client license manager contacts the vendor control plane.
- The control plane re-authenticates the license, re-binds the device signature, and issues a freshly signed Ed25519 license token without requiring repurchasing.
