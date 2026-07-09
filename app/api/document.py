from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentRead


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

UPLOAD_DIR = Path("uploads") # 上传的文件统一保存到项目根目录下的 uploads 文件夹里。
ALLOWED_FILE_TYPES = {"pdf", "docx", "txt"}
# Path("uploads") 会创建一个“路径对象”：
# 这个对象就知道自己是一个文件夹路径，所以可以直接做很多文件路径相关的操作。
# 比如创建文件夹：UPLOAD_DIR.mkdir(exist_ok=True)
# 意思是：
# 创建 uploads 文件夹。如果已经存在，就不要报错。
# 再比如拼接路径：
# saved_path = UPLOAD_DIR / saved_filename
# 这里的 / 不是数学除法，而是 Path 对象重载过的路径拼接。
@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    user_id: int = Form(...), # 前端要传一个 user_id，而且它来自表单数据
        # 这个 ... 表示：必填项。 这个Form表示 这个参数从表单字段里拿，而且必须传
        # 从表单里取普通文本。
    file: UploadFile = File(...), # 从表单里取上传文件。
    db: AsyncSession = Depends(get_db),
):
    # 第一，检查用户是否存在：
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    original_filename = Path(file.filename).name
    file_type = Path(original_filename).suffix.lower().lstrip(".")

    if file_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only pdf, docx and txt files are allowed",
        )

    UPLOAD_DIR.mkdir(exist_ok=True)
    # 如果 uploads 文件夹不存在，就创建它；如果已经存在，也不要报错。

    saved_filename = f"{uuid4().hex}_{original_filename}"
    # 保存上传文件的命名规则
    # 这里不采用原名的原因是， 如果是原名， 当出现同名文件的时候 会有覆盖的现象
    saved_path = UPLOAD_DIR / saved_filename

    #  下面就是读取上传的文件的内容，然后把这个文件保存到本地电脑上
    file_content = await file.read()

    with open(saved_path, "wb") as f:
        f.write(file_content)

    # 它是在创建一个 Python 对象，这个对象代表 documents 表里的一条新记录
    db_document = Document(
        user_id=user_id,
        filename=original_filename,
        file_path=str(saved_path),
        file_type=file_type,
        status="uploaded",
    )

    # 添加记录 添加到数据库
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)

    return db_document


# 这个就是返回数据库中保存的所有的曾经上传过的文件的记录
@router.get("/", response_model=list[DocumentRead])
async def list_documents(
    user_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Document)

    if user_id is not None:
        stmt = stmt.where(Document.user_id == user_id)

    result = await db.execute(stmt)
    documents = result.scalars().all()

    return documents


# 这个就是根据输入的文件的id 查找并返回具体的文件对象
@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document