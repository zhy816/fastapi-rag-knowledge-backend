from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentRead

from app.models.document_chunk import DocumentChunk
from app.schemas.document_chunk import (
    DocumentChunkRead,
    DocumentParseResult,
    DocumentVectorizeResult,
    DocumentSearchRequest,
    DocumentSearchItem,
    DocumentSearchResult,
    DocumentAskRequest,
    DocumentAskResult,
)
from app.services.document_parser import DocumentParseError, parse_document_file
from app.services.text_splitter import split_text
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.services.rag_service import rag_service

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
    file: UploadFile = File(...), # 从表单里取上传文件。 这个就是表单里上传文件的功能
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

    # 但如果以后项目部署到服务器上，那就变成：
    # 用户电脑里的文件
    # 上传到服务器上的 FastAPI 程序
    # 服务器把文件保存到服务器的uploads / 目录
    #
    # 也就是现在本地开发时，“用户电脑”和“服务器”刚好是同一台电脑，
    # 所以你感觉像是在本地文件夹之间搬了一份。实际上逻辑是客户端上传文件给后端，后端保存一份

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

# 遍历所有切好的 chunks。
#
# 每拿到一段文本：
# 1. 给它一个编号 index
# 2. 创建一条 document_chunks 表记录
# 3. 记录它属于哪个文档
# 4. 记录它是第几段
# 5. 记录它的文本内容
# 6. 记录它有多少字符
# 7. 把它加入数据库待保存队列
@router.post("/{document_id}/parse", response_model=DocumentParseResult)
async def parse_document(
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

    document.status = "processing"
    await db.commit()

    try:
        # 这里就调用了你刚才写的 services/document_parser.py。
        text = parse_document_file(
            file_path=document.file_path,
            file_type=document.file_type,
        )

        # 4. 切 chunks
        chunks = split_text(text)

        if not chunks:
            document.status = "failed"
            await db.commit()
            raise HTTPException(
                status_code=400,
                detail="No text content extracted from document",
            )

        # 重新解析文档时，删除 ChromaDB 中原来的旧向量
        # 因为重新切块后，旧向量已经不再对应最新的 chunks
        vector_store.delete_document(document_id)
        
        # 如果这个文档之前解析过，先删除旧 chunks，避免重复插入
        # 这个非常重要。
        # 因为你可能对同一个文档点两次 parse。
        # 如果不删旧 chunks，第二次插入时就会触发我们之前写的联合唯一约束：
        delete_stmt = delete(DocumentChunk).where(
            DocumentChunk.document_id == document_id
        )
        await db.execute(delete_stmt)

        for index, chunk in enumerate(chunks):
            # 所以这句：
            # for index, chunk in enumerate(chunks):
            # 意思是：
            # 每次从 chunks 里面拿出一段文本 chunk，
            # 同时给它一个顺序编号 index。
            db_chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=index,
                content=chunk,
                char_count=len(chunk),
            )
            # 这里是在创建一个 ORM 对象。
            # 你可以理解成：准备往 document_chunks 表里插入一行数据。
            db.add(db_chunk)

        document.status = "completed"
        await db.commit()

        return DocumentParseResult(
            document_id=document.id,
            status=document.status,
            chunk_count=len(chunks),
        )

    except HTTPException:
        raise

    except DocumentParseError as e:
        document.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        document.status = "failed"
        await db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while parsing document: {e}",
        )


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkRead])
async def list_document_chunks(
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

    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    )
    result = await db.execute(stmt)
    chunks = result.scalars().all()

    return chunks

@router.post(
    "/{document_id}/vectorize",
    response_model=DocumentVectorizeResult,
)
async def vectorize_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
):
    # 1. 查询文档是否存在
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # 2. 查询这份文档的所有 chunks
    stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    )

    result = await db.execute(stmt)
    chunks = result.scalars().all()
    # 这里是查询该文档的全部 chunks，并按照文章中的先后顺序排列。因为一篇文档对应多个 chunk，所以使用：
    # result.scalars().all()

    # 3. 如果还没有解析出 chunks，就不能向量化
    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Document has no chunks. Parse it first.",
        )

    try:
        # 4. 从 ORM 对象中分别取出 chunk ID 和文本
        chunk_ids = [chunk.id for chunk in chunks]
        texts = [chunk.content for chunk in chunks]

        # 5. 批量生成向量
        embeddings = embedding_service.embed_texts(texts)

        # 6. 删除这份文档以前保存的旧向量
        vector_store.delete_document(document_id)

        # 7. 把新向量保存到 ChromaDB
        vector_store.add_chunks(
            document_id=document_id,
            chunk_ids=chunk_ids,
            texts=texts,
            embeddings=embeddings,
        )

        # 8. 返回结果
        return DocumentVectorizeResult(
            document_id=document_id,
            status="vectorized",
            vector_count=len(chunks),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while vectorizing document: {e}",
        )

@router.post(
    "/{document_id}/search",
    response_model=DocumentSearchResult,
)
async def search_document(
    document_id: int,
    request: DocumentSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    # 1. 检查文档是否存在
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # 2. 检查用户的问题是否为空
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty",
        )

    try:
        # 3. 把用户的问题转换成向量
        # 它把用户问题转换成一个 512 维向量。
        query_embedding = embedding_service.embed_text(
            request.query
        )

        # 4. 在 ChromaDB 中搜索相似 chunks
        search_results = vector_store.search(
            query_embedding=query_embedding,
            document_id=document_id,
            top_k=request.top_k,
        )

        # 5. 取出 ChromaDB 返回的第一组搜索结果
        # 最外层代表“第几个问题”。我们一次只搜索一个问题，所以使用：search_results["documents"][0]
        # 拿到第一个问题对应的全部结果。
        documents = search_results["documents"][0]
        metadatas = search_results["metadatas"][0]
        distances = search_results["distances"][0]

        # 6. 整理成接口需要返回的格式
        items = []

        for content, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            item = DocumentSearchItem(
                chunk_id=metadata["chunk_id"],
                content=content,
                distance=distance,
            )
            items.append(item)

        # 7. 返回最终搜索结果
        return DocumentSearchResult(
            document_id=document_id,
            query=request.query,
            results=items,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while searching document: {e}",
        )
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

@router.post(
    "/{document_id}/ask",
    response_model=DocumentAskResult,
)
async def ask_document(
    document_id: int,
    request: DocumentAskRequest,
    db: AsyncSession = Depends(get_db),
):
    # 1. 检查文档是否存在
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # 2. 检查用户问题是否为空
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    try:
        # 3. 执行完整的 RAG 问答流程
        answer, sources = await rag_service.answer_question(
            document_id=document_id,
            question=request.question,
            top_k=request.top_k,
        )

        # 4. 整理并返回接口响应
        return DocumentAskResult(
            document_id=document_id,
            question=request.question,
            answer=answer,
            sources=sources,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while answering question: {e}",
        )