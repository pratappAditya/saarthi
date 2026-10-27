import pytest
import os
import sqlite3
import json
from datetime import datetime, timezone
from app.config.settings import settings
from app.db.auth import AuthRepository, hash_password
from app.licensing.payment import SAARTHI_PLAN_PRICING, RazorpayPaymentProvider
from app.services.billing_service import BillingService
from app.security.paths import is_path_allowed, sanitize_filename, validate_file_upload
from app.core.feature_flags import feature_flag_manager
from app.db.backup import DatabaseBackupEngine
from app.admin.audit.admin_audit_service import admin_audit_service
from app.admin.health.system_health_monitor import system_health_monitor

def test_auth_password_hashing_and_security():
    pw = "SuperSecure@2026!"
    h1, salt1 = hash_password(pw)
    h2, salt2 = hash_password(pw, salt=salt1)
    assert h1 == h2
    assert len(salt1) >= 16

def test_canonical_plans_pricing_registry():
    plans = ["FREE", "STUDENT", "PERSONAL", "POWER", "TEAMS", "ENTERPRISE"]
    for p in plans:
        assert p in SAARTHI_PLAN_PRICING
    assert SAARTHI_PLAN_PRICING["FREE"]["inr"] == 0
    assert SAARTHI_PLAN_PRICING["STUDENT"]["inr"] == 99
    assert SAARTHI_PLAN_PRICING["PERSONAL"]["inr"] == 399
    assert SAARTHI_PLAN_PRICING["POWER"]["inr"] == 799
    assert SAARTHI_PLAN_PRICING["TEAMS"]["inr"] == 699

@pytest.mark.asyncio
async def test_billing_abstraction_razorpay_test_mode():
    provider = RazorpayPaymentProvider(key_id="rzp_test_mock", key_secret="rzp_secret_mock")
    order = await provider.create_order("usr_test_1", "PERSONAL", "INR")
    assert order["status"] == "CREATED"
    assert order["amount"] == 39900
    assert order["provider"] == "RAZORPAY"

def test_feature_flags_system():
    assert feature_flag_manager.is_enabled("voice") is True
    assert feature_flag_manager.is_enabled("billing") is False  # Live billing disabled
    feature_flag_manager.set_flag("experimental_features", True)
    assert feature_flag_manager.is_enabled("experimental_features") is True

def test_file_security_and_sanitization():
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    valid_pdf = b"%PDF-1.4 Mock PDF Content"
    res = validate_file_upload("resume.pdf", valid_pdf, max_size_mb=25)
    assert res["valid"] is True
    assert res["sanitized_filename"] == "resume.pdf"

    invalid_exe = b"MZ executable binary"
    res_exe = validate_file_upload("malware.exe", invalid_exe)
    assert res_exe["valid"] is False

def test_admin_audit_logging():
    log_res = admin_audit_service.record_event(
        admin_id="ADMIN_TEST",
        action="USER_SUSPENDED",
        target="usr_violator",
        reason="Policy violation test"
    )
    assert log_res["status"].lower() == "success"

def test_database_backup_engine():
    backup_res = DatabaseBackupEngine.create_backup(tag="test_prod_prep")
    assert backup_res["status"] == "success"
    assert os.path.exists(backup_res["backup_path"])

    integrity = DatabaseBackupEngine.check_integrity()
    assert integrity["healthy"] is True
