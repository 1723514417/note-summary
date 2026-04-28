# Note Summary - 个人知识库

一个基于 AI 的个人知识管理工具，支持智能笔记整理、语义搜索、自动分类等功能。

## 功能特性

- **AI 智能整理** - 输入原始内容，AI 自动生成标题、摘要、关键词、分类建议和标签
- **AI 深度研究** - 对笔记主题进行 AI 深度扩展研究，SSE 实时推送进度，生成更丰富的知识内容
- **多模式搜索** - 支持全文搜索（FTS5）、语义搜索（向量相似度）和混合搜索
- **分类管理** - 支持树形层级分类，自动/手动归类笔记
- **标签系统** - 灵活的标签管理，支持重命名、删除
- **收藏与置顶** - 一键收藏/置顶重要笔记，智能排序（置顶 > 收藏 > 时间）
- **回收站** - 软删除机制，误删可恢复，30 天自动清理
- **双向链接** - `[[标题]]` 语法建立笔记关联，关联笔记选择器一键搜索插入，反向引用自动追踪
- **目录索引** - 笔记详情页右侧目录索引，快速导航到摘要、正文、AI 调研结果、笔记关联
- **数据统计** - ECharts 可视化统计，笔记趋势图、类型分布图
- **暗色模式** - 亮色/暗色主题一键切换，自动检测系统偏好
- **笔记编辑** - 就地编辑模式，支持修改标题、内容、摘要、标签、分类等
- **向量化存储** - 使用 numpy 内存索引或 pgvector 实现高效向量相似度检索
- **移动端适配** - 响应式布局，768px 以下自动切换抽屉式侧边栏
- **用户认证** - JWT 认证、用户注册登录、密码修改、数据隔离

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 + Vue Router + Vite + Axios + Markdown-it + ECharts |
| **后端** | FastAPI + SQLAlchemy + Pydantic |
| **数据库** | SQLite（开发）/ PostgreSQL（生产），自动切换 |
| **AI** | 阿里云通义千问（DashScope 兼容 OpenAI 接口） |
| **向量化** | NumPy（内存索引）/ pgvector（PostgreSQL） |
| **认证** | JWT（HS256）+ bcrypt 密码哈希 |

## 项目结构

```
note-summary/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库初始化、连接池、自动迁移
│   │   ├── schemas.py           # Pydantic 数据模型
│   │   ├── models/
│   │   │   ├── note.py          # SQLAlchemy ORM 模型（Note/Category/Tag/NoteLink）
│   │   │   └── user.py          # 用户模型（User）
│   │   ├── routers/
│   │   │   ├── auth.py          # 认证接口（注册/登录/改密）
│   │   │   ├── notes.py         # 笔记接口（CRUD + 回收站 + 收藏/置顶 + 链接）
│   │   │   ├── search.py        # 搜索接口
│   │   │   ├── categories.py    # 分类接口
│   │   │   ├── tags.py          # 标签接口（列表/重命名/删除）
│   │   │   ├── stats.py         # 数据统计接口
│   │   │   └── ai.py            # AI 功能接口（整理 + SSE 调研）
│   │   └── services/
│   │       ├── ai_service.py    # AI 调用服务
│   │       ├── auth_service.py  # 认证服务（JWT + bcrypt）
│   │       ├── note_service.py  # 笔记业务逻辑（含双向链接引擎）
│   │       ├── search_service.py# 搜索业务逻辑
│   │       ├── category_service.py
│   │       └── vector_service.py# 向量索引服务
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue              # 根组件（侧边栏 + 主题 + Toast + 移动端适配）
│   │   ├── main.js              # 入口文件
│   │   ├── router.js            # 路由配置
│   │   ├── api/
│   │   │   └── index.js         # API 请求封装
│   │   ├── views/
│   │   │   ├── HomeView.vue     # 记录页（新建 + 最近列表 + 关联按钮）
│   │   │   ├── SearchView.vue   # 搜索页
│   │   │   ├── CategoryView.vue # 分类页
│   │   │   ├── NoteDetailView.vue # 笔记详情页（查看/编辑/收藏/置顶/链接/目录索引）
│   │   │   ├── TagsView.vue     # 标签管理页
│   │   │   ├── StatsView.vue    # 数据统计页（ECharts）
│   │   │   ├── TrashView.vue    # 回收站页
│   │   │   └── LoginView.vue    # 登录/注册页
│   │   └── styles/
│   │       └── main.css         # 全局样式（60+ CSS 变量主题系统）
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .env                         # 环境变量（需自行创建）
├── .env.example                 # 环境变量示例
├── start.bat                    # Windows 一键启动脚本
└── start.sh                     # Linux/macOS 一键启动脚本
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

OPENAI_EMBEDDING_API_KEY=your-dashscope-api-key
OPENAI_EMBEDDING_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_EMBEDDING_MODEL=tongyi-embedding-vision-flash

DATABASE_URL=postgresql://postgres:password@localhost:5432/knowledge_db

SECRET_KEY=change-this-to-a-random-secret-key
```

### 2. 安装后端依赖

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动服务

**方式一：一键启动**

```bash
# Windows
start.bat

# Linux/macOS
chmod +x start.sh
./start.sh
```

**方式二：分别启动**

```bash
# 后端（默认端口 8000）
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

# 前端（默认端口 3000）
cd frontend
npm run dev
```

### 5. 访问应用

- 前端界面：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档（Swagger）：http://localhost:8000/docs

## API 接口总览

### 认证 `/api/auth`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/register` | 用户注册 |
| POST | `/login` | 用户登录，返回 JWT Token |
| GET | `/me` | 获取当前用户信息 |
| POST | `/change-password` | 修改密码 |

### 笔记 `/api/notes`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/` | 创建笔记（AI 自动整理） |
| GET | `/` | 笔记列表（分页、筛选） |
| GET | `/trash/list` | 回收站列表 |
| GET | `/trash/count` | 回收站数量 |
| GET | `/{id}` | 笔记详情 |
| GET | `/{id}/links` | 获取笔记关联（反向引用 + 出链） |
| PUT | `/{id}` | 更新笔记 |
| DELETE | `/{id}` | 软删除笔记（移至回收站） |
| POST | `/{id}/star` | 切换收藏状态 |
| POST | `/{id}/pin` | 切换置顶状态 |
| POST | `/{id}/restore` | 从回收站恢复 |
| DELETE | `/{id}/permanent` | 永久删除 |

### 搜索 `/api/search`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 搜索笔记（全文/语义/混合） |

### 分类 `/api/categories`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 分类列表（树形） |
| POST | `/` | 创建分类 |
| PUT | `/{id}` | 更新分类 |
| DELETE | `/{id}` | 删除分类 |

### 标签 `/api/tags`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 标签列表 |
| GET | `/{id}/notes` | 标签下的笔记列表 |
| PUT | `/{id}` | 重命名标签 |
| DELETE | `/{id}` | 删除标签 |

### AI `/api/ai`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/organize` | AI 整理内容 |
| POST | `/research` | AI 深度调研（SSE 流式推送进度） |

### 统计 `/api/stats`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/overview` | 数据统计概览（计数 + 趋势 + 分布） |

## 数据模型

### User（用户）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | String(50) | 用户名（唯一） |
| hashed_password | String(255) | bcrypt 哈希密码 |
| created_at | DateTime | 创建时间 |

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
| user_id | Integer | 所属用户 |
| is_deleted | Boolean | 是否已删除（软删除标记） |
| deleted_at | DateTime | 删除时间 |
| is_starred | Boolean | 是否已收藏 |
| is_pinned | Boolean | 是否已置顶 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### Category（分类）

支持树形层级结构，通过 `parent_id` 实现父子关系。

### Tag（标签）

与笔记多对多关联，通过中间表 `note_tags` 连接。

### NoteLink（笔记链接）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| source_id | Integer | 链接来源笔记 ID（外键） |
| target_id | Integer | 链接目标笔记 ID（外键） |

唯一约束 `(source_id, target_id)` 防止重复链接。

## 配置说明

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| OPENAI_API_KEY | DashScope API Key | - |
| OPENAI_BASE_URL | API 基础地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| OPENAI_MODEL | 文本生成模型 | `qwen3.5-27b` |
| OPENAI_EMBEDDING_MODEL | 向量嵌入模型 | `tongyi-embedding-vision-flash` |
| OPENAI_EMBEDDING_API_KEY | 向量模型 API Key（默认复用 OPENAI_API_KEY） | - |
| OPENAI_EMBEDDING_BASE_URL | 向量模型 API 地址（默认复用 OPENAI_BASE_URL） | - |
| DATABASE_URL | 数据库连接字符串 | `postgresql://postgres:postgres@localhost:5432/knowledge_db` |
| SECRET_KEY | JWT 签名密钥 | 默认值（启动时告警） |

## 生产部署

详细的 Linux 生产环境部署指南请参考 [DEPLOY.md](DEPLOY.md)，包含：

- 服务器要求与依赖安装
- PostgreSQL + pgvector 配置
- 前端构建与后端托管
- Systemd 服务配置
- Nginx 反向代理 + HTTPS
- 运维常用命令

## 许可证

MIT License
