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

    title: Mapped[str] = mapped_column(
        String(255),
        default="新会话",
        nullable=False,
        comment="会话标题",
    )