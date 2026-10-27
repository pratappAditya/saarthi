"""
Saarthi PostgreSQL DDL Schema Definition & Table Initializer
=============================================================
Provides production DDL SQL queries and automated schema initialization for PostgreSQL.
"""
import logging
from app.db.connection import get_db_connection

logger = logging.getLogger("app.db.postgres_schema")

POSTGRES_SCHEMA_SQL = """
-- 1. Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    full_name VARCHAR(255) DEFAULT '',
    is_verified INT NOT NULL DEFAULT 0,
    verification_token VARCHAR(255),
    reset_token VARCHAR(255),
    reset_token_expires TIMESTAMP WITH TIME ZONE,
    role VARCHAR(32) NOT NULL DEFAULT 'USER',
    subscription_plan VARCHAR(32) NOT NULL DEFAULT 'FREE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Sessions
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_id VARCHAR(64) NOT NULL,
    device_name VARCHAR(255) DEFAULT 'Desktop Workstation',
    ip_address VARCHAR(45) DEFAULT '127.0.0.1',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_active_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. Devices
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(64) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_fingerprint VARCHAR(255) DEFAULT '',
    device_name VARCHAR(255) NOT NULL DEFAULT 'Desktop Workstation',
    os_info VARCHAR(255) DEFAULT '',
    device_type VARCHAR(64) DEFAULT 'DESKTOP',
    first_seen TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    last_login TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3b. Login Attempts
CREATE TABLE IF NOT EXISTS login_attempts (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    attempts INT NOT NULL DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    last_attempt TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3c. Free Usage Quota
CREATE TABLE IF NOT EXISTS free_usage_quota (
    id SERIAL PRIMARY KEY,
    user_id_or_device VARCHAR(255) UNIQUE NOT NULL,
    request_count INT NOT NULL DEFAULT 0,
    token_count INT NOT NULL DEFAULT 0,
    daily_limit INT NOT NULL DEFAULT 30,
    cooldown_until TIMESTAMP WITH TIME ZONE,
    last_request_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. Organizations
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    org_id VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    owner_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    subscription_plan VARCHAR(32) NOT NULL DEFAULT 'TEAMS',
    seat_limit INT NOT NULL DEFAULT 5,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 5. Organization Members
CREATE TABLE IF NOT EXISTS organization_members (
    id SERIAL PRIMARY KEY,
    org_id VARCHAR(64) NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL DEFAULT 'MEMBER',
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    joined_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(org_id, user_id)
);

-- 6. Subscriptions
CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    subscription_id VARCHAR(64) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    org_id VARCHAR(64),
    plan_name VARCHAR(32) NOT NULL,
    provider VARCHAR(32) NOT NULL DEFAULT 'RAZORPAY',
    provider_sub_id VARCHAR(128),
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    seat_count INT NOT NULL DEFAULT 1,
    price_per_unit INT NOT NULL DEFAULT 0,
    total_amount INT NOT NULL DEFAULT 0,
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    cancel_at_period_end INT NOT NULL DEFAULT 0,
    canceled_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7. Payments
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    payment_id VARCHAR(128) UNIQUE NOT NULL,
    order_id VARCHAR(128),
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    org_id VARCHAR(64),
    provider VARCHAR(32) NOT NULL DEFAULT 'RAZORPAY',
    amount INT NOT NULL,
    currency VARCHAR(8) NOT NULL DEFAULT 'INR',
    status VARCHAR(32) NOT NULL DEFAULT 'PAID',
    signature VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 8. Payment Orders
CREATE TABLE IF NOT EXISTS payment_orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(128) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    org_id VARCHAR(64),
    provider VARCHAR(32) NOT NULL DEFAULT 'RAZORPAY',
    plan_name VARCHAR(32) NOT NULL,
    amount INT NOT NULL,
    currency VARCHAR(8) NOT NULL DEFAULT 'INR',
    status VARCHAR(32) NOT NULL DEFAULT 'CREATED',
    payment_id VARCHAR(128),
    signature VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 9. Payment Events
CREATE TABLE IF NOT EXISTS payment_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(128) UNIQUE NOT NULL,
    provider VARCHAR(32) NOT NULL DEFAULT 'RAZORPAY',
    event_type VARCHAR(128) NOT NULL,
    payload_json TEXT NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 10. Invoices
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    invoice_id VARCHAR(128) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    subscription_id VARCHAR(64),
    amount INT NOT NULL,
    currency VARCHAR(8) NOT NULL DEFAULT 'INR',
    status VARCHAR(32) NOT NULL DEFAULT 'PAID',
    pdf_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 11. Admin Users
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    admin_id VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'ADMIN',
    full_name VARCHAR(255) DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 12. Admin Sessions
CREATE TABLE IF NOT EXISTS admin_sessions (
    id SERIAL PRIMARY KEY,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    admin_id VARCHAR(64) NOT NULL REFERENCES admin_users(admin_id) ON DELETE CASCADE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ip_address VARCHAR(45) DEFAULT '127.0.0.1',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 13. Admin Audit Log
CREATE TABLE IF NOT EXISTS admin_audit_log (
    id SERIAL PRIMARY KEY,
    admin_id VARCHAR(64) NOT NULL,
    action VARCHAR(128) NOT NULL,
    target_user VARCHAR(255),
    details TEXT,
    ip_address VARCHAR(45) DEFAULT '127.0.0.1',
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 14. Feature Flags
CREATE TABLE IF NOT EXISTS feature_flags (
    id SERIAL PRIMARY KEY,
    key VARCHAR(128) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    enabled INT NOT NULL DEFAULT 1,
    rollout_percentage INT NOT NULL DEFAULT 100,
    description TEXT DEFAULT '',
    updated_by VARCHAR(64) DEFAULT 'ADMIN',
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 15. Maintenance Mode
CREATE TABLE IF NOT EXISTS maintenance_mode (
    id SERIAL PRIMARY KEY,
    enabled INT NOT NULL DEFAULT 0,
    message TEXT DEFAULT 'Saarthi is undergoing scheduled system maintenance.',
    bypass_whitelist TEXT DEFAULT '127.0.0.1',
    updated_by VARCHAR(64) DEFAULT 'ADMIN',
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 16. Tool Policies
CREATE TABLE IF NOT EXISTS tool_policies (
    id SERIAL PRIMARY KEY,
    tool_id VARCHAR(128) UNIQUE NOT NULL,
    risk_classification VARCHAR(32) NOT NULL DEFAULT 'LOW',
    permission_level VARCHAR(32) NOT NULL DEFAULT 'AUTOMATIC',
    enabled INT NOT NULL DEFAULT 1,
    updated_by VARCHAR(64) DEFAULT 'ADMIN',
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 17. Agent Tasks
CREATE TABLE IF NOT EXISTS agent_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(64) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    prompt TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'QUEUED',
    plan_dag_json TEXT,
    current_step_index INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 18. Scheduled Jobs
CREATE TABLE IF NOT EXISTS scheduled_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(64) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    schedule_type VARCHAR(32) NOT NULL DEFAULT 'ONE_TIME',
    cron_expression VARCHAR(64),
    status VARCHAR(32) NOT NULL DEFAULT 'SCHEDULED',
    next_run_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 19. Resumes
CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    resume_id VARCHAR(64) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    raw_content TEXT,
    parsed_facts_json TEXT,
    is_default INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 20. Churn Feedback
CREATE TABLE IF NOT EXISTS churn_feedback (
    id SERIAL PRIMARY KEY,
    feedback_id VARCHAR(64) UNIQUE NOT NULL,
    user_id VARCHAR(64) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    reason VARCHAR(255) NOT NULL,
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 21. MCP Consequential Request State Consumed Tokens
CREATE TABLE IF NOT EXISTS mcp_consumed_tokens (
    token_id VARCHAR(64) PRIMARY KEY,
    principal VARCHAR(255) NOT NULL,
    method VARCHAR(255) NOT NULL,
    params_hash VARCHAR(64) NOT NULL,
    consumed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mcp_consumed_tokens_exp ON mcp_consumed_tokens(expires_at);

-- 22. Job Applications Pipeline
CREATE TABLE IF NOT EXISTS job_applications (
    id SERIAL PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    job_url TEXT,
    location VARCHAR(255),
    salary VARCHAR(128),
    date_applied VARCHAR(64) NOT NULL,
    status VARCHAR(64) NOT NULL DEFAULT 'SAVED',
    resume_version VARCHAR(128),
    cover_letter TEXT,
    recruiter_contact TEXT,
    next_action TEXT,
    follow_up_date VARCHAR(64),
    interview_date VARCHAR(64),
    notes TEXT,
    job_description TEXT,
    work_mode VARCHAR(64) DEFAULT 'REMOTE',
    salary_min REAL,
    salary_max REAL,
    priority VARCHAR(32) DEFAULT 'MEDIUM',
    deadline VARCHAR(64),
    interview_status VARCHAR(64),
    next_action_date VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 23. Student Verifications
CREATE TABLE IF NOT EXISTS student_verifications (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    institution VARCHAR(255),
    status VARCHAR(64) NOT NULL DEFAULT 'VERIFIED',
    verified_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 24. Interview Questions Bank
CREATE TABLE IF NOT EXISTS interview_questions (
    id SERIAL PRIMARY KEY,
    application_id INT,
    category VARCHAR(64) NOT NULL,
    question TEXT NOT NULL,
    difficulty VARCHAR(32) NOT NULL DEFAULT 'Medium',
    reason TEXT,
    preparation_topics TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 25. STAR Answers
CREATE TABLE IF NOT EXISTS star_answers (
    id SERIAL PRIMARY KEY,
    question_id INT NOT NULL,
    situation TEXT,
    task TEXT,
    action TEXT,
    result TEXT,
    score INT DEFAULT 80,
    scoring_breakdown TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 26. Salary Compensation Offers
CREATE TABLE IF NOT EXISTS salary_offers (
    id SERIAL PRIMARY KEY,
    application_id INT,
    company VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    base_salary REAL DEFAULT 0,
    variable_pay REAL DEFAULT 0,
    bonus REAL DEFAULT 0,
    equity TEXT,
    location VARCHAR(255),
    competing_offer TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 27. Career Goals & Milestones
CREATE TABLE IF NOT EXISTS career_goals (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(64) NOT NULL DEFAULT 'SKILLS',
    priority VARCHAR(32) NOT NULL DEFAULT 'MEDIUM',
    target_date VARCHAR(64),
    status VARCHAR(64) NOT NULL DEFAULT 'IN_PROGRESS',
    progress INT DEFAULT 0,
    milestones TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def init_postgres_tables():
    """
    Initializes PostgreSQL tables if connected to PostgreSQL.
    """
    try:
        with get_db_connection() as conn:
            # Check if running against PostgresConnectionAdapter
            if hasattr(conn, "_conn") and hasattr(conn._conn, "cursor"):
                cursor = conn.cursor()
                cursor.execute(POSTGRES_SCHEMA_SQL)
                conn.commit()
                logger.info("Successfully verified/initialized PostgreSQL schema tables.")
    except Exception as e:
        logger.error(f"Error initializing PostgreSQL schema: {e}")
