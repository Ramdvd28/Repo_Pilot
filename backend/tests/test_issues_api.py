import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_issues_api_endpoints(async_client: AsyncClient, mocker):
    # Mock GitHub Service metadata
    mock_meta = {
        "github_url": "https://github.com/sample/issueapi",
        "owner": "sample",
        "name": "issueapi",
        "description": "Issue API test repository",
        "stars": 12,
        "forks": 3,
        "open_issues": 2,
        "default_branch": "main",
        "primary_language": "Python",
        "languages": {"Python": 100},
        "topics": []
    }

    mocker.patch(
        "app.services.github_service.GitHubService.fetch_repository_metadata",
        return_value=mock_meta
    )

    # 1. Create repository
    resp = await async_client.post(
        "/api/v1/repos/analyze",
        json={"github_url": "https://github.com/sample/issueapi"}
    )
    assert resp.status_code == 200
    repo_id = resp.json()["id"]

    # Mock GitHub issues fetch
    mock_issues = [
        {
            "number": 1,
            "title": "Add basic unit test suite",
            "body": "Add pytest unit tests for helper modules.",
            "labels": [{"name": "good first issue"}]
        }
    ]
    mocker.patch(
        "app.services.issue_analyzer_service.IssueAnalyzerService.fetch_github_open_issues",
        return_value=mock_issues
    )

    # 2. Sync issues
    sync_resp = await async_client.post(f"/api/v1/repos/{repo_id}/issues/sync")
    assert sync_resp.status_code == 200
    issues = sync_resp.json()
    assert len(issues) >= 1
    assert issues[0]["issue_number"] == 1
    assert issues[0]["difficulty_level"] == "beginner"

    # 3. GET issues with filter
    list_resp = await async_client.get(f"/api/v1/repos/{repo_id}/issues?difficulty=beginner")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    # 4. GET single issue detail
    detail_resp = await async_client.get(f"/api/v1/repos/{repo_id}/issues/1")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["title"] == "Add basic unit test suite"
