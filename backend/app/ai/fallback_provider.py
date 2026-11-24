import logging
from typing import List, Optional
from app.ai.base import AIProvider, AIProviderError
from app.ai.gemini_provider import GeminiProvider
from app.ai.groq_provider import GroqProvider

logger = logging.getLogger("repopilot.ai.fallback")


class FallbackAIProvider(AIProvider):
    """
    Intelligent resilient AI provider that orchestrates primary and fallback providers:
    1. Attempts Gemini first (Primary).
    2. If Gemini fails due to quota exhaustion (429), rate limits, timeouts, or service errors,
       automatically attempts Groq (Fallback) with identical prompt & context.
    3. If both providers fail, securely logs the internal details and raises a clean,
       user-friendly AIProviderError without leaking keys, URLs, or internal stack traces.
    """

    def __init__(
        self,
        primary: Optional[AIProvider] = None,
        fallback: Optional[AIProvider] = None
    ):
        self.primary = primary or GeminiProvider()
        self.fallback = fallback or GroqProvider()

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> str:
        primary_error: Optional[Exception] = None

        # 1. Attempt Gemini (Primary)
        try:
            # If primary has no API key but fallback does, skip directly to fallback
            primary_has_key = bool(getattr(self.primary, "api_key", None))
            fallback_has_key = bool(getattr(self.fallback, "api_key", None))

            if not primary_has_key and fallback_has_key:
                logger.info("Gemini API key not configured; routing request directly to Groq fallback.")
                return await self.fallback.generate_text(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

            return await self.primary.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as exc:
            primary_error = exc
            logger.warning(
                "Primary AI provider (Gemini) failed. Engaging automatic Groq fallback. Cause: %s",
                str(exc)
            )

        # 2. Attempt Groq (Automatic Fallback)
        try:
            return await self.fallback.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as fallback_exc:
            logger.error(
                "Both AI providers failed. Primary error: %s | Fallback error: %s",
                str(primary_error),
                str(fallback_exc)
            )
            # Raise sanitized user-friendly error
            raise AIProviderError(
                "AI service is temporarily unavailable. Please try again in a moment.",
                provider="fallback"
            ) from fallback_exc

    async def generate_embedding(self, text: str) -> List[float]:
        try:
            return await self.primary.generate_embedding(text)
        except Exception as e:
            logger.warning("Primary embedding generation failed (%s). Falling back.", str(e))
            return await self.fallback.generate_embedding(text)

