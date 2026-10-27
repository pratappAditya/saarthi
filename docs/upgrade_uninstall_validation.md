# Saarthi Upgrade, Uninstall & Clean Machine Audit

## Overview
This document records data preservation rules, clean machine status, and uninstallation policies for Saarthi `v0.5.0-rc2`.

---

## Data Preservation & Uninstall Policy

| Target Asset | Path | Uninstall Behavior | Status |
| :--- | :--- | :--- | :--- |
| **Application Executable** | `{autopf}\Saarthi` | Removed | VERIFIED |
| **SQLite Database** | `E:\Saarthi\data\database\saarthi.db` | **PRESERVED** | VERIFIED |
| **Model Weights** | `E:\Saarthi\models\` | **PRESERVED** | VERIFIED |
| **Workspace Data** | `E:\Saarthi\` | **PRESERVED** | VERIFIED |

---

## Upgrade & Clean Machine Status
- **Upgrade Test**: **NOT TESTED** (Requires compiled installer executable).
- **Clean Machine Test**: **NOT TESTED** (Requires clean isolated virtual machine).
