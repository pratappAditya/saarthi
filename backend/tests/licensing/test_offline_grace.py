import pytest
from datetime import datetime, timezone, timedelta
from app.licensing.models import LicenseStatus, LicensePlan
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager

@pytest.fixture
def setup_mgrs():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

def test_offline_operation_within_grace_period(setup_mgrs):
    vendor, client = setup_mgrs
    cust = vendor.create_customer("Offline User", "off1@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    fp = "fp_offline_1"
    token = vendor.activate_license(lic.license_key, fp)
    
    # Store token with last_verified_at = 3 days ago (within 7-day grace)
    three_days_ago = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
    payload = {"plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at}
    
    client.store_activation_token(lic.license_key, token, payload)
    
    # Manually set last_verified_at in DB
    with client._get_connection() as conn:
        conn.cursor().execute("UPDATE client_license_cache SET last_verified_at = ?", (three_days_ago,))
        conn.commit()
        
    status, ent, msg = client.evaluate_license(fp)
    assert status == LicenseStatus.ACTIVE
    assert ent is not None

def test_offline_grace_period_expired(setup_mgrs):
    vendor, client = setup_mgrs
    cust = vendor.create_customer("Offline User 2", "off2@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    fp = "fp_offline_2"
    token = vendor.activate_license(lic.license_key, fp)
    
    payload = {"plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at}
    client.store_activation_token(lic.license_key, token, payload)
    
    # Set last_verified_at to 10 days ago (exceeding 7-day grace)
    ten_days_ago = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    with client._get_connection() as conn:
        conn.cursor().execute("UPDATE client_license_cache SET last_verified_at = ?", (ten_days_ago,))
        conn.commit()
        
    status, ent, msg = client.evaluate_license(fp)
    assert status == LicenseStatus.GRACE_EXPIRED
    assert "expired" in msg.lower()

def test_clock_rollback_detection_high_water_mark(setup_mgrs):
    vendor, client = setup_mgrs
    now = datetime.now(timezone.utc)
    
    # 1. Log a future timestamp in high water mark log (e.g. 2030)
    future_dt = now + timedelta(days=365)
    client.update_clock_high_water_mark(future_dt)
    
    # 2. Evaluating license with current time (which is earlier than future_dt) triggers CLOCK_TAMPERED
    status, ent, msg = client.evaluate_license()
    assert status == LicenseStatus.CLOCK_TAMPERED
    assert "rollback" in msg.lower()

@pytest.mark.parametrize("offset_hours", [1, 24, 72, 160])
def test_clock_forward_progression_allowed(setup_mgrs, offset_hours):
    _, client = setup_mgrs
    start = datetime.now(timezone.utc)
    
    assert client.update_clock_high_water_mark(start) is True
    assert client.update_clock_high_water_mark(start + timedelta(hours=offset_hours)) is True

@pytest.mark.parametrize("days_offline,expected_active", [
    (0, True),
    (1, True),
    (2, True),
    (3, True),
    (4, True),
    (5, True),
    (6, True),
    (7, True),
    (8, False),
    (9, False),
    (10, False),
    (15, False),
    (30, False),
    (60, False),
    (90, False),
    (120, False),
    (180, False),
    (365, False),
    (500, False),
    (1000, False),
])
def test_offline_grace_boundary_matrix(setup_mgrs, days_offline, expected_active):
    vendor, client = setup_mgrs
    cust = vendor.create_customer("Boundary User", f"user_b_{days_offline}@test.org")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, duration_days=365)
    fp = f"fp_boundary_{days_offline}"
    token = vendor.activate_license(lic.license_key, fp)
    
    payload = {"plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at}
    client.store_activation_token(lic.license_key, token, payload)
    
    past_verified = (datetime.now(timezone.utc) - timedelta(days=days_offline)).isoformat()
    with client._get_connection() as conn:
        conn.cursor().execute("UPDATE client_license_cache SET last_verified_at = ?", (past_verified,))
        conn.commit()
        
    st, ent, _ = client.evaluate_license(fp)
    if expected_active:
        assert st == LicenseStatus.ACTIVE
    else:
        assert st == LicenseStatus.GRACE_EXPIRED
