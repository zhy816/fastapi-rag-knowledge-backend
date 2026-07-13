from pathlib import Path

import chromadb


CHROMA_DB_PATH = Path("chroma_db")
# 指定 ChromaDB 数据的保存位置。以后运行程序，项目根目录会出现：
# chroma_db/
COLLECTION_NAME = "document_chunks"

# chroma_db/ 文件夹
#     → 真正保存向量数据的地方
#
# VectorStore 类
#     → 我们自己封装的“向量数据库操作工具”
#
# vector_store 变量
#     → 根据 VectorStore 类创建出来的具体对象
class VectorStore:
    # 这个类是开始创建 ChromaDB 服务
    def __init__(self):
        # 向量会持久化保存在这个文件夹中。关闭程序、重启电脑后数据不会消失。
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_PATH)
        )

        # Collection 可以暂时理解成 ChromaDB 里的“表
        # 这里就是创建一个明文 COLLECTION_NAME的表
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

    # 给这个数据库添加保存文本的方法
    def add_chunks(
        self,
        document_id: int,
        chunk_ids: list[int],
        texts: list[str],
        embeddings: list[list[float]],
    ) -> None:
        # 因为这几个元素要一一对应去存储到数据库里面， 所以我们在最前面加一个校验
        if not (
            len(chunk_ids) == len(texts) == len(embeddings)
        ):
            raise ValueError(
                "chunk_ids, texts and embeddings must have the same length"
            )

        # document_id：这些chunks属于MySQL里的哪一份文档；
        # chunk_ids：每个文本块在MySQL document_chunks表里的ID；
        # texts：每个文本块的原文；
        # embeddings：每个文本块对应的512维向量。


        # ChromaDB 要求每条记录都有一个字符串 ID，所以我们把 MySQL 的整数 chunk_id 转换成这种形式
        ids = [f"chunk_{chunk_id}" for chunk_id in chunk_ids]
        # 创建一个列表， 里面保存 字符串 chunk_（索引），索引是每个文本块在文章中的位置（就是在document_chunks里面的id）
        # 这个地方的id 是 ChromaDB 自己用于唯一识别记录的 ID，类似主键

        # 这里的document_id 就是我们传进来的那个文件的id
        # 这个metadata 会返回当前加进来的chunks的id 和 他的归属文件的id
        metadatas = [
            {
                "document_id": document_id,
                "chunk_id": chunk_id,
            }
            for chunk_id in chunk_ids
        ]

        # upsert 可以理解为：
        # ID 不存在 → 新增
        # ID 已存在 → 更新
        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )


    def search(
        self,
        query_embedding: list[float],
        document_id: int,
        top_k: int = 5,
    ) -> dict:
        results = self.collection.query(
            # 为什么不是 query_embeddings = query_embeddings
            # 因为 ChromaDB 支持一次查询多个问题向量，所以它要求的结构是：
            # [
            #     [第一个问题的512维向量],
            #     [第二个问题的512维向量]
            # ]
            query_embeddings=[query_embedding], # 用户问的那个问题 经过 embeddings之后生成的向量
            n_results=top_k, # 默认返回最相似的 5 个文本块
            where={"document_id": document_id}, #限定只搜索某一份文档。
        )

        return results

    # 他的作用是：
    # 找到 metadata 中 document_id 等于指定值的记录
    # 把这份文档的所有旧向量删除
    def delete_document(self, document_id: int) -> None:
        self.collection.delete(
            where={"document_id": document_id}
        )
vector_store = VectorStore()