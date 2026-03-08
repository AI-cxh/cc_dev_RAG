------

# 产品需求文档 (PRD): 高性能 RAG 智能体助手

**版本:** 1.0

**状态:** 草案

**技术栈:** Vue 3 + FastAPI + LangGraph + Tavily

------

## 1. 产品概述

本产品旨在构建一个企业级知识库问答助手，通过 **RAG (Retrieval-Augmented Generation)** 技术消除大模型的幻觉。系统支持多种私有文档格式解析，并通过 **LangGraph** 实现复杂的工作流控制（如自我反思、工具调用），为用户提供精准、可溯源的知识问答服务。

------

## 2. 核心功能需求

### 2.1 知识库管理 (Knowledge Base)

- **多格式解析:** * 支持 `.pdf`, `.docx`, `.md`, `.txt` 格式上传。
  - **技术要求:** 使用 `PyMuPDF` 解析 PDF 布局，保留表格信息；使用 `Pandoc` 或 `python-docx` 处理 Word。
- **自动化流水线 (ETL):**
  - **清洗:** 去除冗余字符、页眉页脚。
  - **切分 (Chunking):** 支持“语义切分”或“固定长度+重叠”切分（建议默认 500 tokens，overlap 10%）。
- **向量化控制:**
  - **Embedding 配置:** 允许用户选择模型（如 OpenAI `text-embedding-3-small` 或本地 `BGE-M3`）。
  - **Rerank 配置:** 集成重排序模型（如 `BGE-Reranker` ），提升检索精度。

### 2.2 智能体交互 (Agent Logic)

基于 **LangGraph** 构建有状态的多轮对话系统：

- **检索路由 (Routing):** 智能判断用户问题是否需要检索知识库，或直接调用 Tavily 搜索引擎。
- **重构查询 (Query Rewriting):** 针对模糊提问，利用 LLM 进行问题重写。
- **自我反思机制 (Self-Correction):** * 判断检索到的内容是否与问题相关。
  - 判断生成回答是否包含幻觉。
- **工具集成:** 默认集成 **Tavily Search**，当本地知识库无法覆盖时，自动联网搜索补充。

### 2.3 前端交互 (Frontend)

- **对话界面:** 类似 ChatGPT 的流式输出（SSE/WebSocket），支持 Markdown 渲染及公式显示。
- **引用溯源:** 回答中需标记数据来源，点击可跳转至对应文档的原始切片。
- **后台管理:** * 上传进度条显示。
  - 向量库索引状态监控。

------

## 3. 技术架构设计

### 3.1 逻辑架构图

| **层级**     | **采用技术**          | **说明**                        |
| ------------ | --------------------- | ------------------------------- |
| **表示层**   | Vue 3 + Tailwind CSS  | 响应式布局，Pinia 状态管理      |
| **API 层**   | FastAPI + Pydantic    | 异步处理，自动生成 OpenAPI 文档 |
| **逻辑引擎** | LangGraph + LangChain | 维护对话状态机，编排 Agent 节点 |
| **向量存储** | Milvus / Chroma       | 存储 Embeddings 及元数据        |
| **外部工具** | Tavily API            | 实时互联网搜索补丁              |



