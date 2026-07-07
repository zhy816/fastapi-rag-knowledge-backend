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

## 当前进度

### 阶段 0：项目初始化 ✅

已完成：

- 初始化 FastAPI 项目结构
- 创建并配置虚拟环境
- 安装基础依赖
- 配置 `.gitignore`
- 创建 `.env.example`
- 创建基础 README
- 推送到 GitHub

### 阶段 1：数据库连接与核心数据表 ✅

已完成：

- 使用 `pydantic-settings` 读取 `.env` 配置
- 使用 SQLAlchemy Async 创建 MySQL 异步连接
- 定义 ORM Base 和公共时间字段
- 创建 4 张核心数据表模型：
  - `users`
  - `documents`
  - `chat_sessions`
  - `chat_messages`
- 使用 FastAPI lifespan 在项目启动时自动建表
- MySQL 中已成功生成 4 张核心表
- 项目关闭时释放数据库连接池

### 阶段 2：用户模块 ✅

已完成：

- 实现用户注册接口：`POST /users/register`
- 实现用户列表查询接口：`GET /users/`
- 实现根据 ID 查询用户接口：`GET /users/{user_id}`
- 使用 Argon2 对用户密码进行哈希处理
- 数据库中不保存明文密码
- 重复用户名会返回 `400`
- 查询不存在的用户会返回 `404`
- 接口返回结果不会暴露 `password` 或 `password_hash`

## 当前计划

- [x] 初始化项目结构
- [x] 配置数据库连接
- [x] 设计基础数据表
- [x] 实现用户模块
- [ ] 实现文档上传模块
- [ ] 实现文档解析与切分
- [ ] 接入向量数据库
- [ ] 实现 RAG 问答
- [ ] 保存聊天历史