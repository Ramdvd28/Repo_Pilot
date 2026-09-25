import pytest
from httpx import AsyncClient
from pathlib import Path


@pytest.mark.asyncio
async def test_security_api_endpoints(async_client: AsyncClient, mocker, tmp_path):
    mock_meta = {
        "github_url": "https://github.com/sample/secrepo",
        "owner": "sample",
        "name": "secrepo",
        "description": "Security test repository",
        "stars": 1,
        "forks": 0,
        "open_issues": 0,
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
        json={"github_url": "https://github.com/sample/secrepo"}
    )
    assert resp.status_code == 200
    repo_id = resp.json()["id"]

    # Mock CloneService to point to dummy repo directory with vulnerable code
    dummy_repo_dir = tmp_path / "dummy_sec_repo"
    dummy_repo_dir.mkdir()
    (dummy_repo_dir / "app.py").write_text("api_key = 'AKIA1234567890SECRETKEY'\n")

    mocker.patch(
        "app.services.clone_service.CloneService.clone_repository",
        return_value=dummy_repo_dir
    )
    mocker.patch(
        "app.services.clone_service.CloneService.get_repo_dir",
        return_value=dummy_repo_dir
    )

    # 1. Trigger security scan
    scan_resp = await async_client.post(f"/api/v1/repos/{repo_id}/security/scan")
    assert scan_resp.status_code == 200
    scan_data = scan_resp.json()
    assert "counts" in scan_data
    assert "findings" in scan_data

    # 2. GET security findings
    sec_resp = await async_client.get(f"/api/v1/repos/{repo_id}/security")
    assert sec_resp.status_code == 200
    sec_findings = sec_resp.json()
    assert len(sec_findings) >= 1

    # 3. GET quality findings
    qual_resp = await async_client.get(f"/api/v1/repos/{repo_id}/quality")
    assert qual_resp.status_code == 200
    qual_findings = qual_resp.json()
    assert len(qual_findings) >= 1
