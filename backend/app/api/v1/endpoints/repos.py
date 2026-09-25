from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.repository import (
    RepoAnalyzeRequest,
    RepositoryResponse,
    RepoListResponse
)
from app.models.schema_models import RepositoryFile, CodeChunk
from app.services.github_service import GitHubService
from app.services.repo_service import RepositoryService
from app.services.ingestion_service import IngestionService
from app.services.clone_service import CloneService
from app.services.file_scanner_service import FileScannerService
from app.api.deps import get_github_service, get_repo_service, get_ingestion_service, get_db

router = APIRouter()


@router.post("/analyze", response_model=RepositoryResponse, status_code=status.HTTP_200_OK)
async def analyze_repository(
    payload: RepoAnalyzeRequest,
    github_service: GitHubService = Depends(get_github_service),
    repo_service: RepositoryService = Depends(get_repo_service)
):
    """
    Validates GitHub URL, fetches repository metadata from GitHub REST API,
    and stores/updates the repository record in the database.
    """
    meta = await github_service.fetch_repository_metadata(payload.github_url)
    repo = await repo_service.create_or_update_repo(meta)
    
    return RepositoryResponse(
        id=repo.id,
        github_url=repo.github_url,
        owner=repo.owner,
        name=repo.name,
        description=repo.description,
        stars=repo.stars,
        forks=repo.forks,
        open_issues=repo.open_issues,
        default_branch=repo.default_branch,
        primary_language=repo.primary_language,
        languages=repo.languages_json or {},
        topics=repo.topics_json or [],
        created_at=repo.created_at,
        updated_at=repo.updated_at,
        analyzed_at=repo.analyzed_at
    )


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: str,
    repo_service: RepositoryService = Depends(get_repo_service)
):
    """
    Retrieves stored metadata for an analyzed repository by ID.
    """
    repo = await repo_service.get_by_id(repo_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository with ID '{repo_id}' not found."
        )

    return RepositoryResponse(
        id=repo.id,
        github_url=repo.github_url,
        owner=repo.owner,
        name=repo.name,
        description=repo.description,
        stars=repo.stars,
        forks=repo.forks,
        open_issues=repo.open_issues,
        default_branch=repo.default_branch,
        primary_language=repo.primary_language,
        languages=repo.languages_json or {},
        topics=repo.topics_json or [],
        created_at=repo.created_at,
        updated_at=repo.updated_at,
        analyzed_at=repo.analyzed_at
    )


@router.get("/", response_model=RepoListResponse)
async def list_repositories(
    limit: int = 50,
    offset: int = 0,
    repo_service: RepositoryService = Depends(get_repo_service)
):
    """
    Lists all previously analyzed repositories.
    """
    repos = await repo_service.list_repositories(limit=limit, offset=offset)
    
    formatted = [
        RepositoryResponse(
            id=r.id,
            github_url=r.github_url,
            owner=r.owner,
            name=r.name,
            description=r.description,
            stars=r.stars,
            forks=r.forks,
            open_issues=r.open_issues,
            default_branch=r.default_branch,
            primary_language=r.primary_language,
            languages=r.languages_json or {},
            topics=r.topics_json or [],
            created_at=r.created_at,
            updated_at=r.updated_at,
            analyzed_at=r.analyzed_at
        )
        for r in repos
    ]

    return RepoListResponse(
        total=len(formatted),
        repositories=formatted
    )


# --- Phase 2 Endpoints ---

@router.post("/{repo_id}/ingest")
async def ingest_repository(
    repo_id: str,
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Clones the repository, scans the directory tree, filters files,
    parses source files, and chunks code into database records.
    """
    return await ingestion_service.ingest_repository(repo_id)


@router.get("/{repo_id}/files")
async def get_repository_files(
    repo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Returns all indexed files for a repository.
    """
    result = await db.execute(
        select(RepositoryFile).where(RepositoryFile.repository_id == repo_id).order_by(RepositoryFile.file_path)
    )
    files = result.scalars().all()
    
    return [
        {
            "id": f.id,
            "file_path": f.file_path,
            "language": f.language,
            "size_bytes": f.size_bytes,
            "total_lines": f.total_lines
        }
        for f in files
    ]


@router.get("/{repo_id}/files/content")
async def get_file_content(
    repo_id: str,
    path: str = Query(..., description="Relative file path inside the repository"),
    db: AsyncSession = Depends(get_db)
):
    """
    Safely reads file content for a relative path inside the repository.
    Strictly prevents path traversal attacks.
    """
    clone_service = CloneService()
    base_dir = clone_service.get_repo_dir(repo_id)

    # Validate boundary path traversal check
    target_path = FileScannerService.validate_safe_path(base_dir, path)

    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{path}' not found in repository."
        )

    try:
        with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        language = FileScannerService.detect_language(target_path) or "Plain Text"

        return {
            "repository_id": repo_id,
            "file_path": path,
            "language": language,
            "content": content
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file content: {str(e)}"
        )


@router.get("/{repo_id}/chunks")
async def get_repository_chunks(
    repo_id: str,
    file_path: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves stored code chunks for a repository.
    """
    query = select(CodeChunk).where(CodeChunk.repository_id == repo_id)
    if file_path:
        query = query.where(CodeChunk.file_path == file_path)

    query = query.order_by(CodeChunk.file_path, CodeChunk.start_line).offset(offset).limit(limit)
    result = await db.execute(query)
    chunks = result.scalars().all()

    return [
        {
            "id": c.id,
            "file_path": c.file_path,
            "language": c.language,
            "start_line": c.start_line,
            "end_line": c.end_line,
            "symbol_name": c.symbol_name,
            "content": c.content
        }
        for c in chunks
    ]
