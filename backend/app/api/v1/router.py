from fastapi import APIRouter
from app.api.v1.endpoints import (
    repos,
    health,
    chat,
    issues,
    contribute,
    security,
    architecture,
    docs
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(repos.router, prefix="/repos", tags=["Repositories"])
api_router.include_router(chat.router, prefix="/repos", tags=["AI Chat"])
api_router.include_router(issues.router, prefix="/repos", tags=["Issues Assistant"])
api_router.include_router(contribute.router, prefix="/repos", tags=["Contribution Workspace"])
api_router.include_router(security.router, prefix="/repos", tags=["Security & Quality"])
api_router.include_router(architecture.router, prefix="/repos", tags=["Architecture Visualization"])
api_router.include_router(docs.router, prefix="/repos", tags=["Technical Documentation"])
