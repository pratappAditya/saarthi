import sqlite3
import json
import os
from typing import Dict, Any, Optional

from app.config.settings import settings
from app.db.connection import get_db_connection as _get_unified_conn

def get_db_connection(db_path: Optional[str] = None):
    return _get_unified_conn(db_path or settings.DATABASE_PATH)

def init_benchmark_table():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS hardware_benchmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                measured_tps REAL NOT NULL,
                eval_count INTEGER NOT NULL,
                eval_duration_ns INTEGER NOT NULL,
                benchmarked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def init_profile_table():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                location TEXT NOT NULL DEFAULT '',
                education_json TEXT NOT NULL DEFAULT '[]',
                skills_json TEXT NOT NULL DEFAULT '[]',
                experience_json TEXT NOT NULL DEFAULT '[]',
                projects_json TEXT NOT NULL DEFAULT '[]',
                links_json TEXT NOT NULL DEFAULT '{}',
                work_authorization TEXT NOT NULL DEFAULT 'Authorized to work',
                notice_period_days INTEGER NOT NULL DEFAULT 0,
                preferred_locations_json TEXT NOT NULL DEFAULT '[]',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    init_benchmark_table()

init_benchmark_table()
init_profile_table()

class ProfileRepository:
    @staticmethod
    def get_profile() -> Dict[str, Any]:
        with get_db_connection() as conn:
            row = conn.execute("SELECT * FROM user_profiles ORDER BY id DESC LIMIT 1").fetchone()
            if not row:
                return {
                    "full_name": "",
                    "email": "",
                    "phone": "",
                    "location": "",
                    "education": [],
                    "skills": [],
                    "experience": [],
                    "projects": [],
                    "links": {},
                    "work_authorization": "Authorized to work",
                    "notice_period_days": 0,
                    "preferred_locations": [],
                    "fact_source": "USER-PROVIDED FACT"
                }
            
            d = dict(row)
            return {
                "full_name": d.get("full_name", ""),
                "email": d.get("email", ""),
                "phone": d.get("phone", ""),
                "location": d.get("location", ""),
                "education": json.loads(d.get("education_json", "[]")),
                "skills": json.loads(d.get("skills_json", "[]")),
                "experience": json.loads(d.get("experience_json", "[]")),
                "projects": json.loads(d.get("projects_json", "[]")),
                "links": json.loads(d.get("links_json", "{}")),
                "work_authorization": d.get("work_authorization", "Authorized to work"),
                "notice_period_days": d.get("notice_period_days", 0),
                "preferred_locations": json.loads(d.get("preferred_locations_json", "[]")),
                "fact_source": "STORED PROFILE FACT"
            }

    @staticmethod
    def save_profile(data: Dict[str, Any]) -> Dict[str, Any]:
        full_name = str(data.get("full_name", "")).strip()
        email = str(data.get("email", "")).strip()
        phone = str(data.get("phone", "")).strip()
        location = str(data.get("location", "")).strip()
        education_json = json.dumps(data.get("education", []))
        skills_json = json.dumps(data.get("skills", []))
        experience_json = json.dumps(data.get("experience", []))
        projects_json = json.dumps(data.get("projects", []))
        links_json = json.dumps(data.get("links", {}))
        work_auth = str(data.get("work_authorization", "Authorized to work"))
        notice_period = int(data.get("notice_period_days", 0))
        preferred_locs_json = json.dumps(data.get("preferred_locations", []))

        with get_db_connection() as conn:
            # Upsert single user profile row
            existing = conn.execute("SELECT id FROM user_profiles LIMIT 1").fetchone()
            if existing:
                conn.execute("""
                    UPDATE user_profiles SET
                        full_name=?, email=?, phone=?, location=?,
                        education_json=?, skills_json=?, experience_json=?, projects_json=?,
                        links_json=?, work_authorization=?, notice_period_days=?, preferred_locations_json=?,
                        updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                """, (full_name, email, phone, location, education_json, skills_json,
                      experience_json, projects_json, links_json, work_auth, notice_period,
                      preferred_locs_json, existing["id"]))
            else:
                conn.execute("""
                    INSERT INTO user_profiles (
                        full_name, email, phone, location,
                        education_json, skills_json, experience_json, projects_json,
                        links_json, work_authorization, notice_period_days, preferred_locations_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (full_name, email, phone, location, education_json, skills_json,
                      experience_json, projects_json, links_json, work_auth, notice_period, preferred_locs_json))
            conn.commit()

        return ProfileRepository.get_profile()

    @staticmethod
    def clear_profile() -> Dict[str, Any]:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM user_profiles")
            conn.commit()
        return ProfileRepository.get_profile()


class BenchmarkRepository:
    @staticmethod
    def get_latest_benchmark(model_name: str = None) -> Optional[Dict[str, Any]]:
        with get_db_connection() as conn:
            if model_name:
                row = conn.execute("SELECT * FROM hardware_benchmarks WHERE model_name=? ORDER BY id DESC LIMIT 1", (model_name,)).fetchone()
            else:
                row = conn.execute("SELECT * FROM hardware_benchmarks ORDER BY id DESC LIMIT 1").fetchone()
            if not row:
                return None
            d = dict(row)
            return {
                "is_benchmarked": True,
                "measured_tps": round(d["measured_tps"], 2),
                "eval_count": d["eval_count"],
                "model_name": d["model_name"],
                "benchmarked_at": str(d["benchmarked_at"])
            }

    @staticmethod
    def save_benchmark(model_name: str, measured_tps: float, eval_count: int = 0, eval_duration_ns: int = 0) -> Dict[str, Any]:
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO hardware_benchmarks (model_name, measured_tps, eval_count, eval_duration_ns)
                VALUES (?, ?, ?, ?)
            """, (model_name, measured_tps, eval_count, eval_duration_ns))
            conn.commit()
        return BenchmarkRepository.get_latest_benchmark(model_name)

    @staticmethod
    def clear_benchmarks():
        init_benchmark_table()
        with get_db_connection() as conn:
            conn.execute("DELETE FROM hardware_benchmarks")
            conn.commit()


