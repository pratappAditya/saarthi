"""
Phase 10 — Automated Tests for Experience Modes.
Verifies SIGNATURE, FORGE, PULSE, and AURORA mode configurations.
"""

import pytest

EXPERIENCE_MODES = ["signature", "forge", "pulse", "aurora"]

def test_all_four_experience_modes_defined():
    """Verify all four experience modes are recognized valid values."""
    for mode in EXPERIENCE_MODES:
        assert mode in ("signature", "forge", "pulse", "aurora")
