from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.doc_generator_service import DocGeneratorService

router = APIRouter()


class DocSectionSchema(BaseModel):
    id: str
    title: str


class TechDocsResponse(BaseModel):
    repository_id: str
    owner: str
    name: str
    documentation: str
    sections: List[DocSectionSchema]


@router.post("/{repo_id}/docs/generate", response_model=TechDocsResponse)
async def generate_technical_docs(
    repo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Synthesizes complete developer & architecture documentation suite for an analyzed repository.
    """
    service = DocGeneratorService(db)
    return await service.generate_technical_docs(repo_id)


@router.get("/{repo_id}/docs", response_model=TechDocsResponse)
async def get_technical_docs(
    repo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves technical documentation suite for a repository.
    """
    service = DocGeneratorService(db)
    return await service.generate_technical_docs(repo_id)
