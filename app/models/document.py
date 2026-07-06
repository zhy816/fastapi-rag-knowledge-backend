from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="文档 ID",
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        comment="上传用户 ID",
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="原始文件名",
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="文件保存路径",
    )

    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="文件类型，例如 pdf、docx、txt",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="uploaded",
        nullable=False,
        comment="文档状态：uploaded/processing/completed/failed",
    )