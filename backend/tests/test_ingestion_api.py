import pytest
from httpx import AsyncClient
from pathlib import Path


@pytest.mark.asyncio
async def test_ingest_and_query_files(async_client: AsyncClient, mocker, tmp_path):
    # 1. Create dummy repository via analyze mock
    mock_meta = {
        "github_url": "https://github.com/sample/testrepo",
        "owner": "sample",
        "name": "testrepo",
        "description": "Test repository",
        "stars": 10,
        "forks": 2,
        "open_issues": 1,
        "default_branch": "main",
        "primary_language": "Python",
        "languages": {"Python": 100},
        "topics": []
    }

    mocker.patch(
        "app.services.github_service.GitHubService.fetch_repository_metadata",
        return_value=mock_meta
    )

    resp = await async_client.post(
        "/api/v1/repos/analyze",
        json={"github_url": "https://github.com/sample/testrepo"}
    )
    assert resp.status_code == 200
    repo_data = resp.json()
    repo_id = repo_data["id"]

    # Mock CloneService to point to tmp_path dummy repo
    dummy_repo_dir = tmp_path / "dummy_cloned_repo"
    dummy_repo_dir.mkdir()
    (dummy_repo_dir / "app.py").write_text("def hello():\n    print('world')\n")
    (dummy_repo_dir / "README.md").write_text("# Test Repo\nSample documentation\n")

    mocker.patch(
        "app.services.clone_service.CloneService.clone_repository",
        return_value=dummy_repo_dir
    )
    mocker.patch(
        "app.services.clone_service.CloneService.get_repo_dir",
        return_value=dummy_repo_dir
    )

    # 2. Trigger Ingest
    ingest_resp = await async_client.post(f"/api/v1/repos/{repo_id}/ingest")
    assert ingest_resp.status_code == 200
    ingest_data = ingest_resp.json()
    assert ingest_data["files_indexed"] == 2
    assert ingest_data["chunks_created"] >= 2

    # 3. GET files list
    files_resp = await async_client.get(f"/api/v1/repos/{repo_id}/files")
    assert files_resp.status_code == 200
    files = files_resp.json()
    assert len(files) == 2
    file_paths = [f["file_path"] for f in files]
    assert "app.py" in file_paths
    assert "README.md" in file_paths

    # 4. GET file content safely
    content_resp = await async_client.get(f"/api/v1/repos/{repo_id}/files/content?path=app.py")
    assert content_resp.status_code == 200
    content_data = content_resp.json()
    assert "def hello():" in content_data["content"]

    # 5. Path traversal security test on endpoint
    traversal_resp = await async_client.get(f"/api/v1/repos/{repo_id}/files/content?path=../../etc/passwd")
    assert traversal_resp.status_code == 403
