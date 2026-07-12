from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

# 这个表的作用是：保存文档切分后的每一小段文本。
# 比如你上传了一个 PDF，解析后切成 20 段，那么 document_chunks 表里就会插入 20 行


"""
这张表是干嘛的？

它用来保存文档切分后的每一段文本。

比如一个文档解析后切成 3 段，那么数据库里会有：

document_id | chunk_index | content
1           | 0           | 第一段内容
1           | 1           | 第二段内容
1           | 2           | 第三段内容

"""
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunk_index",
        #     这个规则的意义是：保证一个文档里的 chunk 顺序不会乱。
        ),
    )
    # 在 document_chunks 表里，同一个 document_id 下面，chunk_index 不能重复。

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="chunk ID",
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
        comment="document ID",
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="chunk order in the document",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="chunk text content",
    )

    char_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="character count of this chunk",
    )

    create_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="create time",
    )