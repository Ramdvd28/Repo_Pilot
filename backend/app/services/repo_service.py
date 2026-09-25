from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.repository import Repository


class RepositoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, repo_id: str) -> Optional[Repository]:
        result = await self.db.execute(select(Repository).where(Repository.id == repo_id))
        return result.scalars().first()

    async def get_by_url(self, github_url: str) -> Optional[Repository]:
        result = await self.db.execute(select(Repository).where(Repository.github_url == github_url))
        return result.scalars().first()

    async def get_by_owner_name(self, owner: str, name: str) -> Optional[Repository]:
        result = await self.db.execute(
            select(Repository).where(Repository.owner == owner, Repository.name == name)
        )
        return result.scalars().first()

    async def create_or_update_repo(self, repo_data: Dict[str, Any]) -> Repository:
        github_url = repo_data["github_url"]
        existing = await self.get_by_url(github_url)
        
        now = datetime.now(timezone.utc)
        
        if existing:
            existing.description = repo_data.get("description", existing.description)
            existing.stars = repo_data.get("stars", existing.stars)
            existing.forks = repo_data.get("forks", existing.forks)
            existing.open_issues = repo_data.get("open_issues", existing.open_issues)
            existing.default_branch = repo_data.get("default_branch", existing.default_branch)
            existing.primary_language = repo_data.get("primary_language", existing.primary_language)
            existing.languages_json = repo_data.get("languages", existing.languages_json)
            existing.topics_json = repo_data.get("topics", existing.topics_json)
            existing.analyzed_at = now
            existing.updated_at = now
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            repo = Repository(
                github_url=github_url,
                owner=repo_data["owner"],
                name=repo_data["name"],
                description=repo_data.get("description"),
                stars=repo_data.get("stars", 0),
                forks=repo_data.get("forks", 0),
                open_issues=repo_data.get("open_issues", 0),
                default_branch=repo_data.get("default_branch", "main"),
                primary_language=repo_data.get("primary_language"),
                languages_json=repo_data.get("languages", {}),
                topics_json=repo_data.get("topics", []),
                analyzed_at=now
            )
            self.db.add(repo)
            await self.db.commit()
            await self.db.refresh(repo)
            return repo

    async def list_repositories(self, limit: int = 50, offset: int = 0) -> List[Repository]:
        result = await self.db.execute(
            select(Repository).order_by(Repository.updated_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())
