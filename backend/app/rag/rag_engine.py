from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.factory import get_ai_provider
from app.rag.vector_store import VectorStoreService
from app.models.repository import Repository
from app.services.repo_service import RepositoryService

SYSTEM_PROMPT = """You are an expert software engineer analyzing a GitHub repository.

Answer questions using the repository context provided.

Never invent files, functions, classes, dependencies, APIs, or behavior.

If the provided context is insufficient, explicitly say so.

Always mention relevant file paths when applicable.

Distinguish facts directly supported by the repository from reasonable inferences.

Explain complex code clearly.

When describing a flow, explain it step-by-step."""


class RAGEngine:
    def __init__(self, db: AsyncSession, provider_name: str = "openai"):
        self.db = db
        self.vector_store = VectorStoreService(db)
        self.ai_provider = get_ai_provider(provider_name)
        self.repo_service = RepositoryService(db)

    async def answer_question(
        self,
        repository_id: str,
        question: str
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Executes repository RAG:
        1. Fetches repository details.
        2. Retrieves relevant code chunks from vector store.
        3. Formats dynamic repository context prompt.
        4. Queries LLM with grounding system prompt.
        5. Returns answer text and source attribution chunks.
        """
        repo = await self.repo_service.get_by_id(repository_id)
        repo_name = f"{repo.owner}/{repo.name}" if repo else "Repository"

        # Search top relevant chunks
        relevant_chunks = await self.vector_store.search_relevant_chunks(
            repository_id=repository_id,
            query=question,
            top_k=6
        )

        sources = []
        context_blocks = []

        if not relevant_chunks:
            context_text = f"Repository: {repo_name}\nNote: No indexed code chunks were found for this repository."
        else:
            for idx, chunk in enumerate(relevant_chunks, 1):
                symbol_info = f" (Symbol: {chunk.symbol_name})" if chunk.symbol_name else ""
                source_meta = {
                    "file_path": chunk.file_path,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "language": chunk.language,
                    "symbol_name": chunk.symbol_name,
                    "snippet": chunk.content[:250]
                }
                sources.append(source_meta)

                block = (
                    f"--- Source {idx} [{chunk.file_path} Lines {chunk.start_line}-{chunk.end_line}{symbol_info}] ---\n"
                    f"{chunk.content}\n"
                )
                context_blocks.append(block)

            context_text = "\n".join(context_blocks)

        prompt = (
            f"Repository: {repo_name}\n\n"
            f"User Question: {question}\n\n"
            f"Repository Context:\n{context_text}\n\n"
            f"Provide a clear, detailed explanation answering the question based strictly on the context above."
        )

        answer = await self.ai_provider.generate_text(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=1500
        )

        return answer, sources
