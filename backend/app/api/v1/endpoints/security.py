from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.schema_models import SecurityFinding, CodeQualityFinding
from app.services.security_service import SecurityService

router = APIRouter()


class SecurityFindingSchema(BaseModel):
    id: Optional[str] = None
    rule_id: str
    tool_name: str
    severity: str
    file_path: str
    line_number: Optional[int] = None
    description: str
    ai_explanation: Optional[str] = None


class SecurityScanSummarySchema(BaseModel):
    repository_id: str
    total_findings: int
    counts: Dict[str, int]
    findings: List[SecurityFindingSchema]


class QualityFindingSchema(BaseModel):
    id: str
    tool_name: str
    category: str
    file_path: str
    line_number: Optional[int] = None
    message: str
    ai_suggestion: Optional[str] = None


@router.post("/{repo_id}/security/scan", response_model=SecurityScanSummarySchema)
async def run_security_scan(
    repo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers static security and code-quality scanning using Semgrep, Bandit,
    and OSV-Scanner rule sets. Enriches findings with AI remediation guidance.
    """
    service = SecurityService(db)
    return await service.run_security_scan(repo_id)


@router.get("/{repo_id}/security", response_model=List[SecurityFindingSchema])
async def get_security_findings(
    repo_id: str,
    severity: Optional[str] = Query(None, description="Filter by severity: 'critical', 'high', 'medium', 'low'"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves stored normalized security findings for a repository.
    """
    query = select(SecurityFinding).where(SecurityFinding.repository_id == repo_id)
    if severity:
        query = query.where(SecurityFinding.severity == severity.lower())

    query = query.order_by(SecurityFinding.line_number.asc())
    result = await db.execute(query)
    findings = result.scalars().all()

    return [
        SecurityFindingSchema(
            id=f.id,
            rule_id=f.rule_id,
            tool_name=f.tool_name,
            severity=f.severity,
            file_path=f.file_path,
            line_number=f.line_number,
            description=f.description,
            ai_explanation=f.ai_explanation
        )
        for f in findings
    ]


@router.get("/{repo_id}/quality", response_model=List[QualityFindingSchema])
async def get_quality_findings(
    repo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves code quality findings for a repository.
    """
    result = await db.execute(
        select(CodeQualityFinding).where(CodeQualityFinding.repository_id == repo_id)
    )
    findings = result.scalars().all()

    return [
        QualityFindingSchema(
            id=q.id,
            tool_name=q.tool_name,
            category=q.category,
            file_path=q.file_path,
            line_number=q.line_number,
            message=q.message,
            ai_suggestion=q.ai_suggestion
        )
        for q in findings
    ]
