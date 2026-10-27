import pytest
from app.models.nemotron_service import NemotronService, NemotronModelNotApprovedException, NemotronModelMismatchException

def test_production_gate_nemotron_rejection():
    # Valid Nemotron model
    srv = NemotronService(model_name="nemotron-3-nano:4b")
    assert srv.model_name == "nemotron-3-nano:4b"

    # Non-Nemotron model rejection
    with pytest.raises(NemotronModelNotApprovedException):
        NemotronService(model_name="gpt-4o")

    with pytest.raises(NemotronModelNotApprovedException):
        NemotronService(model_name="llama3:8b")

    with pytest.raises(NemotronModelNotApprovedException):
        NemotronService(model_name="mistral:7b")
