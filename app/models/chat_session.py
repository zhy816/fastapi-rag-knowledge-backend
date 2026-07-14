from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class ChatSession(Base, TimestampMixin):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="会话 ID",
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        comment="用户 ID",
    )
    # 表示 chat_sessions.document_id 必须对应 documents 表里真实存在的文档。
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        comment="关联文档 ID",
    )

    title: Mapped[str] = mapped_column(
        String(255),
        default="新会话",
        nullable=False,
        comment="会话标题",
    )