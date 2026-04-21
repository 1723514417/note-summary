# Note Summary - 个人知识库

一个基于 AI 的个人知识管理工具，支持智能笔记整理、语义搜索、自动分类等功能。

## 功能特性

- **AI 智能整理** - 输入原始内容，AI 自动生成标题、摘要、关键词、分类建议和标签
- **AI 深度研究** - 对笔记主题进行 AI 深度扩展研究，生成更丰富的知识内容
- **多模式搜索** - 支持全文搜索（FTS5）、语义搜索（向量相似度）和混合搜索
- **分类管理** - 支持树形层级分类，自动/手动归类笔记
- **标签系统** - 灵活的标签管理，支持多对多关联
- **向量化存储** - 使用 numpy 内存索引实现高效向量相似度检索

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 + Vue Router + Vite + Axios + Markdown-it |
| **后端** | FastAPI + SQLAlchemy + Pydantic |
| **数据库** | SQLite（FTS5 全文搜索 + 向量存储） |
| **AI** | 阿里云通义千问（DashScope 兼容 OpenAI 接口） |
| **向量化** | NumPy（内存索引 + 矩阵运算） |

## 项目结构

```
note-summary/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库初始化与连接
│   │   ├── schemas.py           # Pydantic 数据模型
│   │   ├── models/
│   │   │   └── note.py          # SQLAlchemy ORM 模型
│   │   ├── routers/
│   │   │   ├── notes.py         # 笔记接口
│   │   │   ├── search.py        # 搜索接口
│   │   │   ├── categories.py    # 分类接口
│   │   │   ├── tags.py          # 标签接口
│   │   │   └── ai.py            # AI 功能接口
│   │   └── services/
│   │       ├── ai_service.py    # AI 调用服务
│   │       ├── note_service.py  # 笔记业务逻辑
│   │       ├── search_service.py# 搜索业务逻辑
│   │       ├── category_service.py
│   │       └── vector_service.py# 向量索引服务
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue              # 根组件
│   │   ├── main.js              # 入口文件
│   │   ├── router.js            # 路由配置
│   │   ├── api/
│   │   │   └── index.js         # API 请求封装
│   │   ├── views/
│   │   │   ├── HomeView.vue     # 记录页
│   │   │   ├── SearchView.vue   # 搜索页
│   │   │   ├── CategoryView.vue # 分类页
│   │   │   └── NoteDetailView.vue # 笔记详情页
│   │   └── styles/
│   │       └── main.css         # 全局样式
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .env                         # 环境变量（需自行创建）
├── .env.example                 # 环境变量示例
└── start.bat                    # Windows 一键启动脚本
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- 阿里云 DashScope API Key

### 1. 配置环境变量

复制 `.env.example` 为 `.env`，填入你的 API Key：

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=your-dashscope-api-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen3.5-27b
OPENAI_EMBEDDING_MODEL=tongyi-embedding-vision-flash
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动服务

**方式一：一键启动（Windows）**

```bash
start.bat
```

**方式二：分别启动**

```bash
# 后端（默认端口 8000）
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 前端（默认端口 5173）
cd frontend
npm run dev
```

### 5. 访问应用

- 前端界面：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档（Swagger）：http://localhost:8000/docs

## 数据模型

### Note（笔记）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| title | String(255) | 标题 |
| raw_content | Text | 原始内容 |
| organized_content | Text | AI 整理后内容 |
| summary | Text | 摘要 |
| category_id | Integer | 所属分类 |
| keywords | Text | 关键词 |
| source_type | String(50) | 来源类型（life/thought/knowledge/todo/idea/work） |
| research_content | Text | AI 研究扩展内容 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### Category（分类）

支持树形层级结构，通过 `parent_id` 实现父子关系。

### Tag（标签）

与笔记多对多关联，通过中间表 `note_tags` 连接。

## 配置说明

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| OPENAI_API_KEY | DashScope API Key | - |
| OPENAI_BASE_URL | API 基础地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| OPENAI_MODEL | 文本生成模型 | `qwen3.5-27b` |
| OPENAI_EMBEDDING_MODEL | 向量嵌入模型 | `tongyi-embedding-vision-flash` |
| OPENAI_EMBEDDING_API_KEY | 向量模型 API Key（默认复用 OPENAI_API_KEY） | - |
| OPENAI_EMBEDDING_BASE_URL | 向量模型 API 地址（默认复用 OPENAI_BASE_URL） | - |
| DATABASE_URL | 数据库连接字符串 | `sqlite+aiosqlite:///./data/knowledge.db` |
