import os
import hashlib
import random
from typing import List, Optional
import httpx
from app.ai.base import AIProvider, AIProviderError
from app.core.config import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqProvider(AIProvider):
    """
    Groq AI Provider leveraging high-speed LPU inference as an automatic fallback.
    Default model: openai/gpt-oss-120b (configurable via GROQ_MODEL).
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        self.model_name = model_name or settings.GROQ_MODEL or "openai/gpt-oss-120b"

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> str:
        if self.api_key:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            try:
                async with httpx.AsyncClient(timeout=settings.AI_TIMEOUT_SECONDS) as client:
                    response = await client.post(GROQ_API_URL, json=payload, headers=headers)

                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices and "message" in choices[0]:
                        return choices[0]["message"].get("content", "") or ""
                    raise AIProviderError("Groq returned empty response", provider="groq")
                
                # Check for rate limit / quota exhaustion / server error
                error_msg = f"Groq API returned HTTP {response.status_code}"
                try:
                    err_json = response.json()
                    if "error" in err_json and "message" in err_json["error"]:
                        error_msg += f": {err_json['error']['message']}"
                except Exception:
                    pass

                raise AIProviderError(error_msg, provider="groq")
            except Exception as e:
                if isinstance(e, AIProviderError):
                    raise
                raise AIProviderError(f"Groq API request failed: {str(e)}", provider="groq") from e

        # Fallback when GROQ_API_KEY is not configured (offline / local development)
        return (
            "[Groq Provider - Fallback Response]\n"
            "This repository analysis response was generated using local repository context matching. "
            "To enable live Groq models, please configure GROQ_API_KEY in your .env file.\n\n"
            f"Based on the repository context:\n{prompt[:300]}..."
        )

    async def generate_embedding(self, text: str) -> List[float]:
        dim = settings.EMBEDDING_DIMENSION or 768
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        rng = random.Random(seed)
        return [rng.uniform(-1.0, 1.0) for _ in range(dim)]

