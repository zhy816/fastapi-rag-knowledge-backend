from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-small-zh-v1.5"
# BAAI：模型发布者，北京智源人工智能研究院。
# bge-small-zh-v1.5：模型名称。
# zh：主要面向中文。
# small：模型相对较小，适合本地运行。

class EmbeddingService:
    # 定义我们自己的 Embedding 服务类。以后其他代码不需要直接操作模型，只需要调用这个服务。
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def embed_text(self, text: str) -> list[float]:
        embedding = self.model.encode(text)
        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    # embed_texts(["第一块", "第二块", "第三块"])
    #     ↓
    # 每个文本块生成一个向量
    # list[list[float]]

embedding_service = EmbeddingService()