from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="消息 ID",
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey("chat_sessions.id"),
        nullable=False,
        comment="所属会话 ID",
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="消息角色：user/assistant/system",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="消息内容",
    )

    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="创建时间",
    )