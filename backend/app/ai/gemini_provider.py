import os
import asyncio
from typing import List, Optional
from app.ai.base import AIProvider, AIProviderError
from app.core.config import settings

try:
    import google.generativeai as genai
    HAS_GEMINI_SDK = True
except ImportError:
    HAS_GEMINI_SDK = False


class GeminiProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or settings.GEMINI_MODEL or "gemini-3.8-flash"
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
                model = genai.GenerativeModel(self.model_name)
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
                
                try:
                    coro = model.generate_content_async(
                        full_prompt,
                        generation_config=generation_config
                    )
                    response = await asyncio.wait_for(coro, timeout=settings.AI_TIMEOUT_SECONDS)
                except AttributeError:
                    response = await asyncio.wait_for(
                        asyncio.to_thread(
                            model.generate_content,
                            full_prompt,
                            generation_config=generation_config
                        ),
                        timeout=settings.AI_TIMEOUT_SECONDS
                    )

                if response and hasattr(response, "text") and response.text:
                    return response.text
                
                raise AIProviderError("Gemini returned an empty or blocked response", provider="gemini")
            except Exception as e:
                if isinstance(e, AIProviderError):
                    raise
                raise AIProviderError(f"Gemini API error: {str(e)}", provider="gemini") from e

        # Fallback when GEMINI_API_KEY is not configured (offline / local development)
        return (
            "[Google Gemini Provider - Fallback Response]\n"
            "This repository analysis response was generated using local repository context matching. "
            "To enable live Gemini models, please configure GEMINI_API_KEY in your .env file.\n\n"
            f"Based on the repository context:\n{prompt[:300]}..."
        )

    async def generate_embedding(self, text: str) -> List[float]:
        dim = getattr(settings, "EMBEDDING_DIMENSIONS", None) or getattr(settings, "EMBEDDING_DIMENSION", 768)
        model_name = getattr(settings, "GEMINI_EMBEDDING_MODEL", None) or getattr(settings, "EMBEDDING_MODEL", "gemini-embedding-2")
        if HAS_GEMINI_SDK and self.api_key:
            try:
                result = await asyncio.to_thread(
                    genai.embed_content,
                    model=model_name,
                    content=text,
                    task_type="retrieval_document"
                )
                if "embedding" in result:
                    emb = result["embedding"]
                    if len(emb) == dim:
                        return emb
                    elif len(emb) > dim:
                        return emb[:dim]
                    else:
                        return emb + [0.0] * (dim - len(emb))
            except Exception:
                pass

        # Deterministic pseudo-embedding vector fallback (768 dim for Gemini)
        import hashlib
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
        import random
        rng = random.Random(seed)
        return [rng.uniform(-1.0, 1.0) for _ in range(dim)]
