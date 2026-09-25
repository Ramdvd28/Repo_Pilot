from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.schema_models import Issue
from app.services.issue_analyzer_service import IssueAnalyzerService

router = APIRouter()


class IssueResponse(BaseModel):
    id: str
    repository_id: str
    issue_number: int
    title: str
    description: Optional[str] = None
    difficulty_level: str
    relevant_files: List[str] = Field(default_factory=list)
    suggested_approach: Optional[str] = None
    created_at: Any


@router.post("/{repo_id}/issues/sync", response_model=List[IssueResponse])
async def sync_repository_issues(
    repo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetches open GitHub issues, analyzes them with AI & RAG context,
    classifies difficulty levels, and saves analysis to the database.
    """
    analyzer = IssueAnalyzerService(db)
    records = await analyzer.sync_and_analyze_issues(repo_id)
    return [
        IssueResponse(
            id=i.id,
            repository_id=i.repository_id,
            issue_number=i.issue_number,
            title=i.title,
            description=i.description,
            difficulty_level=i.difficulty_level,
            relevant_files=i.relevant_files_json or [],
            suggested_approach=i.suggested_approach,
            created_at=i.created_at
        )
        for i in records
    ]


@router.get("/{repo_id}/issues", response_model=List[IssueResponse])
async def list_repository_issues(
    repo_id: str,
    difficulty: Optional[str] = Query(None, description="Filter by difficulty: 'beginner', 'intermediate', or 'advanced'"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves stored GitHub issues for a repository with optional difficulty filtering.
    """
    query = select(Issue).where(Issue.repository_id == repo_id)
    if difficulty:
        query = query.where(Issue.difficulty_level == difficulty.lower())

    query = query.order_by(Issue.issue_number.asc())
    result = await db.execute(query)
    issues = result.scalars().all()

    return [
        IssueResponse(
            id=i.id,
            repository_id=i.repository_id,
            issue_number=i.issue_number,
            title=i.title,
            description=i.description,
            difficulty_level=i.difficulty_level,
            relevant_files=i.relevant_files_json or [],
            suggested_approach=i.suggested_approach,
            created_at=i.created_at
        )
        for i in issues
    ]


@router.get("/{repo_id}/issues/{issue_number}", response_model=IssueResponse)
async def get_issue_detail(
    repo_id: str,
    issue_number: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves analysis details for a single issue by issue number.
    """
    result = await db.execute(
        select(Issue).where(Issue.repository_id == repo_id, Issue.issue_number == issue_number)
    )
    issue = result.scalars().first()
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Issue #{issue_number} not found for repository '{repo_id}'."
        )

    return IssueResponse(
        id=issue.id,
        repository_id=issue.repository_id,
        issue_number=issue.issue_number,
        title=issue.title,
        description=issue.description,
        difficulty_level=issue.difficulty_level,
        relevant_files=issue.relevant_files_json or [],
        suggested_approach=issue.suggested_approach,
        created_at=issue.created_at
    )
