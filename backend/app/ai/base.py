from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class AIProviderError(Exception):
    """
    Exception raised when an AI provider fails due to rate limits, quota exhaustion,
    timeouts, or service errors.
    """
    def __init__(self, message: str, provider: Optional[str] = None, is_retryable: bool = True):
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.is_retryable = is_retryable


class AIProvider(ABC):
    """
    Abstract Base Class for AI Providers (Google Gemini, Groq).
    Enforces standardized interfaces for text generation and vector embeddings.
    """

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> str:
        """Generates text completion for a prompt."""
        pass

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generates vector embedding for input text."""
        pass
