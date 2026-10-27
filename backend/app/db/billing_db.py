import sqlite3
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from app.db.connection import get_db_connection, with_db_retry

def init_billing_tables():
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Email Verification Tokens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verification_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                email TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                is_used INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # Password Reset Tokens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reset_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                is_used INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # Two-Factor Auth Architecture
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS two_factor_auth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                secret_key TEXT NOT NULL,
                is_enabled INTEGER NOT NULL DEFAULT 0,
                backup_codes_json TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # Organizations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                owner_id TEXT NOT NULL DEFAULT '',
                subscription_plan TEXT NOT NULL DEFAULT 'TEAMS',
                seat_limit INTEGER NOT NULL DEFAULT 5,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Non-destructive migrations for organizations
        try:
            cols = [row["name"] for row in cursor.execute("PRAGMA table_info(organizations)").fetchall()]
            if "owner_id" not in cols:
                cursor.execute("ALTER TABLE organizations ADD COLUMN owner_id TEXT DEFAULT ''")
            if "subscription_plan" not in cols:
                cursor.execute("ALTER TABLE organizations ADD COLUMN subscription_plan TEXT DEFAULT 'TEAMS'")
            if "seat_limit" not in cols:
                cursor.execute("ALTER TABLE organizations ADD COLUMN seat_limit INTEGER DEFAULT 5")
        except Exception:
            pass

        # Organization Members
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organization_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                org_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'MEMBER',
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                joined_at TEXT NOT NULL,
                UNIQUE(org_id, user_id),
                FOREIGN KEY(org_id) REFERENCES organizations(org_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # Organization Invitations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS organization_invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invite_id TEXT UNIQUE NOT NULL,
                org_id TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'MEMBER',
                token TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY(org_id) REFERENCES organizations(org_id)
            )
        """)

        # Subscriptions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subscription_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                org_id TEXT,
                plan_name TEXT NOT NULL,
                plan_version TEXT NOT NULL DEFAULT 'v1.0',
                provider TEXT NOT NULL DEFAULT 'RAZORPAY',
                provider_sub_id TEXT,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                seat_count INTEGER NOT NULL DEFAULT 1,
                price_per_unit INTEGER NOT NULL DEFAULT 0,
                total_amount INTEGER NOT NULL DEFAULT 0,
                current_period_start TEXT NOT NULL,
                current_period_end TEXT NOT NULL,
                cancel_at_period_end INTEGER NOT NULL DEFAULT 0,
                canceled_at TEXT,
                ended_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # Non-destructive migrations for subscriptions
        try:
            sub_cols = [row["name"] for row in cursor.execute("PRAGMA table_info(subscriptions)").fetchall()]
            if "plan_version" not in sub_cols:
                cursor.execute("ALTER TABLE subscriptions ADD COLUMN plan_version TEXT DEFAULT 'v1.0'")
        except Exception:
            pass

        # Subscription Events Timeline
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscription_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                subscription_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                details_json TEXT DEFAULT '{}',
                created_at TEXT NOT NULL
            )
        """)

        # Payments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payment_id TEXT UNIQUE NOT NULL,
                order_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                org_id TEXT,
                plan_name TEXT NOT NULL DEFAULT 'PERSONAL',
                seats INTEGER NOT NULL DEFAULT 1,
                provider TEXT NOT NULL DEFAULT 'RAZORPAY',
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL DEFAULT 'INR',
                status TEXT NOT NULL DEFAULT 'PAID',
                signature TEXT,
                receipt_url TEXT,
                created_at TEXT NOT NULL
            )
        """)

        # Non-destructive migrations for payments
        try:
            pay_cols = [row["name"] for row in cursor.execute("PRAGMA table_info(payments)").fetchall()]
            if "plan_name" not in pay_cols:
                cursor.execute("ALTER TABLE payments ADD COLUMN plan_name TEXT DEFAULT 'PERSONAL'")
            if "seats" not in pay_cols:
                cursor.execute("ALTER TABLE payments ADD COLUMN seats INTEGER DEFAULT 1")
        except Exception:
            pass

        # Webhook / Payment Events (Idempotency Tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                provider TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                processed_at TEXT NOT NULL
            )
        """)

        # Invoices
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT UNIQUE NOT NULL,
                subscription_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                org_id TEXT,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL DEFAULT 'INR',
                status TEXT NOT NULL DEFAULT 'PAID',
                pdf_url TEXT,
                billing_reason TEXT DEFAULT 'SUBSCRIPTION_CYCLE',
                created_at TEXT NOT NULL
            )
        """)

        # Refunds
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS refunds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                refund_id TEXT UNIQUE NOT NULL,
                payment_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PROCESSED',
                created_at TEXT NOT NULL
            )
        """)

        # Billing Customers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing_customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT UNIQUE NOT NULL,
                user_id TEXT UNIQUE NOT NULL,
                org_id TEXT,
                provider TEXT NOT NULL DEFAULT 'RAZORPAY',
                provider_customer_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Billing Audit Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing_audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT UNIQUE NOT NULL,
                actor_id TEXT NOT NULL,
                user_id TEXT,
                org_id TEXT,
                action TEXT NOT NULL,
                details_json TEXT DEFAULT '{}',
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()

init_billing_tables()
