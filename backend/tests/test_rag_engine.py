import pytest
from fastapi import HTTPException
from app.rag.rag_engine import RAGEngine
from app.ai.base import AIProviderError
from app.models.repository import Repository
from app.models.schema_models import CodeChunk


@pytest.mark.asyncio
async def test_rag_engine_answer_generation(db_session):
    # Seed repository record
    repo = Repository(
        id="test-repo-123",
        github_url="https://github.com/test/auth-repo",
        owner="test",
        name="auth-repo",
        default_branch="main",
        primary_language="Python"
    )
    db_session.add(repo)
    await db_session.commit()

    # Seed dummy code chunk
    chunk = CodeChunk(
        repository_id="test-repo-123",
        file_path="app/auth.py",
        language="Python",
        start_line=1,
        end_line=15,
        symbol_name="authenticate_user",
        content="def authenticate_user(username, password):\n    # JWT token verification\n    return token\n"
    )
    db_session.add(chunk)
    await db_session.commit()

    rag = RAGEngine(db_session)
    answer, sources = await rag.answer_question(
        repository_id="test-repo-123",
        question="How does user authentication work?"
    )

    assert isinstance(answer, str)
    assert len(sources) >= 1
    assert sources[0]["file_path"] == "app/auth.py"
    assert sources[0]["symbol_name"] == "authenticate_user"


@pytest.mark.asyncio
async def test_rag_engine_metadata_shortcut(db_session):
    repo = Repository(
        id="test-repo-shortcut",
        github_url="https://github.com/test/shortcut-repo",
        owner="test",
        name="shortcut-repo",
        default_branch="main",
        primary_language="TypeScript",
        stars=1250,
        forks=85
    )
    db_session.add(repo)
    await db_session.commit()

    rag = RAGEngine(db_session)

    # Primary language query
    lang_ans, sources = await rag.answer_question(
        repository_id="test-repo-shortcut",
        question="What is the primary language?"
    )
    assert "TypeScript" in lang_ans
    assert len(sources) == 0

    # Star count query
    stars_ans, _ = await rag.answer_question(
        repository_id="test-repo-shortcut",
        question="How many stars?"
    )
    assert "1,250" in stars_ans


@pytest.mark.asyncio
async def test_rag_engine_deduplication(db_session):
    repo = Repository(
        id="test-repo-dedup",
        github_url="https://github.com/test/dedup-repo",
        owner="test",
        name="dedup-repo",
        default_branch="main"
    )
    db_session.add(repo)
    await db_session.commit()

    # Add two identical chunks
    chunk1 = CodeChunk(
        repository_id="test-repo-dedup",
        file_path="app/core.py",
        language="Python",
        start_line=1,
        end_line=10,
        symbol_name="execute",
        content="def execute(): pass"
    )
    chunk2 = CodeChunk(
        repository_id="test-repo-dedup",
        file_path="app/core.py",
        language="Python",
        start_line=1,
        end_line=10,
        symbol_name="execute",
        content="def execute(): pass"
    )
    db_session.add_all([chunk1, chunk2])
    await db_session.commit()

    rag = RAGEngine(db_session)
    _, sources = await rag.answer_question(
        repository_id="test-repo-dedup",
        question="How does execute work?"
    )
    # Deduplication must reduce duplicates to 1 source
    assert len(sources) == 1


@pytest.mark.asyncio
async def test_rag_engine_provider_failure_returns_503(db_session, mocker):
    repo = Repository(
        id="test-repo-fail",
        github_url="https://github.com/test/fail-repo",
        owner="test",
        name="fail-repo",
        default_branch="main"
    )
    db_session.add(repo)
    await db_session.commit()

    rag = RAGEngine(db_session)
    mocker.patch.object(
        rag.ai_provider,
        "generate_text",
        side_effect=AIProviderError("All providers exhausted", provider="fallback")
    )

    with pytest.raises(HTTPException) as exc_info:
        await rag.answer_question(
            repository_id="test-repo-fail",
            question="Explain the architecture."
        )

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "AI service is temporarily unavailable. Please try again in a moment."
