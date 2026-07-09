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

UPLOAD_DIR = Path("uploads")
ALLOWED_FILE_TYPES = {"pdf", "docx", "txt"}


@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
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

    saved_filename = f"{uuid4().hex}_{original_filename}"
    saved_path = UPLOAD_DIR / saved_filename

    file_content = await file.read()

    with open(saved_path, "wb") as f:
        f.write(file_content)

    db_document = Document(
        user_id=user_id,
        filename=original_filename,
        file_path=str(saved_path),
        file_type=file_type,
        status="uploaded",
    )

    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)

    return db_document


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