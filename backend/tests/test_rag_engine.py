import pytest
from app.rag.rag_engine import RAGEngine
from app.models.schema_models import CodeChunk


@pytest.mark.asyncio
async def test_rag_engine_answer_generation(db_session):
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

    rag = RAGEngine(db_session, provider_name="openai")
    answer, sources = await rag.answer_question(
        repository_id="test-repo-123",
        question="How does user authentication work?"
    )

    assert isinstance(answer, str)
    assert len(sources) >= 1
    assert sources[0]["file_path"] == "app/auth.py"
    assert sources[0]["symbol_name"] == "authenticate_user"
