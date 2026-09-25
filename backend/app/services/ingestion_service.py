import time
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from fastapi import HTTPException, status

from app.models.repository import Repository
from app.models.schema_models import RepositoryFile, CodeChunk
from app.services.clone_service import CloneService
from app.services.file_scanner_service import FileScannerService
from app.services.chunker_service import CodeChunkerService
from app.services.repo_service import RepositoryService


class IngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.clone_service = CloneService()
        self.scanner_service = FileScannerService()
        self.chunker_service = CodeChunkerService()
        self.repo_service = RepositoryService(db)

    async def ingest_repository(self, repo_id: str) -> Dict[str, Any]:
        start_time = time.time()

        # 1. Fetch Repository record
        repo = await self.repo_service.get_by_id(repo_id)
        if not repo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository with ID '{repo_id}' not found."
            )

        # 2. Clone repository to storage
        cloned_dir = await self.clone_service.clone_repository(
            repo_id=repo.id,
            github_url=repo.github_url,
            default_branch=repo.default_branch or "main"
        )

        # 3. Scan directory tree
        scanned_files = self.scanner_service.scan_repository(cloned_dir)

        # 4. Clear existing files and chunks in DB for this repo_id
        await self.db.execute(delete(RepositoryFile).where(RepositoryFile.repository_id == repo.id))
        await self.db.execute(delete(CodeChunk).where(CodeChunk.repository_id == repo.id))

        total_files_indexed = 0
        total_chunks_created = 0
        languages_count: Dict[str, int] = {}

        # 5. Process files and generate chunks
        for file_info in scanned_files:
            rel_path = file_info["file_path"]
            full_path = file_info["full_path"]
            language = file_info["language"]
            size_bytes = file_info["size_bytes"]
            total_lines = file_info["total_lines"]

            # Save RepositoryFile model
            file_record = RepositoryFile(
                repository_id=repo.id,
                file_path=rel_path,
                language=language,
                size_bytes=size_bytes,
                total_lines=total_lines
            )
            self.db.add(file_record)
            total_files_indexed += 1

            if language:
                languages_count[language] = languages_count.get(language, 0) + 1

            # Read file content safely for chunking
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            # Generate chunks
            chunks_data = self.chunker_service.chunk_file_content(
                content=content,
                file_path=rel_path,
                language=language
            )

            for chunk_dict in chunks_data:
                chunk_record = CodeChunk(
                    repository_id=repo.id,
                    file_path=chunk_dict["file_path"],
                    language=chunk_dict["language"],
                    start_line=chunk_dict["start_line"],
                    end_line=chunk_dict["end_line"],
                    symbol_name=chunk_dict["symbol_name"],
                    content=chunk_dict["content"]
                )
                self.db.add(chunk_record)
                total_chunks_created += 1

        await self.db.commit()

        duration = round(time.time() - start_time, 2)

        return {
            "repository_id": repo.id,
            "status": "success",
            "files_indexed": total_files_indexed,
            "chunks_created": total_chunks_created,
            "languages_found": languages_count,
            "ingestion_time_seconds": duration
        }
