# RAG 智能体助手 MVP

基于 RAG 技术的高性能企业级知识库问答系统。通过 LangGraph 实现智能工作流，支持多轮对话、知识库检索、联网搜索等功能。

## 功能特性

- 📚 **多知识库管理**: 支持创建、切换、删除多个独立知识库
- 📄 **多格式文档支持**: PDF、DOCX、MD、TXT
- 💬 **多轮对话**: 基于 LangGraph 的智能工作流，支持 SSE 流式响应
- 🔍 **检索增强**: Milvus 向量检索 + Rerank 重排序
- 🔗 **引用溯源**: 点击引用查看原文片段和来源
- 🌐 **联网搜索**: 集成 Tavily API，处理实时性问题
- 🧠 **查询优化**: 自动查询重写和自我反思机制
- 🤖 **模型可配置**: 支持 OpenAI、VLLM、Ollama

## 项目结构

```
cc_dev_project/
├── backend/           # FastAPI 后端
│   └── app/
│       ├── api/       # API 路由
│       ├── core/      # 核心配置
│       ├── models/    # 数据模型
│       ├── schemas/   # Pydantic schemas
│       ├── services/  # 业务逻辑
│       │   ├── llm/   # LLM 服务
│       │   └── rag/   # RAG 服务
│       ├── graph/     # LangGraph 工作流
│       └── main.py    # 应用入口
├── frontend/          # Vue 3 前端
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── stores/    # Pinia 状态管理
│       └── router/    # 路由配置
├── docker/            # Docker 配置
│   └── docker-compose.yml
├── .env               # 环境变量配置
└── README.md
```

## 快速开始

### 前置要求

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### 1. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 配置
# 主要配置项：
# - TAVILY_API_KEY: Tavily 搜索 API 密钥 (已预填开发密钥)
# - OPENAI_API_KEY: OpenAI API 密钥 (可选，用于 OpenAI LLM)
# - MILVUS_HOST/port: Milvus 连接配置
```

### 2. 启动 Milvus

```bash
cd docker
docker-compose up -d

# 等待 Milvus 启动 (首次运行约1-2分钟)
docker-compose ps
```

**Attu 管理界面**: http://localhost:13002 (或 http://您的服务器IP:13002)

### 3. 启动后端

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -e .

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档: http://localhost:8000/docs

### 4. 启动前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问: http://localhost:5173

## 使用指南

### 创建知识库

1. 点击导航栏的 "知识库"
2. 点击 "创建知识库" 按钮
3. 输入知识库名称和描述
4. 点击 "创建"

### 上传文档

1. 在知识库详情页，点击上传区域
2. 选择文件 (支持 PDF、DOCX、MD、TXT)
3. 等待文档解析、切分和向量化完成

### 开始对话

1. 返回对话页面
2. 点击知识库选择器，选择要使用的知识库
3. 输入问题并发送
4. 系统将：
   - 检索相关文档
   - 分析引用来源
   - 生成回答
   - 显示引用链接

### 查看引用

点击回答中的引用标记 (如 [0], [1]) 可查看原文片段。

## 技术栈

### 后端
- **框架**: FastAPI
- **LLM**: LangChain + LangGraph
- **向量数据库**: Milvus
- **对话数据库**: SQLite
- **搜索**: Tavily API

### 前端
- **框架**: Vue 3
- **样式**: Tailwind CSS
- **状态管理**: Pinia
- **HTTP**: Axios
- **流式响应**: SSE
- **Markdown 渲染**: Marked.js

## API 端点

### 对话 API
- `POST /api/v1/chat/stream` - 流式对话 (SSE)
- `POST /api/v1/chat/` - 非流式对话
- `GET /api/v1/chat/conversations` - 获取对话列表
- `GET /api/v1/chat/conversations/{id}` - 获取对话详情
- `POST /api/v1/chat/conversations` - 创建对话
- `DELETE /api/v1/chat/conversations/{id}` - 删除对话

### 知识库 API
- `GET /api/v1/kbs` - 获取知识库列表
- `POST /api/v1/kbs` - 创建知识库
- `DELETE /api/v1/kbs/{id}` - 删除知识库
- `POST /api/v1/kbs/{id}/documents/upload` - 上传文档
- `DELETE /api/v1/kbs/{id}/documents/{doc_id}` - 删除文档

### 配置 API
- `GET /api/v1/config/settings` - 获取当前配置
- `GET /api/v1/config/models` - 获取可用模型

## 开发注意事项

1. **Milvus 首次启动**: 需要等待 1-2 分钟，可通过 `docker-compose ps` 检查状态
2. **本地模型**: 首次使用 BGE-M3 等本地模型会自动下载，需要网络连接
3. **文档限制**: 单个知识库最多 10 个文档 (MVP 限制)
4. **流式响应**: 前端使用 SSE 实现流式输出，确保网络稳定
5. **API 密钥**: 生产环境请使用真实的 OpenAI API Key
6. **端口配置**: 默认端口配置如下
   - Milvus API: 19532 (如果被占用可修改 docker-compose.yml)
   - Attu 管理界面: 13002
   - 后端 API: 8000
   - 前端: 5173
2. **本地模型**: 首次使用 BGE-M3 等本地模型会自动下载，需要网络连接
3. **文档限制**: 单个知识库最多 10 个文档 (MVP 限制)
4. **流式响应**: 前端使用 SSE 实现流式输出，确保网络稳定
5. **API 密钥**: 生产环境请使用真实的 OpenAI API Key

## 故障排查

### Milvus 连接失败
```bash
# 检查 Milvus 状态
cd docker
docker-compose ps

# 重启 Milvus
docker-compose restart milvus
```

### 后端启动失败
```bash
# 检查 Python 版本
python --version  # 需要 >= 3.10

# 重新安装依赖
cd backend
pip install -e --force-reinstall .
```

### 前端构建失败
```bash
# 清除缓存
cd frontend
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request！
