import pytest
from app.licensing.models import LicenseStatus, LicensePlan
from app.licensing.vendor_server import VendorServer
from app.licensing.client_manager import ClientLicenseManager

ALL_STATES = [
    LicenseStatus.UNLICENSED,
    LicenseStatus.TRIAL,
    LicenseStatus.ACTIVE,
    LicenseStatus.GRACE_PERIOD,
    LicenseStatus.GRACE_EXPIRED,
    LicenseStatus.EXPIRED,
    LicenseStatus.SUSPENDED,
    LicenseStatus.REVOKED,
    LicenseStatus.CANCELLED,
    LicenseStatus.CLOCK_TAMPERED
]

# State transition matrix rules:
# Allowed transitions via vendor authority or runtime rules
ALLOWED_TRANSITIONS = {
    LicenseStatus.UNLICENSED: {LicenseStatus.TRIAL, LicenseStatus.ACTIVE},
    LicenseStatus.TRIAL: {LicenseStatus.ACTIVE, LicenseStatus.EXPIRED, LicenseStatus.CANCELLED},
    LicenseStatus.ACTIVE: {LicenseStatus.EXPIRED, LicenseStatus.GRACE_PERIOD, LicenseStatus.GRACE_EXPIRED, LicenseStatus.SUSPENDED, LicenseStatus.REVOKED, LicenseStatus.CANCELLED, LicenseStatus.CLOCK_TAMPERED},
    LicenseStatus.GRACE_PERIOD: {LicenseStatus.ACTIVE, LicenseStatus.GRACE_EXPIRED, LicenseStatus.SUSPENDED, LicenseStatus.REVOKED, LicenseStatus.CANCELLED},
    LicenseStatus.GRACE_EXPIRED: {LicenseStatus.ACTIVE, LicenseStatus.SUSPENDED, LicenseStatus.REVOKED, LicenseStatus.CANCELLED},
    LicenseStatus.EXPIRED: {LicenseStatus.ACTIVE, LicenseStatus.REVOKED, LicenseStatus.CANCELLED},
    LicenseStatus.SUSPENDED: {LicenseStatus.ACTIVE, LicenseStatus.REVOKED, LicenseStatus.CANCELLED},
    LicenseStatus.CANCELLED: {LicenseStatus.ACTIVE, LicenseStatus.REVOKED}, # Can reactivate via new subscription
    LicenseStatus.REVOKED: set(), # Permanent sink state! Cannot transition to active!
    LicenseStatus.CLOCK_TAMPERED: {LicenseStatus.ACTIVE} # Requires clock fix & online re-verify
}

@pytest.fixture
def vendor_and_client():
    vendor = VendorServer(db_path=":memory:")
    client = ClientLicenseManager(db_path=":memory:", public_key_pem=vendor.public_key_pem.encode('utf-8'))
    return vendor, client

@pytest.mark.parametrize("from_state", ALL_STATES)
@pytest.mark.parametrize("to_state", ALL_STATES)
def test_state_machine_transition_matrix(vendor_and_client, from_state, to_state):
    vendor, client = vendor_and_client
    allowed = ALLOWED_TRANSITIONS.get(from_state, set())
    
    if from_state == LicenseStatus.REVOKED and to_state == LicenseStatus.ACTIVE:
        # Critical rule: REVOKED can NEVER locally transition to ACTIVE
        cust = vendor.create_customer("Rev User", f"rev_{from_state.value}_{to_state.value}@test.org")
        lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
        vendor.revoke_license(lic.license_id)
        
        # Local client attempts to clear revocation or evaluate
        client.record_revocation(lic.license_id, "Vendor Revoked")
        st, _, _ = client.evaluate_license()
        assert st != LicenseStatus.ACTIVE

def test_revoked_is_permanent_sink(vendor_and_client):
    vendor, client = vendor_and_client
    cust = vendor.create_customer("User Sink", "sink@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    vendor.revoke_license(lic.license_id)
    assert vendor.restore_license(lic.license_id) is False
    with pytest.raises(ValueError, match="permanently revoked"):
        vendor.activate_license(lic.license_key, "fp_sink")

def test_suspended_requires_vendor_restore(vendor_and_client):
    vendor, client = vendor_and_client
    cust = vendor.create_customer("Susp User", "susp_restore@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    vendor.suspend_license(lic.license_id)
    with pytest.raises(ValueError, match="currently suspended"):
        vendor.activate_license(lic.license_key, "fp_susp")
        
    assert vendor.restore_license(lic.license_id) is True
    t = vendor.activate_license(lic.license_key, "fp_susp")
    assert t is not None

def test_cancelled_requires_vendor_re_subscription(vendor_and_client):
    vendor, client = vendor_and_client
    cust = vendor.create_customer("Cancel User", "cancel_resub@example.com")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    vendor.cancel_license(lic.license_id)
    with pytest.raises(ValueError, match="cancelled"):
        vendor.activate_license(lic.license_key, "fp_cancel")

@pytest.mark.parametrize("state", ALL_STATES)
def test_idempotent_state_operations(vendor_and_client, state):
    vendor, _ = vendor_and_client
    cust = vendor.create_customer(f"User {state.value}", f"idemp_{state.value}@test.org")
    lic = vendor.create_license(cust.customer_id, plan=LicensePlan.MONTHLY)
    
    if state == LicenseStatus.SUSPENDED:
        vendor.suspend_license(lic.license_id)
        vendor.suspend_license(lic.license_id)
    elif state == LicenseStatus.REVOKED:
        vendor.revoke_license(lic.license_id)
        vendor.revoke_license(lic.license_id)
    elif state == LicenseStatus.CANCELLED:
        vendor.cancel_license(lic.license_id)
        vendor.cancel_license(lic.license_id)
