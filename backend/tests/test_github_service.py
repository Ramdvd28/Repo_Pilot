import pytest
import httpx
from fastapi import HTTPException
from app.services.github_service import GitHubService


def test_parse_github_url_valid():
    owner, repo = GitHubService.parse_github_url("https://github.com/fastapi/fastapi")
    assert owner == "fastapi"
    assert repo == "fastapi"

    owner, repo = GitHubService.parse_github_url("https://github.com/pallets/flask.git")
    assert owner == "pallets"
    assert repo == "flask"

    owner, repo = GitHubService.parse_github_url("facebook/react")
    assert owner == "facebook"
    assert repo == "react"


def test_parse_github_url_invalid():
    with pytest.raises(ValueError):
        GitHubService.parse_github_url("invalid-url-string")

    with pytest.raises(ValueError):
        GitHubService.parse_github_url("https://notgithub.com/user/repo")


@pytest.mark.asyncio
async def test_fetch_repository_metadata_normal_200(mocker):
    """
    Regression test: Verifies standard 200 OK response without redirects.
    """
    service = GitHubService()

    mock_repo_resp = mocker.Mock(spec=httpx.Response)
    mock_repo_resp.status_code = 200
    mock_repo_resp.json.return_value = {
        "description": "FastAPI framework",
        "stargazers_count": 75000,
        "forks_count": 6000,
        "open_issues_count": 100,
        "default_branch": "master",
        "language": "Python",
        "html_url": "https://github.com/fastapi/fastapi",
        "owner": {"login": "fastapi"},
        "name": "fastapi",
        "languages_url": "https://api.github.com/repos/fastapi/fastapi/languages",
        "topics": ["fastapi", "python"]
    }

    mock_lang_resp = mocker.Mock(spec=httpx.Response)
    mock_lang_resp.status_code = 200
    mock_lang_resp.json.return_value = {"Python": 100000}

    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = [mock_repo_resp, mock_lang_resp]

    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    mock_client.__aenter__.return_value = mock_client

    meta = await service.fetch_repository_metadata("https://github.com/fastapi/fastapi")
    assert meta["owner"] == "fastapi"
    assert meta["name"] == "fastapi"
    assert meta["github_url"] == "https://github.com/fastapi/fastapi"
    assert meta["stars"] == 75000
    assert meta["primary_language"] == "Python"
    assert "Python" in meta["languages"]


@pytest.mark.asyncio
async def test_fetch_repository_metadata_successful_redirect(mocker):
    """
    Regression test: Verifies that 301/302 redirects (such as facebook/react -> repositories/10270250)
    are followed correctly, Location header is used, and canonical URL is updated.
    """
    service = GitHubService()

    # 1. First call: 301 Moved Permanently with Location header
    mock_redirect_resp = mocker.Mock(spec=httpx.Response)
    mock_redirect_resp.status_code = 301
    mock_redirect_resp.headers = {"Location": "https://api.github.com/repositories/10270250"}
    mock_redirect_resp.json.return_value = {
        "message": "Moved Permanently",
        "url": "https://api.github.com/repositories/10270250"
    }

    # 2. Second call: 200 OK from the redirected location with updated canonical details
    mock_canonical_resp = mocker.Mock(spec=httpx.Response)
    mock_canonical_resp.status_code = 200
    mock_canonical_resp.json.return_value = {
        "description": "The library for web and native user interfaces.",
        "stargazers_count": 230000,
        "forks_count": 45000,
        "open_issues_count": 1200,
        "default_branch": "main",
        "language": "JavaScript",
        "html_url": "https://github.com/react/react",
        "owner": {"login": "react"},
        "name": "react",
        "languages_url": "https://api.github.com/repositories/10270250/languages",
        "topics": ["react", "javascript", "ui"]
    }

    # 3. Third call: languages breakdown
    mock_lang_resp = mocker.Mock(spec=httpx.Response)
    mock_lang_resp.status_code = 200
    mock_lang_resp.json.return_value = {"JavaScript": 500000, "HTML": 10000}

    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = [mock_redirect_resp, mock_canonical_resp, mock_lang_resp]

    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    mock_client.__aenter__.return_value = mock_client

    meta = await service.fetch_repository_metadata("https://github.com/facebook/react")

    # Verify canonical details were updated dynamically without hardcoding
    assert meta["github_url"] == "https://github.com/react/react"
    assert meta["owner"] == "react"
    assert meta["name"] == "react"
    assert meta["stars"] == 230000
    assert meta["primary_language"] == "JavaScript"
    assert "JavaScript" in meta["languages"]

    # Verify GET was called for the original URL and then for the redirect Location
    calls = mock_client.get.call_args_list
    assert calls[0].args[0] == "https://api.github.com/repos/facebook/react"
    assert calls[1].args[0] == "https://api.github.com/repositories/10270250"


@pytest.mark.asyncio
async def test_fetch_repository_metadata_preserves_token_on_trusted_host_and_strips_on_untrusted(mocker):
    """
    Regression test: Verifies that GitHub authentication tokens are safely preserved
    when following redirects on api.github.com, and stripped when redirected to an untrusted host.
    """
    service = GitHubService(token="ghp_secret_token_12345")

    # Test 1: Redirect to trusted api.github.com preserves token
    mock_redir_trusted = mocker.Mock(spec=httpx.Response)
    mock_redir_trusted.status_code = 301
    mock_redir_trusted.headers = {"Location": "https://api.github.com/repositories/99999"}

    mock_200_trusted = mocker.Mock(spec=httpx.Response)
    mock_200_trusted.status_code = 200
    mock_200_trusted.json.return_value = {
        "html_url": "https://github.com/trusted/repo",
        "owner": {"login": "trusted"},
        "name": "repo",
        "languages_url": None
    }

    mock_client_trusted = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client_trusted.get.side_effect = [mock_redir_trusted, mock_200_trusted]

    await service.get_with_redirects(mock_client_trusted, "https://api.github.com/repos/trusted/repo")

    call1_headers = mock_client_trusted.get.call_args_list[0].kwargs["headers"]
    call2_headers = mock_client_trusted.get.call_args_list[1].kwargs["headers"]
    assert call1_headers.get("Authorization") == "token ghp_secret_token_12345"
    assert call2_headers.get("Authorization") == "token ghp_secret_token_12345"

    # Test 2: Redirect to untrusted third-party host strips token
    mock_redir_untrusted = mocker.Mock(spec=httpx.Response)
    mock_redir_untrusted.status_code = 302
    mock_redir_untrusted.headers = {"Location": "https://untrusted-external-domain.com/data"}

    mock_200_untrusted = mocker.Mock(spec=httpx.Response)
    mock_200_untrusted.status_code = 200

    mock_client_untrusted = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client_untrusted.get.side_effect = [mock_redir_untrusted, mock_200_untrusted]

    await service.get_with_redirects(mock_client_untrusted, "https://api.github.com/repos/test/repo")

    untrusted_call_headers = mock_client_untrusted.get.call_args_list[1].kwargs["headers"]
    assert "Authorization" not in untrusted_call_headers


@pytest.mark.asyncio
async def test_fetch_repository_metadata_404_not_found(mocker):
    """
    Regression test: Verifies that 404 response raises HTTPException with 404 status.
    """
    service = GitHubService()

    mock_404_resp = mocker.Mock(spec=httpx.Response)
    mock_404_resp.status_code = 404

    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_404_resp

    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    mock_client.__aenter__.return_value = mock_client

    with pytest.raises(HTTPException) as exc_info:
        await service.fetch_repository_metadata("https://github.com/nonexistent/nonexistent-repo")

    assert exc_info.value.status_code == 404
    assert "not found or is private" in exc_info.value.detail


@pytest.mark.asyncio
async def test_fetch_repository_metadata_rate_limiting(mocker):
    """
    Regression test: Verifies that 403 (with rate limit exceeded) and 429 responses
    raise HTTPException with 429 status.
    """
    service = GitHubService()

    # Case 1: 403 with x-ratelimit-remaining: 0
    mock_403_resp = mocker.Mock(spec=httpx.Response)
    mock_403_resp.status_code = 403
    mock_403_resp.headers = {"x-ratelimit-remaining": "0"}
    mock_403_resp.json.return_value = {"message": "API rate limit exceeded for user"}
    mock_403_resp.text = '{"message": "API rate limit exceeded for user"}'

    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_403_resp

    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    mock_client.__aenter__.return_value = mock_client

    with pytest.raises(HTTPException) as exc_info:
        await service.fetch_repository_metadata("https://github.com/test/repo")

    assert exc_info.value.status_code == 429
    assert "rate limit reached" in exc_info.value.detail

    # Case 2: 429 Too Many Requests
    mock_429_resp = mocker.Mock(spec=httpx.Response)
    mock_429_resp.status_code = 429
    mock_429_resp.headers = {}
    mock_429_resp.json.return_value = {"message": "Too Many Requests"}
    mock_429_resp.text = '{"message": "Too Many Requests"}'

    mock_client.get.return_value = mock_429_resp

    with pytest.raises(HTTPException) as exc_info2:
        await service.fetch_repository_metadata("https://github.com/test/repo")

    assert exc_info2.value.status_code == 429
    assert "rate limit reached" in exc_info2.value.detail


@pytest.mark.asyncio
async def test_fetch_repository_metadata_redirect_errors(mocker):
    """
    Regression test: Verifies that redirect loops and missing Location headers
    raise clear 502 HTTPExceptions.
    """
    service = GitHubService()

    # 1. Missing Location header on 301
    mock_no_loc = mocker.Mock(spec=httpx.Response)
    mock_no_loc.status_code = 301
    mock_no_loc.headers = {}

    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_no_loc

    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    mock_client.__aenter__.return_value = mock_client

    with pytest.raises(HTTPException) as exc_info:
        await service.fetch_repository_metadata("https://github.com/test/repo")

    assert exc_info.value.status_code == 502
    assert "without a Location header" in exc_info.value.detail

    # 2. Redirect loop (> max_redirects)
    mock_loop = mocker.Mock(spec=httpx.Response)
    mock_loop.status_code = 301
    mock_loop.headers = {"Location": "https://api.github.com/repos/test/loop"}

    mock_client.get.return_value = mock_loop

    with pytest.raises(HTTPException) as exc_info2:
        await service.fetch_repository_metadata("https://github.com/test/repo")

    assert exc_info2.value.status_code == 502
    assert "Too many redirects" in exc_info2.value.detail
