import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.schema_models import ChatSession, ChatMessage
from app.rag.rag_engine import RAGEngine
from app.services.repo_service import RepositoryService

router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, description="User question about the repository")
    session_id: Optional[str] = Field(None, description="Existing chat session ID if continuing conversation")
    provider: Optional[str] = Field("openai", description="AI provider to use ('openai' or 'gemini')")


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: Any


class ChatSessionResponse(BaseModel):
    id: str
    repository_id: str
    title: str
    created_at: Any


@router.post("/{repo_id}/chat", response_model=ChatMessageResponse)
async def chat_with_repository(
    repo_id: str,
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    RAG-powered repository chat:
    - Answers developer question grounded in repository code context.
    - Persists chat session and messages in database.
    - Returns answer with line-numbered file citations.
    """
    repo_service = RepositoryService(db)
    repo = await repo_service.get_by_id(repo_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repo_id}' not found."
        )

    # Get or create ChatSession
    session_id = payload.session_id
    if session_id:
        sess_result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        session = sess_result.scalars().first()
        if not session:
            session_id = None

    if not session_id:
        title = payload.question[:40] + "..." if len(payload.question) > 40 else payload.question
        session = ChatSession(
            id=str(uuid.uuid4()),
            repository_id=repo_id,
            title=title
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        session_id = session.id

    # 1. Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=payload.question,
        sources_json=[]
    )
    db.add(user_msg)

    # 2. Execute RAG Engine
    rag_engine = RAGEngine(db, provider_name=payload.provider or "openai")
    answer, sources = await rag_engine.answer_question(repository_id=repo_id, question=payload.question)

    # 3. Save assistant message
    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=answer,
        sources_json=sources
    )
    db.add(assistant_msg)
    await db.commit()
    await db.refresh(assistant_msg)

    return ChatMessageResponse(
        id=assistant_msg.id,
        session_id=session_id,
        role="assistant",
        content=assistant_msg.content,
        sources=sources,
        created_at=assistant_msg.created_at
    )


@router.get("/{repo_id}/chat/sessions", response_model=List[ChatSessionResponse])
async def list_chat_sessions(
    repo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Lists all chat sessions for a repository.
    """
    result = await db.execute(
        select(ChatSession).where(ChatSession.repository_id == repo_id).order_by(ChatSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return [
        ChatSessionResponse(
            id=s.id,
            repository_id=s.repository_id,
            title=s.title,
            created_at=s.created_at
        )
        for s in sessions
    ]


@router.get("/{repo_id}/chat/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    repo_id: str,
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves message history for a chat session.
    """
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc())
    )
    messages = result.scalars().all()
    return [
        ChatMessageResponse(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            content=m.content,
            sources=m.sources_json or [],
            created_at=m.created_at
        )
        for m in messages
    ]
