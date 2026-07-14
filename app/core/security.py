from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """
    把用户输入的明文密码转换成密码哈希。
    """
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证明文密码和数据库中保存的密码哈希是否匹配。
    """
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """
    根据用户 ID 创建 JWT access token。
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> int:
    """
    验证 JWT，并从中取出用户 ID。

    Token 无效、被篡改或已过期时，PyJWT 会抛出 InvalidTokenError。
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

    subject = payload.get("sub")

    if subject is None:
        raise InvalidTokenError("Token subject is missing")

    try:
        return int(subject)
    except (TypeError, ValueError) as exc:
        raise InvalidTokenError("Token subject is invalid") from exc