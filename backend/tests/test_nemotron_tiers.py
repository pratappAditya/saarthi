import pytest
from app.models.nemotron_catalog import NemotronModelCatalog

def test_nemotron_tiers_specs():
    for tier in ["STANDARD", "PRO", "SUPER", "ULTRA"]:
        spec = NemotronModelCatalog.get_spec_by_tier(tier)
        assert spec is not None
        assert spec.tier == tier
        assert "nemotron" in spec.model_id.lower()
        assert spec.verified is True
        assert spec.enabled is True
