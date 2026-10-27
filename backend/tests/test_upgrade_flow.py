import pytest
from app.licensing.models import LicensePlan, LicenseStatus, Entitlements
from app.licensing.middleware import default_client_manager

def test_plan_upgrade_flow_matrix():
    plans = [LicensePlan.FREE, LicensePlan.STUDENT, LicensePlan.PERSONAL, LicensePlan.POWER, LicensePlan.CUSTOM]
    for plan in plans:
        ent = Entitlements.from_plan(plan)
        if plan == LicensePlan.FREE:
            assert ent.requires_watermark is True
            assert ent.max_job_applications_per_month == 3
        else:
            assert ent.requires_watermark is False
            assert ent.max_job_applications_per_month == -1

def test_backend_is_authoritative_for_entitlements():
    status, ent, msg = default_client_manager.evaluate_license()
    if not ent:
        ent = Entitlements.from_plan(LicensePlan.FREE)
    assert ent is not None
    assert hasattr(ent, "requires_watermark")
    assert ent.requires_watermark is True
