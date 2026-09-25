import re
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.schema_models import CodeChunk


class VectorStoreService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_relevant_chunks(
        self,
        repository_id: str,
        query: str,
        top_k: int = 6
    ) -> List[CodeChunk]:
        """
        Retrieves top relevant CodeChunks for a query using TF-IDF / term overlap matching
        and symbol relevance scoring over indexed repository code chunks.
        """
        # Fetch all chunks for repository
        stmt = select(CodeChunk).where(CodeChunk.repository_id == repository_id)
        result = await self.db.execute(stmt)
        chunks = result.scalars().all()

        if not chunks:
            return []

        # Tokenize user query
        query_words = set(re.findall(r"\w+", query.lower()))
        if not query_words:
            return list(chunks[:top_k])

        scored_chunks = []
        for chunk in chunks:
            score = 0.0
            content_lower = chunk.content.lower()
            file_path_lower = chunk.file_path.lower()
            symbol_lower = (chunk.symbol_name or "").lower()

            for word in query_words:
                if len(word) < 2:
                    continue
                # Match in symbol name gives highest weight
                if symbol_lower and word in symbol_lower:
                    score += 10.0
                # Match in file path gives strong weight
                if word in file_path_lower:
                    score += 5.0
                # Match in content
                content_count = content_lower.count(word)
                if content_count > 0:
                    score += min(content_count, 5) * 1.5

            if score > 0:
                scored_chunks.append((score, chunk))

        # Sort by relevance score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        if scored_chunks:
            return [chunk for score, chunk in scored_chunks[:top_k]]

        # Fallback to top_k initial chunks if no direct term match
        return list(chunks[:top_k])
