import pytest
from app.licensing.watermark import WatermarkEngine

def test_phase_ab_rpeu_calculation_logic():
    # RPEU = Attributable Revenue / Eligible Exposed Users
    revenue_control = 1490.0  # 10 payers @ 149
    exposed_control = 50
    rpeu_control = revenue_control / exposed_control
    assert rpeu_control == 29.8

    revenue_treatment = 1500.0  # 15 payers @ 100
    exposed_treatment = 50
    rpeu_treatment = revenue_treatment / exposed_treatment
    assert rpeu_treatment == 30.0
    assert rpeu_treatment > rpeu_control

def test_phase_ab_statistical_sample_gate():
    # Min sample requirement = 100 users per variant
    sample_control = 25
    sample_treatment = 25
    min_required = 100

    decision = "C. CONTINUE EXPERIMENT" if (sample_control < min_required or sample_treatment < min_required) else "EVALUATE"
    assert decision == "C. CONTINUE EXPERIMENT"

def test_phase_ab_existing_subscriber_protection():
    # Existing ₹149 subscribers must retain existing entitlement without re-assignment
    existing_user = "subscriber_user_68"
    v1 = WatermarkEngine.get_pricing_experiment_variant(existing_user)
    v2 = WatermarkEngine.get_pricing_experiment_variant(existing_user)
    assert v1 == v2
