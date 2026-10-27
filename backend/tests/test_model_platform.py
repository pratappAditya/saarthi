"""
Tests for Unified AI Model Platform:
Validates ModelGateway, ModelRegistry, ModelRouter, Provider Adapters, Fallback Chain,
Streaming, Structured Output, and Token/Cost Tracking.
"""

import pytest
import asyncio
from app.models.schema import (
    ModelCapability,
    CostClass,
    LatencyClass,
    PrivacyLevel,
    ModelDescriptor,
    ModelResponse
)
from app.models.registry import ModelRegistry, GLOBAL_MODEL_CATALOG
from app.models.router import ModelRouter, model_router
from app.models.gateway import ModelGateway, model_gateway
from app.models.factory import ModelFactory
from app.models.mock import MockModelProvider


@pytest.mark.asyncio
async def test_model_registry_contains_required_models():
    models = ModelRegistry.list_models()
    assert len(models) >= 10
    model_ids = [m["id"] for m in models]
    assert "nemotron-3-nano:4b" in model_ids
    assert "mock_local_model" in model_ids
    assert "deepseek-chat" in model_ids
    assert "deepseek-reasoner" in model_ids
    assert "qwen-2.5-72b-instruct" in model_ids
    assert "qwen-2.5-coder-32b-instruct" in model_ids
    assert "qwen-vl-max" in model_ids
    assert "llama-3.1-8b-instant" in model_ids
    assert "glm-4-flash" in model_ids
    assert "moonshot-v1-128k" in model_ids


@pytest.mark.asyncio
async def test_model_router_capability_matching():
    # 1. Vision
    vision_model = model_router.select_model(task_type="vision")
    assert ModelCapability.VISION in vision_model.capabilities

    # 2. Coding
    coding_model = model_router.select_model(required_capability=ModelCapability.CODING)
    assert ModelCapability.CODING in coding_model.capabilities

    # 3. Privacy sensitive must be local or zero-data
    private_model = model_router.select_model(privacy_sensitive=True)
    assert private_model.privacy_level in (PrivacyLevel.LOCAL_AIRGAPPED, PrivacyLevel.ZERO_DATA_RETENTION)

    # 4. Explicit model selection
    explicit = model_router.select_model(explicit_model_id="deepseek-chat")
    assert explicit.id == "deepseek-chat"


@pytest.mark.asyncio
async def test_model_factory_creation():
    mock_p = ModelFactory.create_provider("mock", "test-mock")
    assert isinstance(mock_p, MockModelProvider)

    deepseek_p = ModelFactory.create_provider("deepseek", "deepseek-chat")
    assert deepseek_p.provider_name == "deepseek"

    groq_p = ModelFactory.create_provider("groq", "llama-3.1-8b-instant")
    assert groq_p.provider_name == "groq"

    # Unknown provider falls back to mock safely
    unknown_p = ModelFactory.create_provider("non_existent_provider")
    assert isinstance(unknown_p, MockModelProvider)


@pytest.mark.asyncio
async def test_model_gateway_generate_and_metrics():
    gw = ModelGateway()
    response = await gw.generate(
        prompt="Explain quantum entanglement briefly.",
        task_type="chat",
        prefer_local=True
    )
    assert isinstance(response, ModelResponse)
    assert len(response.content) > 0
    assert response.usage.prompt_tokens > 0
    assert response.usage.completion_tokens > 0
    assert response.latency_ms >= 0.0

    metrics = gw.get_metrics()
    assert metrics["total_tokens"] > 0


@pytest.mark.asyncio
async def test_model_gateway_streaming():
    gw = ModelGateway()
    chunks = []
    async for chunk in gw.stream(
        prompt="List three colors.",
        prefer_local=True
    ):
        chunks.append(chunk)

    assert len(chunks) > 0
    full_text = "".join(chunks)
    assert len(full_text) > 0


@pytest.mark.asyncio
async def test_model_gateway_structured_output():
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "status": {"type": "string"}
        },
        "required": ["name", "status"]
    }
    gw = ModelGateway()
    response = await gw.generate(
        prompt="Generate item",
        json_schema=schema,
        prefer_local=True
    )
    assert response.structured_data is not None
    assert "status" in response.structured_data


@pytest.mark.asyncio
async def test_model_gateway_fallback_chain():
    # Verify fallback chain generation
    chain = ModelRouter.get_fallback_chain("deepseek-chat")
    assert len(chain) > 0
    chain_ids = [m.id for m in chain]
    assert "deepseek-chat" not in chain_ids
    assert "mock_local_model" in chain_ids


@pytest.mark.asyncio
async def test_model_gateway_staging_demo_transparency():
    from app.config.settings import settings
    orig_env = settings.ENVIRONMENT
    orig_ollama = settings.OLLAMA_BASE_URL
    try:
        settings.ENVIRONMENT = "staging"
        settings.OLLAMA_BASE_URL = "http://127.0.0.1:59999"
        gw = ModelGateway()
        # Attempt live model without API key in staging environment to trigger fallback to mock
        resp = await gw.generate(
            prompt="Hello test",
            explicit_model_id="deepseek-chat",
            prefer_local=False
        )
        assert resp.is_live is False
        assert resp.execution_mode == "DEMO_FALLBACK"
        assert "[DEMO RESULT / OFFLINE FALLBACK" in resp.content
    finally:
        settings.ENVIRONMENT = orig_env
        settings.OLLAMA_BASE_URL = orig_ollama


@pytest.mark.asyncio
async def test_model_router_free_tier_and_privacy_boundaries():
    # 1. Free-tier query must NOT fall back to paid models
    free_chain = ModelRouter.get_fallback_chain("mock_local_model", allow_paid_fallback=False)
    for model in free_chain:
        assert model.cost_class in (CostClass.FREE_LOCAL, CostClass.FREE_TIER), (
            f"Free-tier request leaked to paid model {model.id} ({model.cost_class})"
        )

    # 2. Privacy-sensitive query must NOT fall back to standard cloud
    private_chain = ModelRouter.get_fallback_chain("nemotron-3-nano:4b", privacy_sensitive=True)
    for model in private_chain:
        assert model.privacy_level != PrivacyLevel.STANDARD_CLOUD, (
            f"Privacy-sensitive request leaked to standard cloud model {model.id}"
        )

