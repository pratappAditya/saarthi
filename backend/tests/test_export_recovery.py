import pytest
from app.licensing.models import Entitlements, LicensePlan
from app.licensing.watermark import WatermarkEngine

def test_watermark_stripping_on_upgrade():
    # 1. User generates document on FREE plan -> watermark appended
    free_ent = Entitlements.from_plan(LicensePlan.FREE)
    raw_doc = "# TAILORED RESUME: Software Engineer\n\n- Key skill: Python\n- Key skill: FastAPI"
    watermarked_doc = WatermarkEngine.watermark_markdown(raw_doc, free_ent)
    assert "Created with Saarthi" in watermarked_doc

    # 2. User upgrades to STUDENT -> entitlement requires_watermark is False
    student_ent = Entitlements.from_plan(LicensePlan.STUDENT)

    # 3. User returns and exports document again -> watermark is cleanly stripped without re-generating AI text
    clean_doc = WatermarkEngine.watermark_markdown(watermarked_doc, student_ent)
    assert "Created with Saarthi" not in clean_doc
    assert "# TAILORED RESUME: Software Engineer" in clean_doc
    assert "- Key skill: Python" in clean_doc

def test_watermark_retains_on_expired_paid_license():
    # If user subscription expires back to FREE, watermark remains required on exports
    free_ent = Entitlements.from_plan(LicensePlan.FREE)
    raw_doc = "# COVER LETTER\n\nDear Hiring Manager..."
    export = WatermarkEngine.watermark_markdown(raw_doc, free_ent)
    assert "Created with Saarthi" in export
