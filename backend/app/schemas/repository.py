from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, HttpUrl, Field, field_validator
import re


class RepoAnalyzeRequest(BaseModel):
    github_url: str = Field(..., description="Full GitHub repository URL or owner/repo format")

    @field_validator("github_url")
    def validate_url(cls, v: str) -> str:
        clean_url = v.strip()
        # Clean trailing .git if present
        if clean_url.endswith(".git"):
            clean_url = clean_url[:-4]
        
        # Match standard github url pattern or owner/repo shorthand
        github_regex = r"^(https?://github\.com/)?([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)/?$"
        match = re.match(github_regex, clean_url)
        if not match:
            raise ValueError("Invalid GitHub repository URL format. Example: https://github.com/fastapi/fastapi or fastapi/fastapi")
        
        owner, repo = match.group(2), match.group(3)
        return f"https://github.com/{owner}/{repo}"


class RepositoryResponse(BaseModel):
    id: str
    github_url: str
    owner: str
    name: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    default_branch: str = "main"
    primary_language: Optional[str] = None
    languages: Dict[str, Any] = Field(default_factory=dict)
    topics: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    analyzed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RepoListResponse(BaseModel):
    total: int
    repositories: List[RepositoryResponse]


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
    version: str = "0.1.0"
