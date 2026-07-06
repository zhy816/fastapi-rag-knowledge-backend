from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin

# 这个文件对应阶段 1 草案里的 app/models/user.py，目标就是定义 users 表。
class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="用户 ID",
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="用户名",
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码哈希",
    )