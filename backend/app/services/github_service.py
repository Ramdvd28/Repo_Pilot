import re
from typing import Tuple, Dict, Any, Optional
import httpx
from fastapi import HTTPException, status
from app.core.config import settings


class GitHubService:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "RepoPilot-AI-Assistant"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    @staticmethod
    def parse_github_url(url: str) -> Tuple[str, str]:
        """
        Parses GitHub URL or owner/repo string into (owner, repo).
        Throws ValueError if format is invalid.
        """
        clean = url.strip()
        if clean.endswith(".git"):
            clean = clean[:-4]
        
        regex = r"^(?:https?://github\.com/)?([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)/?$"
        match = re.match(regex, clean)
        if not match:
            raise ValueError("Invalid GitHub URL format. Please provide a URL like https://github.com/owner/repo")
        
        return match.group(1), match.group(2)

    async def fetch_repository_metadata(self, github_url: str) -> Dict[str, Any]:
        owner, repo = self.parse_github_url(github_url)
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            repo_url = f"https://api.github.com/repos/{owner}/{repo}"
            try:
                response = await client.get(repo_url, headers=self.headers)
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Unable to connect to GitHub API: {str(e)}"
                )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"GitHub repository '{owner}/{repo}' not found or is private."
                )
            elif response.status_code == 403 and "rate limit" in response.text.lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="GitHub API rate limit exceeded. Provide a GITHUB_TOKEN in settings to increase quota."
                )
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"GitHub API error: {response.text}"
                )

            repo_data = response.json()

            # Fetch language breakdown
            languages_url = repo_data.get("languages_url")
            languages = {}
            if languages_url:
                try:
                    lang_resp = await client.get(languages_url, headers=self.headers)
                    if lang_resp.status_code == 200:
                        languages = lang_resp.json()
                except Exception:
                    languages = {}

            return {
                "github_url": f"https://github.com/{owner}/{repo}",
                "owner": owner,
                "name": repo,
                "description": repo_data.get("description"),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "open_issues": repo_data.get("open_issues_count", 0),
                "default_branch": repo_data.get("default_branch", "main"),
                "primary_language": repo_data.get("language"),
                "languages": languages,
                "topics": repo_data.get("topics", [])
            }
