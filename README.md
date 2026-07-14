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
- ChromaDB
- Sentence Transformers
- BAAI/bge-small-zh-v1.5
- RAG
- OpenAI Python SDK
- OpenAI Responses API
- GPT-5.4 mini
- pwdlib / Argon2
- PyJWT
- JWT Bearer Authentication
- React
- TypeScript
- Vite
- Axios

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

### 阶段 3：文档上传模块 ✅

已完成：

- 实现文档上传接口：`POST /documents/upload`
- 实现文档列表查询接口：`GET /documents/`
- 实现根据 ID 查询文档接口：`GET /documents/{document_id}`
- 支持上传 `pdf` / `docx` / `txt`
- 上传前检查 `user_id` 是否存在
- 文件保存到本地 `uploads/` 目录
- 数据库 `documents` 表保存文件记录
- 不支持的文件类型会返回 `400`
- 不存在的用户会返回 `404`

### 阶段 4：文档解析与文本切分 ✅

已完成：

- 新增 `document_chunks` 表，用于保存文档切分后的文本块
- 支持解析 `txt` / `docx` / `pdf` 文件
- 新增文本清洗工具，去除多余空行和空白字符
- 新增文本切分工具，支持 `chunk_size` 和 `chunk_overlap`
- 实现文档解析接口：`POST /documents/{document_id}/parse`
- 实现文档 chunks 查询接口：`GET /documents/{document_id}/chunks`
- 解析成功后将文档状态更新为 `completed`
- 解析失败时将文档状态更新为 `failed`
- 重复解析同一文档时会先删除旧 chunks，避免重复插入

### 阶段 5：文档向量化与语义检索 ✅

已完成：

- 使用 `BAAI/bge-small-zh-v1.5` 作为本地 Embedding 模型
- 新增 `EmbeddingService`，支持单条文本和批量文本向量化
- 接入 ChromaDB，并将向量数据持久化到本地 `chroma_db/` 目录
- 新增 `VectorStore`，封装向量新增、搜索和删除操作
- 实现文档向量化接口：`POST /documents/{document_id}/vectorize`
- 实现文档语义搜索接口：`POST /documents/{document_id}/search`
- ChromaDB 同时保存 chunk 原文、向量及 `document_id`、`chunk_id` 元数据
- 支持通过 `document_id` 将语义搜索限制在指定文档内
- 支持通过 `top_k` 控制返回的相关文本块数量
- 限制 `top_k` 的取值范围为 1 至 20
- 重复向量化时会先删除旧向量，避免数据重复
- 重新解析文档时会同步清理 ChromaDB 中的旧向量
- 已完成多 chunk 批量向量化和语义检索测试
- `chroma_db/` 已加入 `.gitignore`，本地向量数据不会提交到 Git

### 阶段 6：基于大模型的 RAG 问答 ✅

已完成：

- 接入 OpenAI Python SDK 和 Responses API
- 使用 `gpt-5.4-mini` 生成基于文档资料的自然语言答案
- 使用 `.env` 安全保存 OpenAI API Key
- 新增 `LLMService`，封装异步大模型调用
- 新增 `RAGService`，串联问题向量化、语义检索、上下文拼接和答案生成
- 实现文档问答接口：`POST /documents/{document_id}/ask`
- 支持通过 `top_k` 控制用于生成答案的相关文本块数量
- 返回大模型答案以及对应的 chunk 引用来源
- 参考资料不足时明确返回无法回答，减少模型编造
- 文档没有向量数据时直接返回提示，不调用大模型
- 阶段 5 与阶段 6 共用同一个 `EmbeddingService` 和 `VectorStore` 实例
- 已完成正常问答、无答案问题、空问题、非法 `top_k`、错误文档 ID 和未向量化文档测试

### 阶段 7：聊天会话与消息历史 ✅

已完成：

- 为 `chat_sessions` 表增加 `document_id` 外键，使聊天会话关联用户和文档
- 新增 `ChatService`，封装聊天会话与消息的写入和查询逻辑
- 实现创建聊天会话接口：`POST /chat/sessions`
- 支持自定义会话标题，未传标题时默认使用“新会话”
- 创建会话前检查用户、文档以及文档归属关系
- 实现会话问答接口：`POST /chat/ask`
- 用户提问时自动保存 `user` 消息
- 调用 `RAGService` 生成回答后自动保存 `assistant` 消息
- 会话通过 `document_id` 自动确定需要检索的文档
- 实现用户历史会话查询接口：`GET /users/{user_id}/chat-sessions`
- 实现会话历史消息查询接口：`GET /chat/sessions/{session_id}/messages`
- 历史会话按照创建时间倒序返回
- 历史消息按照创建时间正序返回
- 已完成正常创建、默认标题、RAG 问答、历史查询、错误用户、错误会话、会话归属和空问题测试

### 阶段 8A：JWT 登录鉴权与数据权限隔离 ✅

已完成：

- 使用 `PyJWT` 实现 JWT access token 的签发与验证
- 使用 `HS256` 对 Token 进行签名
- Token 使用 `sub` 保存用户 ID，并通过 `exp` 控制过期时间
- 将 JWT 密钥、签名算法和 Token 有效期保存到 `.env`
- 实现用户登录接口：`POST /users/login`
- 实现当前用户查询接口：`GET /users/me`
- 新增 `get_current_user` 依赖，统一解析 Bearer Token 并查询当前用户
- 登录失败时统一返回 `401 Incorrect username or password`
- 缺少、伪造或无效 Token 时返回 `401`
- 移除公开的用户列表和任意用户 ID 查询接口
- 文档上传不再接收前端传入的 `user_id`，自动使用当前登录用户
- 文档列表只返回当前用户拥有的文档
- 新增文档归属检查依赖，统一保护文档查询、解析、切分、向量化、检索和问答接口
- 创建聊天会话和会话问答不再接收前端传入的 `user_id`
- 用户历史会话接口调整为：`GET /chat/sessions`
- 会话历史消息和会话问答均校验会话归属
- 已完成正确登录、错误密码、无 Token、伪造 Token、文档越权和聊天会话越权测试

### 阶段 8B：React 前端与前后端联调 ✅

已完成：

- 使用 Vite 创建 React + TypeScript 前端项目
- 使用 Axios 封装后端请求客户端
- 使用 Axios 请求拦截器自动携带 JWT Bearer Token
- 登录成功后将 access token 保存到 localStorage
- 页面启动时通过 `GET /users/me` 恢复并验证登录状态
- 实现用户注册、登录和退出功能
- 为 FastAPI 配置 CORS，允许本地 React 前端访问
- 实现当前用户文档列表展示
- 实现 PDF、DOCX 和 TXT 文档上传
- 实现文档解析和向量化操作
- 实现聊天会话创建与历史会话切换
- 实现聊天历史消息展示
- 实现 RAG 问答和引用来源展示
- 完成登录、上传、解析、向量化、创建会话、问答和历史记录全流程联调
- 前端生产构建检查通过


## 当前计划

- [x] 初始化项目结构
- [x] 配置数据库连接
- [x] 设计基础数据表
- [x] 实现用户模块
- [x] 实现文档上传模块
- [x] 实现文档解析与切分
- [x] 接入 Embedding 模型
- [x] 接入 ChromaDB 向量数据库
- [x] 实现文档向量化
- [x] 实现语义检索
- [x] 接入大模型并实现 RAG 问答
- [x] 保存聊天历史
- [x] 实现 JWT 登录鉴权
- [x] 实现文档与聊天会话权限隔离
- [x] 实现前端页面
- [ ] 完善项目展示与运行说明