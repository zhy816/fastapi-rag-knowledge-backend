from app.services.embedding_service import EmbeddingService


embedding_service = EmbeddingService()
# 创建服务对象。执行这一行时，会加载模型。第一次运行时还会自动下载模型，所以可能需要等待一会儿。

text = "FastAPI 是一个用于构建 API 的 Python 框架。"
embedding = embedding_service.embed_text(text) #把测试文本转换成向量。

print("原始文本：", text)
print("向量维度：", len(embedding))
print("向量前 10 个数字：", embedding[:10])