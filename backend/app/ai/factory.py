from typing import Optional
from app.ai.base import AIProvider
from app.ai.gemini_provider import GeminiProvider
from app.ai.groq_provider import GroqProvider
from app.ai.fallback_provider import FallbackAIProvider


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Factory function returning the configured AIProvider instance.
    Defaults to FallbackAIProvider (Gemini as primary with Groq as automatic fallback).
    Supports explicit 'gemini' or 'groq' for isolated provider testing.
    """
    if provider_name:
        name = provider_name.lower().strip()
        if name == "gemini":
            return GeminiProvider()
        if name == "groq":
            return GroqProvider()

    return FallbackAIProvider()
