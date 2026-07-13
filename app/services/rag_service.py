from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store


class RAGService:
    async def answer_question(
        self,
        document_id: int,
        question: str,
        top_k: int = 5,
    ) -> tuple[str, list[dict]]:
        # 表示这个函数一次返回两个值：return answer, sources
        # 第一个值是字符串：answer: str
        # 第二个值是一个由多个字典组成的列表：sources: list[dict]

        # 1. 把用户问题转换成向量
        query_embedding = embedding_service.embed_text(question)

        # 2. 从指定文档中检索相关 chunks
        search_results = vector_store.search(
            query_embedding=query_embedding,
            document_id=document_id,
            top_k=top_k,
        )

        documents = search_results["documents"][0]
        metadatas = search_results["metadatas"][0]
        distances = search_results["distances"][0]
        # 5. 为什么都要取 [0]
        # ChromaDB 支持一次查询多个问题，所以结果是二维列表：
        # [
        #     [第一个问题的全部结果],
        #     [第二个问题的全部结果],
        # ]
        # 我们每次只查询一个问题，因此只需要第一个问题的搜索结果：

        # 3. 没有检索结果时，不调用大模型
        if not documents:
            return "当前文档还没有可用于回答的向量数据。", []

        # 4. 把检索到的多个 chunks 拼接成参考资料
        context_parts = []

        for index, content in enumerate(documents, start=1):
            context_parts.append(
                f"[参考片段 {index}]\n{content}"
            )
        # 假设：
        # documents = [
        #     "ANN 会通过索引缩小搜索范围。",
        #     "暴力搜索需要逐个比较所有向量。",
        # ]
        # enumerate(documents, start=1) 会依次产生：
        #
        # 1, "ANN 会通过索引缩小搜索范围。"
        # 2, "暴力搜索需要逐个比较所有向量。"

        context = "\n\n".join(context_parts)
        # 使用两个换行符把多个片段连接起来：
        # [参考片段 1]
        # ANN 会通过索引缩小搜索范围。
        #
        # [参考片段 2]
        # 暴力搜索需要逐个比较所有向量。

        # 5. 把问题和参考资料交给大模型
        answer = await llm_service.generate_answer(
            question=question,
            context=context,
        )

        # 如果接口只返回答案：
        # 用户无法知道这个答案是根据哪些原文生成的。

        # 6. 整理引用来源
        sources = []

        for content, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            sources.append(
                {
                    "chunk_id": metadata["chunk_id"],
                    "content": content,
                    "distance": float(distance),
                }
            )

        return answer, sources
#     这里最后返回的是一个元组

#     (
#     "ANN 比暴力搜索更快，是因为……",
#     [
#         {
#             "chunk_id": 18,
#             "content": "ANN 会通过索引……",
#             "distance": 0.21,
#         }
#     ],
# )


rag_service = RAGService()