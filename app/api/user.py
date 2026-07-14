from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRead,
)


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/register", response_model=UserRead)
async def register_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    # 1. 先检查用户名是否已经存在
    stmt = select(User).where(User.username == user_create.username)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail="Username already exists",
        )

    # 2. 对明文密码做 hash，不能直接存明文密码
    hashed_password = get_password_hash(user_create.password)

    # 3. 创建 User ORM 对象
    db_user = User(
        username=user_create.username,
        password_hash=hashed_password,
    )

    # 4. 添加到数据库 session
    db.add(db_user)

    # 5. 提交事务，真正写入数据库
    await db.commit()

    # 6. 刷新对象，拿到数据库生成的 id、create_time 等字段
    await db.refresh(db_user)

    # 7. 返回用户信息
    return db_user

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_login: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    # 1. 根据用户名查询用户
    stmt = select(User).where(User.username == user_login.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # 2. 用户不存在或密码不正确，都返回相同错误
    if user is None or not verify_password(
        user_login.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 密码正确，根据用户 ID 生成 JWT
    access_token = create_access_token(user.id)

    # 4. 返回 Token 和用户基本信息
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )

@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
