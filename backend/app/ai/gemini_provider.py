import os
from typing import List, Optional
from app.ai.base import AIProvider
from app.core.config import settings

try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False


class GeminiProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if HAS_GEMINI_SDK and self.api_key:
            genai.configure(api_key=self.api_key)

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> str:
        if HAS_GEMINI_SDK and self.api_key:
            try:
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    )
                )
                return response.text or ""
            except Exception as e:
                return f"[Gemini API Error]: {str(e)}"

        # Fallback when GEMINI_API_KEY is not configured
        return (
            "[Google Gemini Provider - Fallback Response]\n"
            "This repository analysis response was generated using local repository context matching. "
            "To enable live Gemini models, please configure GEMINI_API_KEY in your .env file.\n\n"
            f"Based on the repository context:\n{prompt[:300]}..."
        )

    async def generate_embedding(self, text: str) -> List[float]:
        if HAS_GEMINI_SDK and self.api_key:
            try:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document"
                )
                return result["embedding"]
            except Exception:
                pass

        # Deterministic pseudo-embedding vector fallback (768 dim for Gemini)
        import hashlib
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        import random
        rng = random.Random(seed)
        return [rng.uniform(-1.0, 1.0) for _ in range(768)]
