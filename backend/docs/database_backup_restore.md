# Saarthi Database Backup & Restore Guide

## Overview
This document specifies the procedure for backing up and restoring the Saarthi SQLite database without interrupting active sessions or causing database corruption.

---

## Database Architecture
- **Location**: `E:\Saarthi\data\database\saarthi.db`
- **Tables**: `memories`, `chat_history`
- **Indexes**: `idx_messages_session`

---

## Safe Backup Procedure

### 1. File Copy Backup (Offline / Idle)
```powershell
Copy-Item "E:\Saarthi\data\database\saarthi.db" "E:\Saarthi\data\database\saarthi_backup.db"
```

### 2. SQLite Online Vacuum Backup (Live Database)
```powershell
sqlite3 "E:\Saarthi\data\database\saarthi.db" ".backup 'E:\Saarthi\data\database\saarthi_backup.db'"
```

---

## Safe Restore Procedure

1. Stop the Saarthi backend service (`app.main`).
2. Verify backup file integrity:
```powershell
sqlite3 "E:\Saarthi\data\database\saarthi_backup.db" "PRAGMA quick_check;"
```
3. Copy backup file back to primary database path:
```powershell
Copy-Item "E:\Saarthi\data\database\saarthi_backup.db" "E:\Saarthi\data\database\saarthi.db" -Force
```
4. Restart Saarthi backend service.
