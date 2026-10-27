import os
import shutil
import sqlite3
import datetime
import logging
from typing import List, Dict, Any, Optional
from app.config.settings import settings
from app.db.connection import get_db_connection

logger = logging.getLogger("app.db.backup")

class DatabaseBackupEngine:
    """
    Automated SQLite Database Snapshot, Integrity Check, and Disaster Recovery Engine.
    """
    @staticmethod
    def get_backup_dir() -> str:
        backup_dir = os.path.join(settings.SAARTHI_DATA_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    @classmethod
    def create_backup(cls, tag: str = "manual") -> Dict[str, Any]:
        """
        Creates an online SQLite snapshot using `sqlite3.Connection.backup()`.
        """
        db_path = settings.DATABASE_PATH
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file does not exist at {db_path}")

        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"saarthi_db_{tag}_{timestamp}.bak"
        backup_path = os.path.join(cls.get_backup_dir(), filename)

        try:
            with get_db_connection(db_path) as source_conn:
                with sqlite3.connect(backup_path) as dest_conn:
                    source_conn.backup(dest_conn)
            
            size_mb = round(os.path.getsize(backup_path) / (1024 * 1024), 3)
            logger.info(f"Database backup created successfully: {backup_path} ({size_mb} MB)")

            return {
                "status": "success",
                "filename": filename,
                "backup_path": backup_path,
                "size_mb": size_mb,
                "timestamp": timestamp,
                "tag": tag
            }
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}", exc_info=True)
            raise

    @classmethod
    def list_backups(cls) -> List[Dict[str, Any]]:
        """
        Lists all available database backup files sorted by creation time (newest first).
        """
        backup_dir = cls.get_backup_dir()
        files = [f for f in os.listdir(backup_dir) if f.endswith(".bak")]
        backups = []
        for f in files:
            p = os.path.join(backup_dir, f)
            stat = os.stat(p)
            backups.append({
                "filename": f,
                "path": p,
                "size_mb": round(stat.st_size / (1024 * 1024), 3),
                "created_at": datetime.datetime.fromtimestamp(stat.st_ctime, datetime.timezone.utc).isoformat()
            })
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups

    @classmethod
    def check_integrity(cls, db_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs SQLite integrity checks (`PRAGMA quick_check`).
        """
        path = db_path or settings.DATABASE_PATH
        try:
            with get_db_connection(path) as conn:
                res = conn.execute("PRAGMA quick_check;").fetchall()
                messages = [row[0] for row in res]
                is_ok = len(messages) == 1 and messages[0].lower() == "ok"
                return {
                    "healthy": is_ok,
                    "status": "OK" if is_ok else "CORRUPTED",
                    "messages": messages
                }
        except Exception as e:
            return {
                "healthy": False,
                "status": "ERROR",
                "messages": [str(e)]
            }

    @classmethod
    def restore_backup(cls, filename: str) -> Dict[str, Any]:
        """
        Restores database from a verified `.bak` file.
        """
        backup_path = os.path.join(cls.get_backup_dir(), filename)
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file {filename} does not exist.")

        # Verify backup integrity first
        check = cls.check_integrity(backup_path)
        if not check["healthy"]:
            raise ValueError(f"Backup file {filename} failed integrity check: {check['messages']}")

        # Create a safety pre-restore backup of the current database
        if os.path.exists(settings.DATABASE_PATH):
            cls.create_backup(tag="pre_restore_safety")

        # Copy backup file onto active database path
        shutil.copy2(backup_path, settings.DATABASE_PATH)
        logger.info(f"Database successfully restored from {filename}")

        return {
            "status": "success",
            "message": f"Database successfully restored from {filename}",
            "restored_from": filename
        }
