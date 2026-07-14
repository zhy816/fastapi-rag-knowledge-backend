from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

from app.models.document import Document


bearer_scheme = HTTPBearer(auto_error=False)
# HTTPBearer 是一个 FastAPI 安全工具，负责检查请求头有没有：Authorization: Bearer <token>
# 这里设置： auto_error=False
# 表示：如果请求里没有 Token，先不要自动抛出异常，而是返回 None，让我们自己决定错误响应

# 前端请求接口
# → 请求头携带 JWT
# → get_current_user 验证 JWT
# → 找到数据库中的用户
# → 把 User 对象交给真正的接口

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User: #表示验证成功后，函数会返回一个 SQLAlchemy User 对象。
    # HTTPBearer：从请求头读取 Bearer Token。
    # HTTPAuthorizationCredentials：描述读取结果的数据类型。

    # 参数解释：
    # 表示 credentials 可能有两种情况：
    # 成功读取 Token：HTTPAuthorizationCredentials
    # 没有携带 Token：None
    """
    从 Authorization: Bearer <token> 中识别当前用户。
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}, # 这个接口使用 Bearer Token 认证。
    )
    # 这里先创建了一个统一的异常对象。
    # 401 的意思是：
    # 当前请求没有通过身份认证。
    # 下面这些情况都会抛出它：
    # 没带 Token
    # Token 格式错误
    # Token 已经过期
    # Token 签名错误
    # Token 中没有合法用户 ID
    # Token 对应的用户不存在

    # 请求没有携带 Bearer Token
    if credentials is None:
        raise credentials_exception

    try:
        user_id = decode_access_token(credentials.credentials)
    except InvalidTokenError:
        raise credentials_exception

    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Document:
    """
    查询指定文档，并确认它属于当前登录用户。
    """
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    if document.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Document does not belong to current user",
        )

    return document