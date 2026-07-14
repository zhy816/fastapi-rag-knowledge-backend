from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession


class ChatService:
    async def create_session(
        self,
        db: AsyncSession,
        user_id: int,
        document_id: int,
        title: str,
    ) -> ChatSession:
        chat_session = ChatSession(
            user_id=user_id,
            document_id=document_id,
            title=title,
        )

        db.add(chat_session)
        await db.commit()
        await db.refresh(chat_session)

        return chat_session

    async def save_message(
        self,
        db: AsyncSession,
        session_id: int,
        role: str,
        content: str,
    ) -> ChatMessage:
        chat_message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
        )

        db.add(chat_message)
        await db.commit()
        await db.refresh(chat_message)

        return chat_message


    # get_session()：根据 session_id 查一条会话；不存在就返回 None
    # get_user_sessions()：查询一个用户的所有会话，最新创建的排在前面
    # get_session_messages()：查询一个会话里的全部消息，最早消息排在前面

    async def get_session(
        self,
        db: AsyncSession,
        session_id: int,
    ) -> ChatSession | None:
        stmt = select(ChatSession).where(
            ChatSession.id == session_id
        )
        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    async def get_user_sessions(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> list[ChatSession]:
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.create_time.desc())
        )
        result = await db.execute(stmt)

        return list(result.scalars().all())

    async def get_session_messages(
        self,
        db: AsyncSession,
        session_id: int,
    ) -> list[ChatMessage]:
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(
                ChatMessage.create_time.asc(),
                ChatMessage.id.asc(),
            )
        )
        result = await db.execute(stmt)

        return list(result.scalars().all())


chat_service = ChatService()