import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_repository_endpoint(async_client: AsyncClient, mocker):
    # Mock GitHub Service metadata call
    mock_meta = {
        "github_url": "https://github.com/fastapi/fastapi",
        "owner": "fastapi",
        "name": "fastapi",
        "description": "FastAPI framework",
        "stars": 75000,
        "forks": 6000,
        "open_issues": 120,
        "default_branch": "master",
        "primary_language": "Python",
        "languages": {"Python": 95.0, "HTML": 5.0},
        "topics": ["fastapi", "python"]
    }

    mocker.patch(
        "app.services.github_service.GitHubService.fetch_repository_metadata",
        return_value=mock_meta
    )

    response = await async_client.post(
        "/api/v1/repos/analyze",
        json={"github_url": "https://github.com/fastapi/fastapi"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["owner"] == "fastapi"
    assert data["name"] == "fastapi"
    assert data["stars"] == 75000
    assert "id" in data

    repo_id = data["id"]

    # Test GET /api/v1/repos/{repo_id}
    get_resp = await async_client.get(f"/api/v1/repos/{repo_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["id"] == repo_id
    assert get_data["name"] == "fastapi"

    # Test GET /api/v1/repos/
    list_resp = await async_client.get("/api/v1/repos/")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1


@pytest.mark.asyncio
async def test_analyze_repository_invalid_url(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/repos/analyze",
        json={"github_url": "not-a-valid-github-url"}
    )
    assert response.status_code == 422
