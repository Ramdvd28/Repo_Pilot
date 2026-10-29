import re
from typing import Tuple, Dict, Any, Optional, List
from urllib.parse import urlparse, urljoin
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

    @staticmethod
    def is_trusted_github_host(hostname: Optional[str]) -> bool:
        """
        Checks if a hostname is a trusted GitHub API host where authentication
        tokens may be safely forwarded during redirects.
        """
        if not hostname:
            return False
        host = hostname.lower().strip()
        return host == "api.github.com"

    async def get_with_redirects(
        self,
        client: httpx.AsyncClient,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        max_redirects: int = 5
    ) -> Tuple[httpx.Response, List[str]]:
        """
        Executes an HTTP GET request, safely following HTTP redirects (301, 302, 307, 308):
        - Follows redirects using the response's Location header.
        - Preserves GitHub authentication headers for trusted hosts (api.github.com).
        - Safely strips authentication tokens if redirected to any untrusted or third-party host.
        - Returns the final response and a list of redirect URLs traversed.
        """
        current_url = url
        req_headers = dict(headers or self.headers)
        redirect_history: List[str] = []
        redirect_count = 0

        while redirect_count <= max_redirects:
            try:
                response = await client.get(current_url, headers=req_headers, follow_redirects=False)
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Unable to connect to GitHub API: {str(e)}"
                )

            # Check if response is an HTTP redirect (301 Moved Permanently, 302 Found, 307/308 Temporary/Permanent Redirect)
            if response.status_code in (301, 302, 307, 308):
                location = response.headers.get("Location")
                if not location:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"GitHub API returned redirect status {response.status_code} without a Location header."
                    )

                next_url = urljoin(current_url, location)
                redirect_history.append(next_url)

                redirect_host = urlparse(next_url).hostname
                # Preserve authorization token only if target host is a trusted GitHub API host.
                # Never forward credentials to untrusted/external hosts.
                if not self.is_trusted_github_host(redirect_host):
                    req_headers.pop("Authorization", None)
                elif self.token and "Authorization" not in req_headers:
                    req_headers["Authorization"] = f"token {self.token}"

                current_url = next_url
                redirect_count += 1
                if redirect_count > max_redirects:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="Too many redirects encountered while querying GitHub API."
                    )
                continue

            return response, redirect_history

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Too many redirects encountered while querying GitHub API."
        )

    def _handle_error_response(self, response: httpx.Response, owner: str, repo: str) -> None:
        """
        Translates GitHub API HTTP error responses into descriptive HTTPExceptions.
        """
        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"GitHub repository '{owner}/{repo}' not found or is private."
            )

        if response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired GitHub token. Please verify GITHUB_TOKEN in settings."
            )

        # Rate limit handling: GitHub sends 403 or 429 when rate limited
        if response.status_code in (403, 429):
            remaining = response.headers.get("x-ratelimit-remaining")
            body_text = ""
            try:
                err_json = response.json()
                body_text = err_json.get("message", "")
            except Exception:
                body_text = response.text

            if response.status_code == 429 or remaining == "0" or "rate limit" in body_text.lower():
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="GitHub API rate limit reached or access restricted. Please configure GITHUB_TOKEN in settings to increase quota."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"GitHub API access restricted: {body_text or 'Access forbidden.'}"
                )

        if response.status_code != 200:
            error_detail = response.text
            try:
                err_json = response.json()
                error_detail = err_json.get("message", response.text)
            except Exception:
                pass

            raise HTTPException(
                status_code=response.status_code,
                detail=f"GitHub API error: {error_detail}"
            )

    async def fetch_repository_metadata(self, github_url: str) -> Dict[str, Any]:
        try:
            owner, repo = self.parse_github_url(github_url)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        async with httpx.AsyncClient(timeout=15.0) as client:
            repo_url = f"https://api.github.com/repos/{owner}/{repo}"
            response, _ = await self.get_with_redirects(client, repo_url)

            if response.status_code != 200:
                self._handle_error_response(response, owner, repo)

            repo_data = response.json()

            # Canonical repository details from the final response
            canonical_owner = (
                repo_data.get("owner", {}).get("login")
                if isinstance(repo_data.get("owner"), dict)
                else owner
            )
            canonical_name = repo_data.get("name") or repo
            canonical_url = (
                repo_data.get("html_url")
                or f"https://github.com/{canonical_owner}/{canonical_name}"
            )

            # Fetch language breakdown using the canonical languages_url
            languages_url = repo_data.get("languages_url")
            languages = {}
            if languages_url:
                try:
                    lang_resp, _ = await self.get_with_redirects(client, languages_url)
                    if lang_resp.status_code == 200:
                        languages = lang_resp.json()
                except Exception:
                    languages = {}

            return {
                "github_url": canonical_url,
                "owner": canonical_owner,
                "name": canonical_name,
                "description": repo_data.get("description"),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "open_issues": repo_data.get("open_issues_count", 0),
                "default_branch": repo_data.get("default_branch", "main"),
                "primary_language": repo_data.get("language"),
                "languages": languages,
                "topics": repo_data.get("topics", [])
            }
