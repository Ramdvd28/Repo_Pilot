from typing import Optional
from app.ai.base import AIProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.gemini_provider import GeminiProvider
from app.core.config import settings


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Factory function returning the configured AIProvider instance.
    Supports "openai" and "gemini".
    """
    target_provider = (provider_name or settings.AI_PROVIDER or "openai").lower().strip()

    if target_provider == "gemini":
        return GeminiProvider()
    
    # Default to OpenAI
    return OpenAIProvider()
