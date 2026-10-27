# Saarthi Windows Installer Toolchain & Audit Record

## Overview
This document records the installer script audit and toolchain discovery for Saarthi `v0.5.0-rc2`.

---

## Toolchain & Compilation Audit

| Item | Status / Record | Notes |
| :--- | :--- | :--- |
| **Installer Script** | `installer/saarthi_setup.iss` | Verified syntax, shortcuts, uninstall preservation rules. |
| **Inno Setup Compiler (`ISCC.exe`)** | **NOT INSTALLED** | `ISCC.exe` not found on system PATH or Program Files. |
| **Installer Compilation** | **NOT TESTED** | Per Rule H.1 / H.3, compilation marked NOT TESTED. |
| **Executable Binary** | `release/Saarthi-0.5.0-rc2-Setup.exe` | **NOT TESTED** |

---

## Data & Model Isolation Rules
The Inno Setup script (`saarthi_setup.iss`) specifies that uninstallation and updates MUST NOT remove:
- `E:\Saarthi\data` (SQLite database `saarthi.db` & logs)
- `E:\Saarthi\models` (GGUF weights)
- Sandboxed workspace files
