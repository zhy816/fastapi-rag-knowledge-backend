from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import Base
from app.db.session import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    
    # yield 下面：项目关闭时执行
    await async_engine.dispose()


app = FastAPI(
    title="FastAPI RAG Knowledge Backend",
    description="基于 FastAPI 与 RAG 的智能知识库问答系统后端",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {
        "message": "FastAPI RAG Knowledge Backend is running"
    }