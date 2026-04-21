# 个人知识库工具 (Note Summary) - 实施计划

## 项目概述

构建一个 AI 驱动的个人知识库工具，用户可以传入任意内容（生活琐事、个人感想、学习笔记等），由 AI 自动整理归类并存储，支持按目录/关键词检索。

## 技术栈

* **后端**: Python 3.11+ / FastAPI

* **数据库**: SQLite (轻量、适合个人使用)

* **AI 集成**: OpenAI API (用于内容整理、分类、总结、调研)

* **向量检索**: ChromaDB (用于语义搜索，支持模糊检索)

* **前端**: Vue 3 + Vite (简洁的单页应用)

* **包管理**: pip + venv

## 系统架构

```
用户输入 → FastAPI 后端 → AI 处理模块 (分类/标签/摘要/调研)
                ↓
           SQLite + ChromaDB 存储
                ↓
           搜索/检索 API ← 前端界面
```

## 数据库设计

### SQLite 表结构

**categories (分类目录)**

| 字段          | 类型         | 说明             |
| ----------- | ---------- | -------------- |
| id          | INTEGER PK | 主键             |
| name        | TEXT       | 分类名称           |
| parent\_id  | INTEGER FK | 父分类ID (支持多级目录) |
| description | TEXT       | 分类描述           |
| created\_at | DATETIME   | 创建时间           |

**notes (知识条目)**

| 字段                 | 类型         | 说明                                   |
| ------------------ | ---------- | ------------------------------------ |
| id                 | INTEGER PK | 主键                                   |
| title              | TEXT       | 标题 (AI 生成)                           |
| raw\_content       | TEXT       | 用户原始输入                               |
| organized\_content | TEXT       | AI 整理后的内容                            |
| summary            | TEXT       | AI 生成的摘要                             |
| category\_id       | INTEGER FK | 所属分类                                 |
| keywords           | TEXT       | 关键词 (逗号分隔)                           |
| source\_type       | TEXT       | 来源类型 (life/thought/knowledge/todo 等) |
| created\_at        | DATETIME   | 创建时间                                 |
| updated\_at        | DATETIME   | 更新时间                                 |

**tags (标签)**

| 字段   | 类型          | 说明   |
| ---- | ----------- | ---- |
| id   | INTEGER PK  | 主键   |
| name | TEXT UNIQUE | 标签名称 |

**note\_tags (笔记-标签关联)**

| 字段       | 类型         | 说明   |
| -------- | ---------- | ---- |
| note\_id | INTEGER FK | 笔记ID |
| tag\_id  | INTEGER FK | 标签ID |

## API 设计

### 笔记管理

* `POST /api/notes` — 提交原始内容，AI 自动整理并保存

* `GET /api/notes` — 获取笔记列表 (支持分页、按分类/标签筛选)

* `GET /api/notes/{id}` — 获取笔记详情

* `PUT /api/notes/{id}` — 更新笔记

* `DELETE /api/notes/{id}` — 删除笔记

### 搜索

* `GET /api/search` — 关键词搜索 (支持全文搜索 + 语义搜索)

* `GET /api/search/semantic` — 语义搜索 (用自然语言描述模糊查找)

### 分类管理

* `GET /api/categories` — 获取分类树

* `POST /api/categories` — 创建分类

* `PUT /api/categories/{id}` — 更新分类

* `DELETE /api/categories/{id}` — 删除分类

### AI 功能

* `POST /api/ai/organize` — 对原始内容进行 AI 整理 (不保存，仅预览)

* `POST /api/ai/research` — 对已有笔记进行 AI 深度调研/扩展

### 标签

* `GET /api/tags` — 获取所有标签

* `GET /api/tags/{id}/notes` — 获取某标签下的所有笔记

## 项目目录结构

```
note-summary/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理 (API Key 等)
│   │   ├── database.py          # 数据库连接与初始化
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── note.py          # 笔记相关 Pydantic 模型
│   │   │   ├── category.py      # 分类相关模型
│   │   │   └── tag.py           # 标签相关模型
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── notes.py         # 笔记路由
│   │   │   ├── search.py        # 搜索路由
│   │   │   ├── categories.py    # 分类路由
│   │   │   ├── tags.py          # 标签路由
│   │   │   └── ai.py            # AI 功能路由
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ai_service.py    # AI 处理服务 (调用 OpenAI)
│   │   │   ├── note_service.py  # 笔记业务逻辑
│   │   │   ├── search_service.py # 搜索服务 (SQLite FTS + ChromaDB)
│   │   │   └── category_service.py # 分类服务
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── text_utils.py    # 文本处理工具
│   ├── requirements.txt
│   └── init_db.py               # 数据库初始化脚本
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.vue
│       ├── main.js
│       ├── api/
│       │   └── index.js         # API 调用封装
│       ├── components/
│       │   ├── NoteInput.vue     # 内容输入组件
│       │   ├── NoteList.vue      # 笔记列表组件
│       │   ├── NoteDetail.vue    # 笔记详情组件
│       │   ├── SearchBar.vue     # 搜索栏组件
│       │   ├── CategoryTree.vue  # 分类树组件
│       │   └── TagCloud.vue      # 标签云组件
│       ├── views/
│       │   ├── HomeView.vue      # 首页 (快速输入)
│       │   ├── SearchView.vue    # 搜索页
│       │   └── CategoryView.vue  # 分类浏览页
│       └── styles/
│           └── main.css          # 全局样式
├── .env.example                  # 环境变量模板
└── README.md
```

## AI 处理流程

### 1. 内容整理流程

```
用户输入原始内容
    ↓
调用 AI API，Prompt 包含：
  - 对内容进行结构化整理
  - 生成合适的标题
  - 自动分类 (从现有分类中选择或建议新分类)
  - 提取关键词/标签
  - 生成内容摘要
    ↓
返回整理结果供用户确认/修改
    ↓
保存到数据库 + 向量存储
```

### 2. 搜索流程

```
用户输入搜索关键词/描述
    ↓
并行执行：
  - SQLite FTS5 全文搜索 (精确关键词匹配)
  - ChromaDB 向量搜索 (语义相似度匹配)
    ↓
合并结果、排序、返回
```

### 3. 调研流程

```
用户选择已有笔记或输入主题
    ↓
AI 基于知识库中的相关内容进行深度分析
    ↓
生成调研报告/知识扩展
    ↓
保存为新的知识条目
```

## 实施步骤

### 第一阶段：后端基础 (Step 1-4)

1. **初始化项目** — 创建项目结构，配置 Python 虚拟环境，安装依赖
2. **数据库层** — 实现 SQLite 数据库初始化、表创建、基础 CRUD 操作
3. **AI 服务** — 封装 OpenAI API 调用，实现内容整理/分类/摘要功能
4. **核心 API** — 实现笔记 CRUD、搜索、分类管理等 API 端点

### 第二阶段：搜索与向量 (Step 5-6)

1. **全文搜索** — 实现 SQLite FTS5 全文搜索
2. **语义搜索** — 集成 ChromaDB，实现基于向量的语义搜索

### 第三阶段：前端界面 (Step 7-9)

1. **前端初始化** — 搭建 Vue 3 + Vite 项目，配置基础框架
2. **核心页面** — 实现内容输入页、笔记列表页、笔记详情页
3. **搜索与分类** — 实现搜索功能页和分类浏览页

### 第四阶段：整合与优化 (Step 10)

1. **联调测试** — 前后端联调，端到端功能测试，修复问题

## 依赖列表

### 后端 (requirements.txt)

```
fastapi==0.115.0
uvicorn==0.30.0
sqlalchemy==2.0.35
pydantic==2.9.0
openai==1.50.0
chromadb==0.5.0
python-dotenv==1.0.1
aiosqlite==0.20.0
```

### 前端 (package.json)

```
vue: ^3.5.0
vite: ^5.4.0
axios: ^1.7.0
```

