from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.document_chunk import DocumentSearchItem

# ChatSessionCreate 用来接收创建会话的请求
class ChatSessionCreate(BaseModel):
    user_id: int
    document_id: int
    title: str = Field(
        default="新会话",
        min_length=1,
        max_length=255, # 表示 title 可以不传。不传时自动使用“新会话”；传了就必须在 1～255 个字符之间。
    )

# ChatSessionRead 用来返回创建完成后的完整会话：
class ChatSessionRead(BaseModel):
    id: int
    user_id: int
    document_id: int
    title: str
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)

# 接收用户在某个会话中的提问：
class ChatAskRequest(BaseModel):
    user_id: int
    session_id: int
    question: str
    top_k: int = Field(default=5, ge=1, le=20)

# 返回阶段 6 的 RAG 结果：
class ChatAskResult(BaseModel):
    session_id: int
    question: str
    answer: str
    sources: list[DocumentSearchItem]

# 查询历史消息时，每条消息返回：
class ChatMessageRead(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)