from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead


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

@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    # 1. 根据 user_id 查询用户
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # 2. 如果用户不存在，返回 404
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # 3. 如果用户存在，返回用户信息
    return user


@router.get("/", response_model=list[UserRead])
async def list_users(
    db: AsyncSession = Depends(get_db),
):
    # 1. 查询所有用户
    stmt = select(User)
    result = await db.execute(stmt)

    # 2. scalars() 取出 User 对象，all() 转成列表
    users = result.scalars().all()

    # 3. 返回用户列表
    return users