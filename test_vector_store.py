from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore


embedding_service = EmbeddingService()
vector_store = VectorStore()

document_id = -1
chunk_ids = [-101, -102, -103]

texts = [
    "FastAPI 是一个用于构建 Web API 的 Python 框架。",
    "ChromaDB 是一个可以存储和检索向量的向量数据库。",
    "今天天气很好，适合去公园散步。",
]

embeddings = embedding_service.embed_texts(texts)

try:
    vector_store.add_chunks(
        document_id=document_id,
        chunk_ids=chunk_ids,
        texts=texts,
        embeddings=embeddings,
    )

    question = "什么工具可以保存文本向量？"
    query_embedding = embedding_service.embed_text(question)

    results = vector_store.search(
        query_embedding=query_embedding,
        document_id=document_id,
        top_k=3,
    )

    print("问题：", question)
    print("检索到的文本：", results["documents"][0])
    print("距离：", results["distances"][0])
    print("关联信息：", results["metadatas"][0])

finally:
    vector_store.collection.delete(
        ids=[f"chunk_{chunk_id}" for chunk_id in chunk_ids]
    )