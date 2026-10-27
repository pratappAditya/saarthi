import pytest
from app.models.nemotron_catalog import NemotronModelCatalog

def test_catalog_tiers():
    specs = NemotronModelCatalog.get_all_specs()
    assert len(specs) >= 4
    tiers = [s.tier for s in specs]
    assert "STANDARD" in tiers
    assert "PRO" in tiers
    assert "SUPER" in tiers
    assert "ULTRA" in tiers

def test_catalog_approval_enforcement():
    assert NemotronModelCatalog.is_approved("nemotron-3-nano:4b") is True
    assert NemotronModelCatalog.is_approved("nemotron-mini:4b") is True
    assert NemotronModelCatalog.is_approved("nemotron:3b") is True
    assert NemotronModelCatalog.is_approved("nemotron-3-8b") is True
    assert NemotronModelCatalog.is_approved("llama3:8b") is False
    assert NemotronModelCatalog.is_approved("mistral:7b") is False
    assert NemotronModelCatalog.is_approved("gpt-4o") is False
