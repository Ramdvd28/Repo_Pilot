from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.code_review_service import CodeReviewService
from app.services.pr_generator_service import PrGeneratorService

router = APIRouter()


class CodeReviewRequest(BaseModel):
    git_diff: str = Field(..., min_length=5, description="Git diff output to review")
    issue_number: Optional[int] = Field(None, description="Optional linked GitHub issue number")


class ReviewFindingSchema(BaseModel):
    severity: str = Field(..., description="'error', 'warning', or 'info'")
    file_path: str
    line_number: Optional[int] = None
    explanation: str
    suggested_fix: Optional[str] = None


class CodeReviewResponseSchema(BaseModel):
    score: int
    summary: str
    findings: List[ReviewFindingSchema]


class PrGenerateRequest(BaseModel):
    git_diff: str = Field(..., min_length=5, description="Git diff output")
    issue_number: Optional[int] = None
    test_results: Optional[str] = None


class PrGenerateResponseSchema(BaseModel):
    title: str
    markdown_description: str


@router.post("/{repo_id}/review", response_model=CodeReviewResponseSchema)
async def review_code_diff(
    repo_id: str,
    payload: CodeReviewRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Executes AI Code Review over a provided git diff.
    Returns structured findings with severity levels, explanations, and suggested code fixes.
    """
    reviewer = CodeReviewService(db)
    review_data = await reviewer.review_git_diff(
        repository_id=repo_id,
        git_diff=payload.git_diff,
        issue_number=payload.issue_number
    )
    return CodeReviewResponseSchema(**review_data)


@router.post("/{repo_id}/generate-pr", response_model=PrGenerateResponseSchema)
async def generate_pr_description(
    repo_id: str,
    payload: PrGenerateRequest
):
    """
    Generates a professional GitHub Pull Request title and Markdown description based on git diff and test results.
    """
    generator = PrGeneratorService()
    pr_data = await generator.generate_pr_description(
        git_diff=payload.git_diff,
        issue_number=payload.issue_number,
        test_results=payload.test_results
    )
    return PrGenerateResponseSchema(**pr_data)
