from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.chat import (
    ChatAskRequest,
    ChatAskResult,
    ChatMessageRead,
    ChatSessionCreate,
    ChatSessionRead,
)
from app.services.chat_service import chat_service
from app.services.rag_service import rag_service

router = APIRouter(
    tags=["chat"],
)


@router.post(
    "/chat/sessions",
    response_model=ChatSessionRead,
)
async def create_chat_session(
    request: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    user_stmt = select(User).where(
        User.id == request.user_id
    )
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    document_stmt = select(Document).where(
        Document.id == request.document_id
    )
    document_result = await db.execute(document_stmt)
    document = document_result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if document.user_id != request.user_id:
        raise HTTPException(
            status_code=403,
            detail="Document does not belong to this user",
        )

    title = request.title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty",
        )

    chat_session = await chat_service.create_session(
        db=db,
        user_id=request.user_id,
        document_id=request.document_id,
        title=title,
    )

    return chat_session

@router.post(
    "/chat/ask",
    response_model=ChatAskResult,
)
async def ask_in_chat(
    request: ChatAskRequest,
    db: AsyncSession = Depends(get_db),
):
    chat_session = await chat_service.get_session(
        db=db,
        session_id=request.session_id,
    )

    if chat_session is None:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found",
        )

    if chat_session.user_id != request.user_id:
        raise HTTPException(
            status_code=403,
            detail="Chat session does not belong to this user",
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    await chat_service.save_message(
        db=db,
        session_id=chat_session.id,
        role="user",
        content=question,
    )

    answer, sources = await rag_service.answer_question(
        document_id=chat_session.document_id,
        question=question,
        top_k=request.top_k,
    )

    await chat_service.save_message(
        db=db,
        session_id=chat_session.id,
        role="assistant",
        content=answer,
    )

    return ChatAskResult(
        session_id=chat_session.id,
        question=question,
        answer=answer,
        sources=sources,
    )

@router.get(
    "/users/{user_id}/chat-sessions",
    response_model=list[ChatSessionRead],
)
# 会先检查用户是否存在，然后返回该用户全部会话。按照我们在 ChatService 中写的排序，最新会话排在最前面。
async def get_user_chat_sessions(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    user_stmt = select(User).where(
        User.id == user_id
    )
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    chat_sessions = await chat_service.get_user_sessions(
        db=db,
        user_id=user_id,
    )

    return chat_sessions


@router.get(
    "/chat/sessions/{session_id}/messages",
    response_model=list[ChatMessageRead],
)
# 会先检查会话是否存在，然后按时间正序返回历史消息。
async def get_chat_session_messages(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    chat_session = await chat_service.get_session(
        db=db,
        session_id=session_id,
    )

    if chat_session is None:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found",
        )

    messages = await chat_service.get_session_messages(
        db=db,
        session_id=session_id,
    )

    return messages