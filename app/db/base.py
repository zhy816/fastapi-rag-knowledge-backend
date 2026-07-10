# 因为 SQLAlchemy 不会自动扫描 models 文件夹。
# 只有被导入过的模型，才会登记到：Base.metadata

from app.models.base import Base
from app.models.user import User
from app.models.document import Document
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.document_chunk import DocumentChunk