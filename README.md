# FastAPI RAG Knowledge Backend

基于 FastAPI 与 RAG 的智能知识库问答系统后端。

## 项目目标

本项目用于实现一个支持文档上传、知识库检索和 AI 问答的后端系统。

用户可以上传学习资料或文档，系统会对文档进行解析、切分、向量化，并在用户提问时检索相关内容，再结合大模型生成回答。

## 技术栈

- FastAPI
- SQLAlchemy Async
- MySQL
- Pydantic
- Chroma / Milvus
- RAG
- LLM API

## 当前计划

- [x] 初始化项目结构
- [ ] 配置数据库连接
- [ ] 设计基础数据表
- [ ] 实现用户模块
- [ ] 实现文档上传模块
- [ ] 实现文档解析与切分
- [ ] 接入向量数据库
- [ ] 实现 RAG 问答
- [ ] 保存聊天历史