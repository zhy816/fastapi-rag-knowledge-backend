from openai import AsyncOpenAI

from app.core.config import settings

# 这个文件只做一件事：
# 接收 question 和 context
# → 组装给大模型的请求
# → 调用 OpenAI
# → 返回自然语言答案
MODEL_NAME = "gpt-5.4-mini"


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    #  这里采用 异步函数 因为response采用了 await
    async def generate_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        # self.client 就是已经配置好 API Key 的 OpenAI 客户端
        response = await self.client.responses.create(
            # 通过 OpenAI 的 Responses API，创建一次新的模型回答。
            # 等待这次 OpenAI 请求完成并取得结果；等待期间允许程序处理其他异步任务。
            model=MODEL_NAME,
            instructions=(
                "你是一个知识库问答助手。"
                "请严格根据提供的参考资料回答问题。"
                "如果参考资料中没有足够信息，请明确回答："
                "根据当前资料无法回答该问题。"
                "不要编造参考资料中不存在的信息。"
            ),
            input=(
                f"参考资料：\n{context}\n\n"
                f"用户问题：\n{question}"
            ),
        )

        return response.output_text


llm_service = LLMService()
# 表示程序启动时创建一个可复用的服务对象，以后其他文件可以直接导入当前包， 并直接调用