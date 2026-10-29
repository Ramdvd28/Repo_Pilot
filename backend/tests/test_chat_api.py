import pytest
from httpx import AsyncClient
from sqlalchemy.future import select
from app.models.repository import Repository
from app.models.schema_models import ChatSession


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


@pytest.mark.asyncio
async def test_chat_repository_creation_and_full_retrieval_flow(async_client: AsyncClient, mocker):
    """
    Tests full flow: repository creation -> multiple chat turns with session continuation -> session & message retrieval.
    """
    mock_meta = {
        "github_url": "https://github.com/test/multiturn",
        "owner": "test",
        "name": "multiturn",
        "description": "Multi-turn chat test",
        "stars": 10,
        "forks": 2,
        "open_issues": 1,
        "default_branch": "main",
        "primary_language": "TypeScript",
        "languages": {"TypeScript": 100},
        "topics": []
    }

    mocker.patch(
        "app.services.github_service.GitHubService.fetch_repository_metadata",
        return_value=mock_meta
    )

    # 1. Ingest / create repository
    create_resp = await async_client.post(
        "/api/v1/repos/analyze",
        json={"github_url": "https://github.com/test/multiturn"}
    )
    assert create_resp.status_code == 200
    repo_id = create_resp.json()["id"]
    assert repo_id is not None

    # 2. First chat question
    msg1_resp = await async_client.post(
        f"/api/v1/repos/{repo_id}/chat",
        json={"question": "What is the entry point?"}
    )
    assert msg1_resp.status_code == 200
    msg1_data = msg1_resp.json()
    session_id = msg1_data["session_id"]
    assert session_id is not None
    assert msg1_data["role"] == "assistant"

    # 3. Follow-up question continuing the existing chat session
    msg2_resp = await async_client.post(
        f"/api/v1/repos/{repo_id}/chat",
        json={
            "question": "How are routes registered?",
            "session_id": session_id
        }
    )
    assert msg2_resp.status_code == 200
    msg2_data = msg2_resp.json()
    assert msg2_data["session_id"] == session_id

    # 4. Retrieve chat sessions for this repository
    sessions_resp = await async_client.get(f"/api/v1/repos/{repo_id}/chat/sessions")
    assert sessions_resp.status_code == 200
    sessions = sessions_resp.json()
    assert len(sessions) == 1
    assert sessions[0]["id"] == session_id
    assert sessions[0]["repository_id"] == repo_id

    # 5. Retrieve all messages for the session
    messages_resp = await async_client.get(
        f"/api/v1/repos/{repo_id}/chat/messages?session_id={session_id}"
    )
    assert messages_resp.status_code == 200
    messages = messages_resp.json()
    assert len(messages) == 4  # 2 user questions + 2 assistant responses
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "What is the entry point?"
    assert messages[1]["role"] == "assistant"
    assert messages[2]["role"] == "user"
    assert messages[2]["content"] == "How are routes registered?"
    assert messages[3]["role"] == "assistant"


@pytest.mark.asyncio
async def test_chat_with_missing_database_record(async_client: AsyncClient, db_session):
    """
    Verifies that querying chat for a valid UUID not in the database returns 404 Not Found
    and does NOT silently create a repository or fabricate data.
    """
    missing_id = "9ca3b3ea-5dcc-4980-8b17-8c0bbf705bf5"

    # Ensure repository does not exist in the database
    check_repo = await db_session.execute(select(Repository).where(Repository.id == missing_id))
    assert check_repo.scalars().first() is None

    # Chat endpoint should return 404
    chat_resp = await async_client.post(
        f"/api/v1/repos/{missing_id}/chat",
        json={"question": "Where is the main entry point?"}
    )
    assert chat_resp.status_code == 404
    assert chat_resp.json()["detail"] == f"Repository '{missing_id}' not found."

    # Sessions endpoint should return 404
    sessions_resp = await async_client.get(f"/api/v1/repos/{missing_id}/chat/sessions")
    assert sessions_resp.status_code == 404
    assert sessions_resp.json()["detail"] == f"Repository '{missing_id}' not found."

    # Messages endpoint should return 404
    messages_resp = await async_client.get(f"/api/v1/repos/{missing_id}/chat/messages?session_id=any-session")
    assert messages_resp.status_code == 404
    assert messages_resp.json()["detail"] == f"Repository '{missing_id}' not found."

    # Verify no repository record was silently created or fabricated
    check_repo_after = await db_session.execute(select(Repository).where(Repository.id == missing_id))
    assert check_repo_after.scalars().first() is None

    # Verify no chat session was created
    check_session = await db_session.execute(select(ChatSession).where(ChatSession.repository_id == missing_id))
    assert check_session.scalars().first() is None


@pytest.mark.asyncio
async def test_chat_with_invalid_repository_ids(async_client: AsyncClient):
    """
    Verifies that invalid or malformed repository IDs are rejected with 404
    and do not cause unhandled 500 errors or fabricate data.
    """
    invalid_ids = [
        "not-a-valid-uuid",
        "unknown-repo-slug-12345",
        "00000000-0000-0000-0000-000000000000",
        "11111111-2222-3333-4444-555555555555"
    ]

    for inv_id in invalid_ids:
        # Chat POST
        resp = await async_client.post(
            f"/api/v1/repos/{inv_id}/chat",
            json={"question": "Can you explain this repo?"}
        )
        assert resp.status_code == 404
        assert resp.json()["detail"] == f"Repository '{inv_id}' not found."

        # Sessions GET
        sess_resp = await async_client.get(f"/api/v1/repos/{inv_id}/chat/sessions")
        assert sess_resp.status_code == 404
        assert sess_resp.json()["detail"] == f"Repository '{inv_id}' not found."

        # Repo GET
        repo_resp = await async_client.get(f"/api/v1/repos/{inv_id}")
        assert repo_resp.status_code == 404
        assert repo_resp.json()["detail"] == f"Repository '{inv_id}' not found."
