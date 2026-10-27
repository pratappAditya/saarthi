# Saarthi Release Installation & Portable Distribution Verification

## Overview
This document records the installation and distribution artifact validation for Saarthi `v0.5.0-rc2`.

---

## Distribution Artifact Summary

| Artifact | Type | Status | Size | SHA-256 Checksum |
| :--- | :--- | :--- | :--- | :--- |
| **`Saarthi-0.5.0-rc2-Portable.zip`** | Portable Archive | **VERIFIED (PASS)** | ~1.2 MB | `E7F1166215B2D0BC3A32D1EE51B31632BF7F3AA32A04CA574CD3E8928E44EA50` |
| **`release_manifest.json`** | Metadata | **VERIFIED (PASS)** | ~0.5 KB | `5BCC86651CCA6FB23C21FFFB03F10563FB1492003CD98A9EDF5FD0493B106ECA` |
| **`Saarthi-Setup-v0.5.0-rc2.exe`** | Windows Installer | **NOT TESTED** | N/A | Inno Setup compiler (`ISCC.exe`) not installed on environment. |

---

## Portable Distribution Test Results
- Portable zip archive extracted and tested on workstation.
- Application backend, static frontend dist, and launcher execute cleanly.
- Preserves `E:\Saarthi\data` (SQLite database) and `E:\Saarthi\models` (GGUF weights).
