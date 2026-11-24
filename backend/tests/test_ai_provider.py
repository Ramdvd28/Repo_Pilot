import pytest
from app.ai.base import AIProviderError
from app.ai.factory import get_ai_provider
from app.ai.gemini_provider import GeminiProvider
from app.ai.groq_provider import GroqProvider
from app.ai.fallback_provider import FallbackAIProvider


def test_ai_provider_factory():
    default_p = get_ai_provider()
    assert isinstance(default_p, FallbackAIProvider)
    assert isinstance(default_p.primary, GeminiProvider)
    assert isinstance(default_p.fallback, GroqProvider)

    gemini_p = get_ai_provider("gemini")
    assert isinstance(gemini_p, GeminiProvider)

    groq_p = get_ai_provider("groq")
    assert isinstance(groq_p, GroqProvider)


@pytest.mark.asyncio
async def test_gemini_provider_fallback():
    provider = GeminiProvider(api_key=None)
    text = await provider.generate_text("Explain database connection.")
    assert "Fallback Response" in text or len(text) > 10

    embedding = await provider.generate_embedding("class Database:")
    assert len(embedding) == 768


@pytest.mark.asyncio
async def test_groq_provider_fallback():
    provider = GroqProvider(api_key=None)
    text = await provider.generate_text("Explain routing architecture.")
    assert "Fallback Response" in text or len(text) > 10

    embedding = await provider.generate_embedding("def route(): pass")
    assert len(embedding) == 768


@pytest.mark.asyncio
async def test_fallback_provider_primary_success(mocker):
    primary = GeminiProvider(api_key="mock_key")
    fallback = GroqProvider(api_key="mock_key")

    mocker.patch.object(primary, "generate_text", return_value="Gemini primary answer")
    fallback_mock = mocker.patch.object(fallback, "generate_text", return_value="Groq fallback answer")

    provider = FallbackAIProvider(primary=primary, fallback=fallback)
    result = await provider.generate_text("What does this project do?")

    assert result == "Gemini primary answer"
    # Fallback must NOT be called when primary succeeds
    fallback_mock.assert_not_called()


@pytest.mark.asyncio
async def test_fallback_provider_groq_on_gemini_quota_error(mocker):
    primary = GeminiProvider(api_key="mock_key")
    fallback = GroqProvider(api_key="mock_key")

    # Simulate Gemini 429 quota exhaustion / rate limit
    mocker.patch.object(
        primary,
        "generate_text",
        side_effect=AIProviderError("ResourceExhausted: 429 Quota reached", provider="gemini")
    )
    mocker.patch.object(fallback, "generate_text", return_value="Groq fallback answer after Gemini 429")

    provider = FallbackAIProvider(primary=primary, fallback=fallback)
    result = await provider.generate_text("What does this project do?")

    assert result == "Groq fallback answer after Gemini 429"


@pytest.mark.asyncio
async def test_fallback_provider_both_fail_sanitized_error(mocker):
    primary = GeminiProvider(api_key="mock_key")
    fallback = GroqProvider(api_key="mock_key")

    mocker.patch.object(
        primary,
        "generate_text",
        side_effect=AIProviderError("Gemini error with sensitive info https://api.internal/key=secret", provider="gemini")
    )
    mocker.patch.object(
        fallback,
        "generate_text",
        side_effect=AIProviderError("Groq error with sensitive info https://api.internal/key=secret", provider="groq")
    )

    provider = FallbackAIProvider(primary=primary, fallback=fallback)
    
    with pytest.raises(AIProviderError) as exc_info:
        await provider.generate_text("Any query")

    # Ensure sensitive provider error or URLs are NOT exposed to user
    err_str = str(exc_info.value)
    assert "secret" not in err_str
    assert "https://" not in err_str
    assert "AI service is temporarily unavailable. Please try again in a moment." in err_str
