from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# DocumentChunkRead：
# 查询 chunks 时返回每个 chunk 的格式。
#
# DocumentParseResult：
# 解析接口成功后返回一个简洁结果：
# 文档 ID、状态、生成了多少个 chunks。

class DocumentChunkRead(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    char_count: int
    create_time: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentParseResult(BaseModel):
    document_id: int
    status: str
    chunk_count: int

# document_id：刚刚向量化的是哪份文档；
# status：向量化结果；
# vector_count：一共生成并保存了多少条向量。
class DocumentVectorizeResult(BaseModel):
    document_id: int
    status: str
    vector_count: int

# 前端发给后端的数据：
class DocumentSearchRequest(BaseModel):
    query: str
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )
# 一条搜索结果的格式：
class DocumentSearchItem(BaseModel):
    chunk_id: int
    content: str
    distance: float

# 整个接口最终返回：
class DocumentSearchResult(BaseModel):
    document_id: int
    query: str
    results: list[DocumentSearchItem]

class DocumentAskRequest(BaseModel):
    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class DocumentAskResult(BaseModel):
    document_id: int
    question: str
    answer: str
    sources: list[DocumentSearchItem]