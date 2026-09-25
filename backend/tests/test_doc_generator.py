import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_doc_generator_api_endpoints(async_client: AsyncClient, mocker, tmp_path):
    mock_meta = {
        "github_url": "https://github.com/sample/docrepo",
        "owner": "sample",
        "name": "docrepo",
        "description": "Doc generation test repository",
        "stars": 5,
        "forks": 1,
        "open_issues": 0,
        "default_branch": "main",
        "primary_language": "TypeScript",
        "languages": {"TypeScript": 100},
        "topics": []
    }

    mocker.patch(
        "app.services.github_service.GitHubService.fetch_repository_metadata",
        return_value=mock_meta
    )

    resp = await async_client.post(
        "/api/v1/repos/analyze",
        json={"github_url": "https://github.com/sample/docrepo"}
    )
    assert resp.status_code == 200
    repo_id = resp.json()["id"]

    dummy_repo_dir = tmp_path / "dummy_doc"
    dummy_repo_dir.mkdir()
    (dummy_repo_dir / "index.ts").write_text("console.log('test')\n")

    mocker.patch("app.services.clone_service.CloneService.clone_repository", return_value=dummy_repo_dir)
    mocker.patch("app.services.clone_service.CloneService.get_repo_dir", return_value=dummy_repo_dir)

    docs_resp = await async_client.post(f"/api/v1/repos/{repo_id}/docs/generate")
    assert docs_resp.status_code == 200
    data = docs_resp.json()
    assert "documentation" in data
    assert len(data["documentation"]) > 10
    assert "sections" in data
