import pytest
from app.licensing.watermark import WatermarkEngine, WATERMARK_EXPERIMENTS

def test_experiment_variant_deterministic_assignment():
    v1 = WatermarkEngine.get_experiment_variant("user_abc")
    v2 = WatermarkEngine.get_experiment_variant("user_abc")
    assert v1 == v2
    assert v1 in ["CONTROL", "VARIANT_A", "VARIANT_B", "VARIANT_C"]

def test_experiment_variant_data():
    for v_key in ["CONTROL", "VARIANT_A", "VARIANT_B", "VARIANT_C"]:
        data = WatermarkEngine.get_experiment_data(v_key)
        assert "text" in data
        assert "message" in data
        assert len(data["message"]) > 10

def test_all_variants_contain_saarthi():
    for v_key, data in WATERMARK_EXPERIMENTS.items():
        assert "Saarthi" in data["text"] or "Saarthi" in data["message"]
