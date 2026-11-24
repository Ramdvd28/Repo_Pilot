import re
import hashlib
from typing import List, Dict, Any, Tuple, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.base import AIProviderError
from app.ai.factory import get_ai_provider
from app.rag.vector_store import VectorStoreService
from app.models.repository import Repository
from app.services.repo_service import RepositoryService

SYSTEM_PROMPT = """You are an expert software engineer analyzing a GitHub repository.

Answer questions using the repository context provided.

Never invent files, functions, classes, dependencies, APIs, or behavior.

If the provided context is insufficient, explicitly say so.

Always mention relevant file paths when applicable.
Always mention line numbers when available from the provided sources.

Distinguish facts directly supported by the repository from reasonable inferences.

Keep responses concise, clear, and focused on the code context."""


class RAGEngine:
    def __init__(self, db: AsyncSession, provider_name: Optional[str] = None):
        self.db = db
        self.vector_store = VectorStoreService(db)
        self.ai_provider = get_ai_provider(provider_name)
        self.repo_service = RepositoryService(db)

    def _check_metadata_shortcut(self, repo: Repository, question: str) -> Optional[str]:
        """
        Answers direct metadata questions without consuming LLM API quota or introducing latency.
        """
        clean_q = question.lower().strip().rstrip("?.")
        repo_name = f"{repo.owner}/{repo.name}"

        # Primary language queries
        if clean_q in (
            "what is the primary language",
            "what language is this",
            "what programming language is used",
            "primary language",
            "what language does this project use"
        ):
            lang = repo.primary_language or "not specified"
            return f"The primary programming language of **{repo_name}** is **{lang}**."

        # Star count queries
        if clean_q in (
            "how many stars does this repo have",
            "how many stars",
            "stars count",
            "star count",
            "stars"
        ):
            return f"**{repo_name}** currently has **{repo.stars:,}** GitHub stars."

        # Fork count queries
        if clean_q in (
            "how many forks does this repo have",
            "how many forks",
            "fork count",
            "forks"
        ):
            return f"**{repo_name}** has **{repo.forks:,}** forks."

        # Default branch queries
        if clean_q in (
            "what is the default branch",
            "default branch",
            "main branch"
        ):
            return f"The default branch of **{repo_name}** is **{repo.default_branch}**."

        # Owner / repository name queries
        if clean_q in (
            "who owns this repository",
            "who is the owner",
            "what is the repository name",
            "repo owner"
        ):
            return f"This repository is **{repo.name}**, owned by **{repo.owner}**."

        return None

    async def answer_question(
        self,
        repository_id: str,
        question: str
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Executes focused repository RAG:
        1. Validates repository existence.
        2. Fast-paths direct repository metadata questions to save LLM quota.
        3. Retrieves relevant code chunks from vector store.
        4. Deduplicates overlapping and identical chunks.
        5. Builds focused repository context.
        6. Queries AI Provider (Gemini Primary with Groq Automatic Fallback).
        7. Returns grounded answer with sources.
        """
        repo = await self.repo_service.get_by_id(repository_id)
        if not repo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository '{repository_id}' not found."
            )
        repo_name = f"{repo.owner}/{repo.name}"

        # 1. Check metadata shortcut
        metadata_answer = self._check_metadata_shortcut(repo, question)
        if metadata_answer:
            return metadata_answer, []

        # 2. Retrieve top chunks (retrieves up to 6)
        raw_chunks = await self.vector_store.search_relevant_chunks(
            repository_id=repository_id,
            query=question,
            top_k=6
        )

        # 3. Deduplicate chunks & build focused context
        sources: List[Dict[str, Any]] = []
        context_blocks: List[str] = []
        seen_spans = set()
        seen_hashes = set()

        for chunk in raw_chunks:
            span_key = (chunk.file_path, chunk.start_line, chunk.end_line)
            if span_key in seen_spans:
                continue
            seen_spans.add(span_key)

            # Content hash to filter identical duplicate blocks
            content_snippet = chunk.content.strip()
            content_hash = hashlib.md5(content_snippet.encode("utf-8")).hexdigest()
            if content_hash in seen_hashes:
                continue
            seen_hashes.add(content_hash)

            symbol_info = f" (Symbol: {chunk.symbol_name})" if chunk.symbol_name else ""
            source_meta = {
                "file_path": chunk.file_path,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "language": chunk.language,
                "symbol_name": chunk.symbol_name,
                "snippet": content_snippet[:250]
            }
            sources.append(source_meta)

            # Limit individual chunk length in context to maintain high focus
            focused_content = content_snippet[:1500]
            block = (
                f"--- Source {len(sources)} [{chunk.file_path} Lines {chunk.start_line}-{chunk.end_line}{symbol_info}] ---\n"
                f"{focused_content}\n"
            )
            context_blocks.append(block)

            # Limit to at most 5 unique sources for context efficiency
            if len(sources) >= 5:
                break

        if not context_blocks:
            context_text = f"Repository: {repo_name}\nNote: No indexed code chunks were found for this query in the repository."
        else:
            context_text = "\n".join(context_blocks)

        prompt = (
            f"Repository: {repo_name}\n\n"
            f"User Question: {question}\n\n"
            f"Repository Context:\n{context_text}\n\n"
            f"Provide a clear, detailed explanation answering the question based strictly on the repository context above."
        )

        try:
            answer = await self.ai_provider.generate_text(
                prompt=prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.2,
                max_tokens=1500
            )
            return answer, sources
        except AIProviderError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is temporarily unavailable. Please try again in a moment."
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service is temporarily unavailable. Please try again in a moment."
            ) from e
