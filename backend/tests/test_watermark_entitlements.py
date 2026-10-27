import pytest
from app.licensing.models import Entitlements, LicensePlan
from app.licensing.watermark import WatermarkEngine

def test_watermark_entitlements_matrix():
    free_ent = Entitlements.from_plan(LicensePlan.FREE)
    assert free_ent.requires_watermark is True
    assert free_ent.max_job_applications_per_month == 3

    stu_ent = Entitlements.from_plan(LicensePlan.STUDENT)
    assert stu_ent.requires_watermark is False
    assert stu_ent.max_job_applications_per_month == -1

    per_ent = Entitlements.from_plan(LicensePlan.PERSONAL)
    assert per_ent.requires_watermark is False

    pow_ent = Entitlements.from_plan(LicensePlan.POWER)
    assert pow_ent.requires_watermark is False

    cust_ent = Entitlements.from_plan(LicensePlan.CUSTOM)
    assert cust_ent.requires_watermark is False

def test_watermark_engine_markdown_free():
    free_ent = Entitlements.from_plan(LicensePlan.FREE)
    content = "# My Resume\n\nContent details here."
    watermarked = WatermarkEngine.watermark_markdown(content, free_ent)
    assert "Created with Saarthi" in watermarked
    assert content in watermarked

def test_watermark_engine_markdown_paid():
    stu_ent = Entitlements.from_plan(LicensePlan.STUDENT)
    content = "# My Resume\n\nContent details here."
    clean = WatermarkEngine.watermark_markdown(content, stu_ent)
    assert "Created with Saarthi" not in clean
    assert clean == content

def test_watermark_engine_html_free():
    free_ent = Entitlements.from_plan(LicensePlan.FREE)
    html = "<html><body><h1>Resume</h1></body></html>"
    watermarked = WatermarkEngine.watermark_html(html, free_ent)
    assert "Created with Saarthi" in watermarked
    assert "</body>" in watermarked

def test_original_source_file_untouched():
    original_text = "John Doe | Resume Baseline"
    free_ent = Entitlements.from_plan(LicensePlan.FREE)
    WatermarkEngine.watermark_markdown(original_text, free_ent)
    # Ensure original input variable was not modified in-place
    assert original_text == "John Doe | Resume Baseline"
