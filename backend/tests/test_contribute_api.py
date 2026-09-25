import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_contribute_api_endpoints(async_client: AsyncClient, mocker):
    mock_meta = {
        "github_url": "https://github.com/sample/contribrepo",
        "owner": "sample",
        "name": "contribrepo",
        "description": "Contribution test repo",
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
        json={"github_url": "https://github.com/sample/contribrepo"}
    )
    assert resp.status_code == 200
    repo_id = resp.json()["id"]

    sample_diff = """diff --git a/app/main.py b/app/main.py
--- a/app/main.py
+++ b/app/main.py
@@ -1,2 +1,3 @@
 def main():
+    print("Hello world")
"""

    # 1. Test POST /review
    review_resp = await async_client.post(
        f"/api/v1/repos/{repo_id}/review",
        json={"git_diff": sample_diff}
    )
    assert review_resp.status_code == 200
    review_data = review_resp.json()
    assert "score" in review_data
    assert "findings" in review_data

    # 2. Test POST /generate-pr
    pr_resp = await async_client.post(
        f"/api/v1/repos/{repo_id}/generate-pr",
        json={
            "git_diff": sample_diff,
            "issue_number": 1,
            "test_results": "pytest 5 passed"
        }
    )
    assert pr_resp.status_code == 200
    pr_data = pr_resp.json()
    assert "title" in pr_data
    assert "markdown_description" in pr_data
