import pytest
from app.ai.factory import get_ai_provider
from app.ai.openai_provider import OpenAIProvider
from app.ai.gemini_provider import GeminiProvider


def test_ai_provider_factory():
    openai_p = get_ai_provider("openai")
    assert isinstance(openai_p, OpenAIProvider)

    gemini_p = get_ai_provider("gemini")
    assert isinstance(gemini_p, GeminiProvider)


@pytest.mark.asyncio
async def test_openai_provider_fallback():
    provider = OpenAIProvider(api_key=None)
    text = await provider.generate_text("Explain authentication flow.")
    assert "Fallback Response" in text or len(text) > 10

    embedding = await provider.generate_embedding("def login(): pass")
    assert len(embedding) == 1536


@pytest.mark.asyncio
async def test_gemini_provider_fallback():
    provider = GeminiProvider(api_key=None)
    text = await provider.generate_text("Explain database connection.")
    assert "Fallback Response" in text or len(text) > 10

    embedding = await provider.generate_embedding("class Database:")
    assert len(embedding) == 768
