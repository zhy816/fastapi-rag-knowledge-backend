from datetime import datetime

from pydantic import BaseModel, ConfigDict

# DocumentRead 是返回格式。比如上传成功后，接口返回：
# from_attributes=True 还是那个意思：允许 Pydantic 从 SQLAlchemy ORM 对象里面读属性。
class DocumentRead(BaseModel):
    id: int
    user_id: int
    filename: str
    file_path: str
    file_type: str
    status: str
    create_time: datetime
    update_time: datetime

    model_config = ConfigDict(from_attributes=True)