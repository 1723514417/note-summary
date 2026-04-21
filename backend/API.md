# Note Summary API 接口文档

Base URL: `http://localhost:8000`

所有接口返回 JSON 格式数据。错误响应格式：

```json
{
  "detail": "错误描述信息"
}
```

---

## 1. 笔记管理 `/api/notes`

### 1.1 创建笔记

AI 自动整理原始内容，生成标题、摘要、关键词、分类和标签。

```
POST /api/notes
```

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| raw_content | string | 是 | 原始笔记内容 |
| category_id | integer | 否 | 指定分类 ID |
| source_type | string | 否 | 来源类型（life/thought/knowledge/todo/idea/work） |

**请求示例：**

```json
{
  "raw_content": "今天学习了 Vue3 的组合式 API，感觉比选项式 API 更灵活..."
}
```

**响应：** `NoteResponse`

```json
{
  "id": 1,
  "title": "Vue3 组合式 API 学习笔记",
  "raw_content": "今天学习了 Vue3 的组合式 API...",
  "organized_content": "## 学习要点\n\n1. 组合式 API 概述...",
  "summary": "记录了 Vue3 组合式 API 的学习心得...",
  "category_id": 3,
  "keywords": "Vue3,组合式API,前端开发",
  "source_type": "knowledge",
  "research_content": null,
  "created_at": "2025-01-01T10:00:00",
  "updated_at": "2025-01-01T10:00:00",
  "tags": [
    {"id": 1, "name": "Vue3"},
    {"id": 2, "name": "前端"}
  ]
}
```

---

### 1.2 获取笔记列表

```
GET /api/notes
```

**查询参数：**

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| skip | integer | 0 | 跳过记录数（分页偏移） |
| limit | integer | 20 | 每页数量（1-100） |
| category_id | integer | - | 按分类筛选 |
| source_type | string | - | 按来源类型筛选 |
| keyword | string | - | 关键词筛选 |

**响应：** `SearchResult`

```json
{
  "notes": [
    {
      "id": 1,
      "title": "Vue3 组合式 API 学习笔记",
      "summary": "记录了 Vue3 组合式 API 的学习心得...",
      "category_id": 3,
      "keywords": "Vue3,组合式API",
      "source_type": "knowledge",
      "created_at": "2025-01-01T10:00:00"
    }
  ],
  "total": 1
}
```

---

### 1.3 获取笔记详情

```
GET /api/notes/{note_id}
```

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| note_id | integer | 笔记 ID |

**响应：** `NoteResponse`（同创建笔记响应）

---

### 1.4 更新笔记

```
PUT /api/notes/{note_id}
```

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| note_id | integer | 笔记 ID |

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 标题 |
| organized_content | string | 否 | 整理后内容 |
| summary | string | 否 | 摘要 |
| category_id | integer | 否 | 分类 ID |
| keywords | string | 否 | 关键词 |
| source_type | string | 否 | 来源类型 |
| research_content | string | 否 | 研究扩展内容 |

**响应：** `NoteResponse`

---

### 1.5 删除笔记

```
DELETE /api/notes/{note_id}
```

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| note_id | integer | 笔记 ID |

**响应：**

```json
{
  "message": "删除成功"
}
```

---

## 2. 搜索 `/api/search`

### 2.1 搜索笔记

```
GET /api/search
```

**查询参数：**

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| q | string | 是 | - | 搜索关键词（最少 1 个字符） |
| limit | integer | 否 | 20 | 返回数量（1-100） |
| offset | integer | 否 | 0 | 偏移量 |
| mode | string | 否 | hybrid | 搜索模式：`fts`（全文）/ `semantic`（语义）/ `hybrid`（混合） |

**搜索模式说明：**

| 模式 | 说明 |
|------|------|
| `fts` | 基于 SQLite FTS5 的全文搜索，速度快，精确匹配关键词 |
| `semantic` | 基于向量嵌入的语义搜索，能理解语义相似性 |
| `hybrid` | 混合搜索，结合全文搜索和语义搜索的结果 |

**响应：** `SearchResult`

```json
{
  "notes": [
    {
      "id": 1,
      "title": "Vue3 组合式 API 学习笔记",
      "summary": "记录了 Vue3 组合式 API 的学习心得...",
      "category_id": 3,
      "keywords": "Vue3,组合式API",
      "source_type": "knowledge",
      "created_at": "2025-01-01T10:00:00"
    }
  ],
  "total": 1
}
```

---

## 3. 分类管理 `/api/categories`

### 3.1 获取分类列表

返回树形结构的分类列表。

```
GET /api/categories
```

**响应：** `CategoryResponse[]`（树形结构）

```json
[
  {
    "id": 1,
    "name": "技术",
    "parent_id": null,
    "description": "技术相关笔记",
    "created_at": "2025-01-01T10:00:00",
    "children": [
      {
        "id": 3,
        "name": "前端",
        "parent_id": 1,
        "description": null,
        "created_at": "2025-01-01T10:00:00",
        "children": []
      }
    ]
  }
]
```

---

### 3.2 创建分类

```
POST /api/categories
```

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 分类名称 |
| parent_id | integer | 否 | 父分类 ID（为空表示顶级分类） |
| description | string | 否 | 分类描述 |

**请求示例：**

```json
{
  "name": "前端",
  "parent_id": 1,
  "description": "前端开发相关笔记"
}
```

**响应：** `CategoryResponse`

---

### 3.3 更新分类

```
PUT /api/categories/{category_id}
```

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| category_id | integer | 分类 ID |

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 分类名称 |
| parent_id | integer | 否 | 父分类 ID |
| description | string | 否 | 分类描述 |

**响应：** `CategoryResponse`

---

### 3.4 删除分类

```
DELETE /api/categories/{category_id}
```

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| category_id | integer | 分类 ID |

**响应：**

```json
{
  "message": "删除成功"
}
```

---

## 4. 标签管理 `/api/tags`

### 4.1 获取标签列表

```
GET /api/tags
```

**响应：** `TagResponse[]`

```json
[
  { "id": 1, "name": "Vue3" },
  { "id": 2, "name": "前端" },
  { "id": 3, "name": "Python" }
]
```

---

### 4.2 获取标签下的笔记

```
GET /api/tags/{tag_id}/notes
```

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| tag_id | integer | 标签 ID |

**查询参数：**

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| skip | integer | 0 | 跳过记录数 |
| limit | integer | 20 | 每页数量（1-100） |

**响应：** `NoteListItem[]`

```json
[
  {
    "id": 1,
    "title": "Vue3 组合式 API 学习笔记",
    "summary": "记录了 Vue3 组合式 API 的学习心得...",
    "category_id": 3,
    "keywords": "Vue3,组合式API",
    "source_type": "knowledge",
    "created_at": "2025-01-01T10:00:00"
  }
]
```

---

## 5. AI 功能 `/api/ai`

### 5.1 AI 整理内容

将原始文本交给 AI 进行整理，返回结构化内容（不创建笔记）。

```
POST /api/ai/organize
```

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| raw_content | string | 是 | 原始内容 |

**请求示例：**

```json
{
  "raw_content": "今天学习了 Vue3 的组合式 API，感觉比选项式 API 更灵活..."
}
```

**响应：** `OrganizeResponse`

```json
{
  "title": "Vue3 组合式 API 学习笔记",
  "organized_content": "## 学习要点\n\n1. 组合式 API 概述...",
  "summary": "记录了 Vue3 组合式 API 的学习心得...",
  "suggested_category": "技术/前端",
  "suggested_tags": ["Vue3", "前端", "JavaScript"],
  "source_type": "knowledge",
  "keywords": "Vue3,组合式API,前端开发"
}
```

---

### 5.2 AI 深度研究

对指定笔记或主题进行 AI 深度研究，生成扩展内容。

```
POST /api/ai/research
```

**请求体：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| note_id | integer | 否* | 笔记 ID（与 topic 二选一） |
| topic | string | 否* | 研究主题（与 note_id 二选一） |

> *`note_id` 和 `topic` 至少提供一个。提供 `note_id` 时，会基于笔记内容进行扩展研究并自动更新笔记的 `research_content` 字段。

**请求示例 1 — 基于笔记扩展：**

```json
{
  "note_id": 1
}
```

**请求示例 2 — 基于主题研究：**

```json
{
  "topic": "Vue3 组合式 API 最佳实践"
}
```

**响应：** `ResearchResponse`

```json
{
  "research_content": "## Vue3 组合式 API 最佳实践\n\n### 1. 逻辑复用...",
  "related_notes": [
    {
      "id": 1,
      "title": "Vue3 组合式 API 学习笔记",
      "summary": "记录了 Vue3 组合式 API 的学习心得...",
      "category_id": 3,
      "keywords": "Vue3,组合式API",
      "source_type": "knowledge",
      "created_at": "2025-01-01T10:00:00"
    }
  ]
}
```

---

## 数据模型参考

### Source Type 枚举值

| 值 | 说明 | 标签色 |
|----|------|--------|
| `life` | 生活 | 绿色 |
| `thought` | 想法 | 黄色 |
| `knowledge` | 知识 | 蓝色 |
| `todo` | 待办 | 粉色 |
| `idea` | 创意 | 紫色 |
| `work` | 工作 | 橙色 |

### 通用字段说明

| 字段 | 说明 |
|------|------|
| `created_at` | ISO 8601 格式时间戳，时区为 Asia/Shanghai |
| `updated_at` | ISO 8601 格式时间戳，笔记更新时自动刷新 |

### 分页说明

支持分页的接口统一使用 `skip`（偏移量）和 `limit`（每页数量）参数。笔记列表接口额外返回 `total` 字段表示总记录数。
