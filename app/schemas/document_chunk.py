from datetime import datetime

from pydantic import BaseModel, ConfigDict

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