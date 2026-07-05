from fastapi import FastAPI


app = FastAPI(
    title="FastAPI RAG Knowledge Backend",
    description="基于 FastAPI 与 RAG 的智能知识库问答系统后端",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {
        "message": "FastAPI RAG Knowledge Backend is running"
    }