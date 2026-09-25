import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_with_repository_api(async_client: AsyncClient, mocker):
    # Mock GitHub Service metadata
    mock_meta = {
        "github_url": "https://github.com/test/chatrepo",
        "owner": "test",
        "name": "chatrepo",
        "description": "Chat test repository",
        "stars": 5,
        "forks": 1,
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

    # 1. Create repository
    resp = await async_client.post(
        "/api/v1/repos/analyze",
        json={"github_url": "https://github.com/test/chatrepo"}
    )
    assert resp.status_code == 200
    repo_id = resp.json()["id"]

    # 2. Ask question
    chat_resp = await async_client.post(
        f"/api/v1/repos/{repo_id}/chat",
        json={"question": "What does this project do?"}
    )
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert chat_data["role"] == "assistant"
    assert "content" in chat_data
    session_id = chat_data["session_id"]

    # 3. GET chat sessions
    sessions_resp = await async_client.get(f"/api/v1/repos/{repo_id}/chat/sessions")
    assert sessions_resp.status_code == 200
    sessions = sessions_resp.json()
    assert len(sessions) >= 1

    # 4. GET chat messages
    messages_resp = await async_client.get(
        f"/api/v1/repos/{repo_id}/chat/messages?session_id={session_id}"
    )
    assert messages_resp.status_code == 200
    messages = messages_resp.json()
    assert len(messages) == 2  # user + assistant
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
