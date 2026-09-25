import pytest
from app.services.issue_analyzer_service import IssueAnalyzerService
from app.models.repository import Repository


@pytest.mark.asyncio
async def test_issue_analyzer_service_sync(db_session, mocker):
    # Seed dummy repo
    repo = Repository(
        id="test-repo-456",
        github_url="https://github.com/sample/issuerepo",
        owner="sample",
        name="issuerepo",
        description="Issue test repository",
        stars=10,
        forks=2
    )
    db_session.add(repo)
    await db_session.commit()

    # Mock fetch_github_open_issues
    mock_issues = [
        {
            "number": 101,
            "title": "Fix typo in documentation README",
            "body": "Fix small spelling mistake in section 2.",
            "labels": [{"name": "good first issue"}]
        },
        {
            "number": 102,
            "title": "Implement distributed rate limiting",
            "body": "Add Redis token bucket rate limiter for API endpoints.",
            "labels": [{"name": "architecture"}, {"name": "advanced"}]
        }
    ]

    service = IssueAnalyzerService(db_session)
    mocker.patch.object(service, "fetch_github_open_issues", return_value=mock_issues)

    records = await service.sync_and_analyze_issues("test-repo-456")
    assert len(records) == 2
    assert records[0].difficulty_level == "beginner"
    assert records[1].difficulty_level == "advanced"
