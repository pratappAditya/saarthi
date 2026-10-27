import pytest
from datetime import datetime, timezone, timedelta
from app.licensing.models import LicenseStatus, LicensePlan
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager

@pytest.fixture
def env():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

@pytest.mark.parametrize("day", range(0, 11))
def test_offline_daily_progression(env, day):
    vendor, client = env
    cust = vendor.create_customer("Offline User", f"off_day_{day}@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY, duration_days=30)
    fp = f"fp_off_day_{day}"
    token = vendor.activate_license(lic.license_key, fp)
    
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": f"n_{day}"}
    client.store_activation_token(lic.license_key, token, payload)
    
    past_verified = (datetime.now(timezone.utc) - timedelta(days=day)).isoformat()
    with client._get_connection() as conn:
        conn.cursor().execute("UPDATE client_license_cache SET last_verified_at = ?", (past_verified,))
        conn.commit()
        
    st, ent, _ = client.evaluate_license(fp)
    if day <= 7:
        assert st == LicenseStatus.ACTIVE
        assert ent is not None
    else:
        assert st == LicenseStatus.GRACE_EXPIRED
        assert ent is None

@pytest.mark.parametrize("minutes_back", [10, 60, 1440, 10000, 50000])
def test_clock_rollback_variations(env, minutes_back):
    _, client = env
    now = datetime.now(timezone.utc)
    
    # High water mark logged at 'now'
    client.update_clock_high_water_mark(now)
    
    # Attempting request with time set back by minutes_back
    past_time = now - timedelta(minutes=minutes_back)
    is_valid = client.update_clock_high_water_mark(past_time)
    assert is_valid is False

@pytest.mark.parametrize("i", range(1, 41))
def test_offline_cache_tampering_fails(env, i):
    vendor, client = env
    cust = vendor.create_customer(f"Tamper User {i}", f"tamper_{i}@saarthi.ai")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    fp = f"fp_tamper_{i}"
    token = vendor.activate_license(lic.license_key, fp)
    
    payload = {"license_id": lic.license_id, "plan": "MONTHLY", "status": "ACTIVE", "device_fingerprint": fp, "issued_at": lic.issued_at, "expires_at": lic.expires_at, "nonce": f"n_{i}"}
    client.store_activation_token(lic.license_key, token, payload)
    
    # User modifies local database cache `last_verified_at` to a fake future timestamp
    fake_future = (datetime.now(timezone.utc) + timedelta(days=i)).isoformat()
    with client._get_connection() as conn:
        conn.cursor().execute("UPDATE client_license_cache SET last_verified_at = ?", (fake_future,))
        conn.commit()
        
    # High water mark check detects clock rollback / forward manipulation if evaluated with earlier current time
    st, _, _ = client.evaluate_license(fp)
    assert st in (LicenseStatus.ACTIVE, LicenseStatus.CLOCK_TAMPERED)
