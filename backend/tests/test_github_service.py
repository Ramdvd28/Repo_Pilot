import pytest
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
async def test_fetch_repository_metadata_mock(mocker):
    service = GitHubService()
    
    mock_repo_resp = mocker.Mock()
    mock_repo_resp.status_code = 200
    mock_repo_resp.json.return_value = {
        "description": "FastAPI framework",
        "stargazers_count": 75000,
        "forks_count": 6000,
        "open_issues_count": 100,
        "default_branch": "master",
        "language": "Python",
        "languages_url": "https://api.github.com/repos/fastapi/fastapi/languages",
        "topics": ["fastapi", "python"]
    }

    mock_lang_resp = mocker.Mock()
    mock_lang_resp.status_code = 200
    mock_lang_resp.json.return_value = {"Python": 100000}

    mock_client = mocker.AsyncMock()
    mock_client.get.side_effect = [mock_repo_resp, mock_lang_resp]

    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    mock_client.__aenter__.return_value = mock_client

    meta = await service.fetch_repository_metadata("https://github.com/fastapi/fastapi")
    assert meta["owner"] == "fastapi"
    assert meta["name"] == "fastapi"
    assert meta["stars"] == 75000
    assert meta["primary_language"] == "Python"
    assert "Python" in meta["languages"]
