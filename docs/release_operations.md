# Saarthi Release Operations Guide

## Overview
This document describes release operations, artifact publishing, and verification procedures for Saarthi `v0.5.0-rc2`.

---

## Release Directory Structure
```text
E:\Saarthi\release\
├── Saarthi-0.5.0-rc2-Portable.zip  # Standalone portable distribution archive
├── release_manifest.json           # Release metadata & version definitions
└── SHA256SUMS.txt                  # SHA-256 integrity checksums
```

---

## Verifying Release Artifact Integrity
To independently verify the release artifact checksums on Windows PowerShell:

```powershell
Get-FileHash -Path "E:\Saarthi\release\Saarthi-0.5.0-rc2-Portable.zip" -Algorithm SHA256
```

Expected output hash: `E7F1166215B2D0BC3A32D1EE51B31632BF7F3AA32A04CA574CD3E8928E44EA50`
