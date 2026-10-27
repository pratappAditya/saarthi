"""
SQLite Data Exporter Tool for Saarthi
=====================================
Exports all persistent SQLite tables to a JSON dump file for PostgreSQL migration.
"""
import os
import json
import sqlite3
import argparse
from typing import Dict, Any

TABLES_TO_EXPORT = [
    "users",
    "sessions",
    "devices",
    "organizations",
    "organization_members",
    "subscriptions",
    "payments",
    "payment_orders",
    "payment_events",
    "invoices",
    "admin_users",
    "admin_sessions",
    "admin_audit_log",
    "feature_flags",
    "maintenance_mode",
    "tool_policies",
    "support_feedback",
    "agent_tasks",
    "scheduled_jobs",
    "resumes",
    "churn_feedback"
]

def export_sqlite_to_json(db_path: str, output_path: str) -> Dict[str, Any]:
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"SQLite database file not found at {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    dump_data = {}

    for table in TABLES_TO_EXPORT:
        try:
            cursor = conn.cursor()
            rows = cursor.execute(f"SELECT * FROM {table}").fetchall()
            dump_data[table] = [dict(r) for r in rows]
            print(f"Exported {len(dump_data[table])} rows from table '{table}'")
        except Exception as e:
            print(f"Notice: Could not export table '{table}': {e}")
            dump_data[table] = []

    conn.close()

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dump_data, f, indent=2, default=str)

    print(f"\n[SUCCESS] Successfully exported SQLite database to {output_path}")
    return dump_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Saarthi SQLite database to JSON")
    parser.add_argument("--db-path", default="data/database/saarthi.db", help="Path to SQLite database file")
    parser.add_argument("--output", default="data/dump.json", help="Path to output JSON dump file")
    args = parser.parse_args()

    export_sqlite_to_json(args.db_path, args.output)
