from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.github_service import GitHubService
from app.services.repo_service import RepositoryService
from app.services.ingestion_service import IngestionService


def get_github_service() -> GitHubService:
    return GitHubService()


def get_repo_service(db: AsyncSession = Depends(get_db)) -> RepositoryService:
    return RepositoryService(db)


def get_ingestion_service(db: AsyncSession = Depends(get_db)) -> IngestionService:
    return IngestionService(db)
