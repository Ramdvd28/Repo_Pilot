import pytest
from httpx import AsyncClient
from app.analyzers.architecture_analyzer import ArchitectureAnalyzer


def test_architecture_analyzer_extracts_graph(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    (repo_dir / "backend").mkdir()
    (repo_dir / "backend" / "main.py").write_text("from fastapi import FastAPI\n")
    (repo_dir / "frontend").mkdir()
    (repo_dir / "frontend" / "page.tsx").write_text("export default function Page() {}\n")

    analyzer = ArchitectureAnalyzer()
    res = analyzer.analyze_repository(repo_dir, "test-repo")

    assert res["repository_name"] == "test-repo"
    assert res["total_nodes"] >= 4
    assert res["total_edges"] >= 3

    node_ids = [n["id"] for n in res["nodes"]]
    assert "node-entry" in node_ids
    assert "node-backend" in node_ids
    assert "node-frontend" in node_ids


@pytest.mark.asyncio
async def test_architecture_api_endpoints(async_client: AsyncClient, mocker, tmp_path):
    mock_meta = {
        "github_url": "https://github.com/sample/archrepo",
        "owner": "sample",
        "name": "archrepo",
        "description": "Architecture test repository",
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
        json={"github_url": "https://github.com/sample/archrepo"}
    )
    assert resp.status_code == 200
    repo_id = resp.json()["id"]

    dummy_repo_dir = tmp_path / "dummy_arch"
    dummy_repo_dir.mkdir()
    (dummy_repo_dir / "main.py").write_text("print('hello')\n")

    mocker.patch("app.services.clone_service.CloneService.clone_repository", return_value=dummy_repo_dir)
    mocker.patch("app.services.clone_service.CloneService.get_repo_dir", return_value=dummy_repo_dir)

    arch_resp = await async_client.get(f"/api/v1/repos/{repo_id}/architecture")
    assert arch_resp.status_code == 200
    data = arch_resp.json()
    assert "nodes" in data
    assert "edges" in data
