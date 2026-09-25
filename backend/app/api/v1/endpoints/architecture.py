from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.architecture_service import ArchitectureService

router = APIRouter()


class NodeDataSchema(BaseModel):
    label: str
    category: str
    description: str
    icon: Optional[str] = "Layers"


class NodePositionSchema(BaseModel):
    x: float
    y: float


class NodeSchema(BaseModel):
    id: str
    type: str
    data: NodeDataSchema
    position: NodePositionSchema


class EdgeSchema(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None


class ArchitectureGraphResponse(BaseModel):
    repository_name: str
    total_nodes: int
    total_edges: int
    nodes: List[NodeSchema]
    edges: List[EdgeSchema]


@router.get("/{repo_id}/architecture", response_model=ArchitectureGraphResponse)
async def get_architecture_graph(
    repo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves extracted architectural components, nodes, and dependency edges
    for dynamic visual rendering in React Flow.
    """
    service = ArchitectureService(db)
    return await service.get_architecture_graph(repo_id)


@router.post("/{repo_id}/architecture/generate", response_model=ArchitectureGraphResponse)
async def generate_architecture_graph(
    repo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Triggers re-analysis of the repository structure to generate updated architecture graph data.
    """
    service = ArchitectureService(db)
    return await service.get_architecture_graph(repo_id)
