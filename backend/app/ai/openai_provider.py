import os
from typing import List, Optional
from app.ai.base import AIProvider
from app.core.config import settings

try:
    from openai import AsyncOpenAI
    HAS_OPENAI_SDK = True
except ImportError:
    HAS_OPENAI_SDK = False


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        self.client = None
        if HAS_OPENAI_SDK and self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> str:
        if self.client:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content or ""

        # Fallback when OPENAI_API_KEY is not configured
        return (
            "[OpenAI Provider - Fallback Response]\n"
            "This repository analysis response was generated using local repository context matching. "
            "To enable live OpenAI GPT models, please configure OPENAI_API_KEY in your .env file.\n\n"
            f"Based on the repository context:\n{prompt[:300]}..."
        )

    async def generate_embedding(self, text: str) -> List[float]:
        if self.client:
            # Clean newlines for embedding model
            cleaned_text = text.replace("\n", " ")
            response = await self.client.embeddings.create(
                model=settings.EMBEDDING_MODEL or "text-embedding-3-small",
                input=cleaned_text
            )
            return response.data[0].embedding

        # Deterministic pseudo-embedding vector fallback for testing/local offline mode (1536 dim)
        import hashlib
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        import random
        rng = random.Random(seed)
        return [rng.uniform(-1.0, 1.0) for _ in range(1536)]
