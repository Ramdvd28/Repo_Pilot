from typing import Dict, Any
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.services.clone_service import CloneService
from app.services.repo_service import RepositoryService
from app.analyzers.architecture_analyzer import ArchitectureAnalyzer


class ArchitectureService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.clone_service = CloneService()
        self.repo_service = RepositoryService(db)
        self.analyzer = ArchitectureAnalyzer()

    async def get_architecture_graph(self, repo_id: str) -> Dict[str, Any]:
        repo = await self.repo_service.get_by_id(repo_id)
        if not repo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository '{repo_id}' not found."
            )

        repo_dir = self.clone_service.get_repo_dir(repo_id)
        if not repo_dir.exists():
            repo_dir = await self.clone_service.clone_repository(
                repo_id=repo.id,
                github_url=repo.github_url,
                default_branch=repo.default_branch or "main"
            )

        return self.analyzer.analyze_repository(repo_dir=repo_dir, repo_name=repo.name)
