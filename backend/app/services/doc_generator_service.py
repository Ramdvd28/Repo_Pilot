from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.services.repo_service import RepositoryService
from app.services.file_scanner_service import FileScannerService
from app.services.clone_service import CloneService
from app.ai.factory import get_ai_provider


class DocGeneratorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo_service = RepositoryService(db)
        self.clone_service = CloneService()
        self.ai_provider = get_ai_provider()

    async def generate_technical_docs(self, repo_id: str) -> Dict[str, Any]:
        repo = await self.repo_service.get_by_id(repo_id)
        if not repo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository '{repo_id}' not found."
            )

        repo_dir = self.clone_service.get_repo_dir(repo_id)
        scanned_summary = ""
        if repo_dir.exists():
            scanner = FileScannerService()
            files = scanner.scan_repository(repo_dir)
            top_files = [f["file_path"] for f in files[:15]]
            scanned_summary = f"Scanned {len(files)} files. Key files: {', '.join(top_files)}."

        prompt = (
            f"Generate a professional, comprehensive technical documentation suite for repository '{repo.owner}/{repo.name}'.\n"
            f"Description: {repo.description or 'Open-source software project'}\n"
            f"Primary Language: {repo.primary_language or 'Python / TypeScript'}\n"
            f"Languages: {repo.languages_json}\n"
            f"Codebase info: {scanned_summary}\n\n"
            f"Create markdown documentation structured with clear headings:\n"
            f"1. Executive Summary & Core Value Proposition\n"
            f"2. System Architecture & Module Breakdown\n"
            f"3. API Reference & Key Endpoints\n"
            f"4. Database Schema & Data Models\n"
            f"5. Local Setup, Configuration & Testing Guide\n"
        )

        doc_content = await self.ai_provider.generate_text(
            prompt=prompt,
            system_prompt="You are a principal technical author and software architect creating production-grade developer documentation.",
            temperature=0.2,
            max_tokens=1500
        )

        return {
            "repository_id": repo_id,
            "owner": repo.owner,
            "name": repo.name,
            "documentation": doc_content,
            "sections": [
                {"id": "summary", "title": "Executive Summary"},
                {"id": "architecture", "title": "System Architecture"},
                {"id": "api", "title": "API Specification"},
                {"id": "database", "title": "Database Schema"},
                {"id": "setup", "title": "Setup & Quickstart"}
            ]
        }
