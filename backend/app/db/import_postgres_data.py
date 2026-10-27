"""
PostgreSQL Data Importer Tool for Saarthi
=========================================
Imports JSON dump data into a target PostgreSQL database instance.
"""
import os
import json
import argparse
import psycopg2
import psycopg2.extras
from typing import Dict, Any

def import_json_to_postgres(json_path: str, db_url: str):
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON dump file not found at {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        dump_data: Dict[str, Any] = json.load(f)

    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    for table, rows in dump_data.items():
        if not rows:
            continue

        columns = list(rows[0].keys())
        col_names = ", ".join(columns)
        val_placeholders = ", ".join(["%s"] * len(columns))
        sql = f"INSERT INTO {table} ({col_names}) VALUES ({val_placeholders}) ON CONFLICT DO NOTHING;"

        inserted = 0
        for row in rows:
            values = tuple(row[c] for c in columns)
            try:
                cursor.execute(sql, values)
                inserted += 1
            except Exception as e:
                print(f"Warning inserting into {table}: {e}")
                conn.rollback()

        conn.commit()
        print(f"Imported {inserted}/{len(rows)} records into PostgreSQL table '{table}'")

    conn.close()
    print(f"\n[SUCCESS] PostgreSQL import complete from {json_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import JSON dump into PostgreSQL database")
    parser.add_argument("--input", default="data/dump.json", help="Path to input JSON dump file")
    parser.add_argument("--db-url", required=True, help="PostgreSQL connection string (e.g. postgresql://user:pass@host:5432/dbname)")
    args = parser.parse_args()

    import_json_to_postgres(args.input, args.db_url)
