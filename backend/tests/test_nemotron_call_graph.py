import pytest
from app.models.factory import ModelFactory
from app.models.nemotron_service import NemotronService

def test_model_factory_call_graph_returns_valid_provider():
    provider = ModelFactory.get_provider()
    assert provider is not None
    assert hasattr(provider, "generate_response")
