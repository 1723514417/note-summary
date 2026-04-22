# 暗色模式实现计划

## 概述

为 Note Summary 应用添加完整的暗色模式支持，包括手动切换和系统偏好自动适配。

## 当前问题分析

项目当前存在以下阻碍暗色模式的问题：

1. **CSS 变量使用不彻底**：`main.css` 中定义了 8 个 CSS 变量，但有约 50+ 处硬编码颜色值
2. **LoginView.vue 存在独立 scoped 样式**：约 25 处硬编码颜色，且与 main.css 有大量重复
3. **组件内联 style 中包含颜色**：NoteDetailView（`background: #f8fafc`）、CategoryView、HomeView 中有颜色相关的内联样式

## 实现步骤

### 第 1 步：扩展 CSS 变量体系（main.css `:root` 部分）

将现有的 8 个变量扩展为完整的主题变量系统，补充缺失的语义化变量：

```css
:root {
  /* 原有变量 */
  --primary: #4f46e5;
  --primary-hover: #4338ca;
  --bg: #f8fafc;
  --card-bg: #ffffff;
  --text: #1e293b;
  --text-secondary: #64748b;
  --border: #e2e8f0;
  --success: #10b981;
  --danger: #ef4444;
  --radius: 8px;
  --shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);

  /* 新增变量 */
  --text-label: #374151;
  --input-border: #e2e8f0;
  --input-focus-ring: rgba(79, 70, 229, 0.1);
  --error-bg: #fef2f2;
  --error-text: #dc2626;
  --success-bg: #f0fdf4;
  --success-text: #16a34a;
  --primary-light: #a5b4fc;
  --nav-hover-bg: #eef2ff;
  --tag-bg: #eef2ff;
  --tag-hover-bg: #e0e7ff;
  --btn-secondary-hover: #e2e8f0;
  --logout-hover-bg: #fef2f2;
  --danger-hover: #dc2626;
  --modal-bg: #ffffff;
  --modal-overlay: rgba(0, 0, 0, 0.4);
  --modal-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  --sidebar-shadow: rgba(0, 0, 0, 0.08);
  --code-bg: #f1f5f9;
  --code-block-bg: #1e293b;
  --code-block-text: #e2e8f0;
  --tab-bg: #f1f5f9;
  --tab-active-bg: #ffffff;
  --tips-bg: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%);
  --tips-border: #e0e7ff;
  --input-bg: #ffffff;
  --note-hover-shadow: rgba(79, 70, 229, 0.1);
  --summary-bg: #f8fafc;
  --login-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --login-card-bg: #ffffff;

  /* source-type 徽章变量 */
  --source-life-bg: #dcfce7;
  --source-life-text: #166534;
  --source-thought-bg: #fef3c7;
  --source-thought-text: #92400e;
  --source-knowledge-bg: #dbeafe;
  --source-knowledge-text: #1e40af;
  --source-todo-bg: #fce7f3;
  --source-todo-text: #9d174d;
  --source-idea-bg: #f3e8ff;
  --source-idea-text: #6b21a8;
  --source-work-bg: #ffedd5;
  --source-work-text: #9a3412;
}
```

### 第 2 步：添加暗色主题变量（main.css 新增 `[data-theme="dark"]` 选择器）

```css
[data-theme="dark"] {
  --primary: #818cf8;
  --primary-hover: #6366f1;
  --bg: #0f172a;
  --card-bg: #1e293b;
  --text: #e2e8f0;
  --text-secondary: #94a3b8;
  --border: #334155;
  --success: #34d399;
  --danger: #f87171;
  --shadow: 0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2);

  --text-label: #cbd5e1;
  --input-border: #475569;
  --input-focus-ring: rgba(129, 140, 248, 0.2);
  --error-bg: #451a1a;
  --error-text: #fca5a5;
  --success-bg: #052e16;
  --success-text: #86efac;
  --primary-light: #4f46e5;
  --nav-hover-bg: #1e1b4b;
  --tag-bg: #1e1b4b;
  --tag-hover-bg: #312e81;
  --btn-secondary-hover: #475569;
  --logout-hover-bg: #451a1a;
  --danger-hover: #b91c1c;
  --modal-bg: #1e293b;
  --modal-overlay: rgba(0, 0, 0, 0.6);
  --modal-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  --sidebar-shadow: rgba(0, 0, 0, 0.3);
  --code-bg: #334155;
  --code-block-bg: #0f172a;
  --code-block-text: #e2e8f0;
  --tab-bg: #334155;
  --tab-active-bg: #1e293b;
  --tips-bg: linear-gradient(135deg, #1e1b4b 0%, #2e1065 100%);
  --tips-border: #312e81;
  --input-bg: #0f172a;
  --note-hover-shadow: rgba(129, 140, 248, 0.15);
  --summary-bg: #0f172a;
  --login-gradient: linear-gradient(135deg, #312e81 0%, #4c1d95 100%);
  --login-card-bg: #1e293b;

  --source-life-bg: #052e16;
  --source-life-text: #86efac;
  --source-thought-bg: #451a03;
  --source-thought-text: #fcd34d;
  --source-knowledge-bg: #172554;
  --source-knowledge-text: #93c5fd;
  --source-todo-bg: #4a0d2b;
  --source-todo-text: #f9a8d4;
  --source-idea-bg: #2e1065;
  --source-idea-text: #c4b5fd;
  --source-work-bg: #431407;
  --source-work-text: #fdba74;
}
```

### 第 3 步：替换 main.css 中所有硬编码颜色为 CSS 变量

需要替换的硬编码颜色（约 30+ 处）：

| 位置 | 当前硬编码值 | 替换为变量 |
|------|------------|-----------|
| `.sidebar:hover` box-shadow | `rgba(0, 0, 0, 0.08)` | `var(--sidebar-shadow)` |
| `.logout-btn:hover` background | `#fef2f2` | `var(--logout-hover-bg)` |
| `.modal-overlay` background | `rgba(0, 0, 0, 0.4)` | `var(--modal-overlay)` |
| `.modal-card` background | `#fff` | `var(--modal-bg)` |
| `.modal-card` box-shadow | `rgba(0, 0, 0, 0.15)` | `var(--modal-shadow)` |
| `.modal-card h3` color | `#1e293b` | `var(--text)` |
| `.modal-card .form-group label` color | `#374151` | `var(--text-label)` |
| `.modal-card .form-group input` border | `#e2e8f0` | `var(--input-border)` |
| `.modal-card .form-group input:focus` border-color | `#4f46e5` | `var(--primary)` |
| `.modal-card .form-group input:focus` box-shadow | `rgba(79, 70, 229, 0.1)` | `var(--input-focus-ring)` |
| `.modal-card .error-msg` background/color | `#fef2f2` / `#dc2626` | `var(--error-bg)` / `var(--error-text)` |
| `.modal-card .success-msg` background/color | `#f0fdf4` / `#16a34a` | `var(--success-bg)` / `var(--success-text)` |
| `.btn-cancel` border/background/color | `#e2e8f0` / `#fff` / `#64748b` | `var(--border)` / `var(--card-bg)` / `var(--text-secondary)` |
| `.btn-cancel:hover` background | `#f8fafc` | `var(--bg)` |
| `.btn-confirm` background | `#4f46e5` | `var(--primary)` |
| `.btn-confirm:hover` background | `#4338ca` | `var(--primary-hover)` |
| `.btn-confirm:disabled` background | `#a5b4fc` | `var(--primary-light)` |
| `.sidebar-nav a:hover` background | `#eef2ff` | `var(--nav-hover-bg)` |
| `textarea/input:focus` box-shadow | `rgba(79, 70, 229, 0.1)` | `var(--input-focus-ring)` |
| `.btn-primary:disabled` background | `#a5b4fc` | `var(--primary-light)` |
| `.btn-danger:hover` background | `#dc2626` | `var(--danger-hover)` |
| `.btn-secondary:hover` background | `#e2e8f0` | `var(--btn-secondary-hover)` |
| `.tag` background | `#eef2ff` | `var(--tag-bg)` |
| `.tag-clickable:hover` background | `#e0e7ff` | `var(--tag-hover-bg)` |
| `.source-*` (6 组) | 各自硬编码 | 对应 `var(--source-*-bg/text)` |
| `.note-list-item:hover` box-shadow | `rgba(79, 70, 229, 0.1)` | `var(--note-hover-shadow)` |
| `.tips-panel` background/border | `linear-gradient` / `#e0e7ff` | `var(--tips-bg)` / `var(--tips-border)` |
| `.markdown-content code` background | `#f1f5f9` | `var(--code-bg)` |
| `.markdown-content pre` background/color | `#1e293b` / `#e2e8f0` | `var(--code-block-bg)` / `var(--code-block-text)` |
| `.toast` box-shadow | `rgba(0,0,0,0.15)` | `0 4px 12px rgba(0,0,0,0.2)` |

### 第 4 步：替换 LoginView.vue scoped 样式中的硬编码颜色

LoginView.vue 中约 25 处硬编码颜色，全部替换为 CSS 变量。由于 scoped 样式也能访问全局 CSS 变量，只需将硬编码值替换为 `var(--xxx)` 引用即可。

| 选择器 | 当前值 | 替换为 |
|--------|--------|--------|
| `.login-page` background | `linear-gradient(135deg, #667eea, #764ba2)` | `var(--login-gradient)` |
| `.login-card` background | `#fff` | `var(--login-card-bg)` |
| `.login-header h1` color | `#1e293b` | `var(--text)` |
| `.login-header p` color | `#64748b` | `var(--text-secondary)` |
| `.login-tabs` background | `#f1f5f9` | `var(--tab-bg)` |
| `.tab-btn` color | `#64748b` | `var(--text-secondary)` |
| `.tab-btn.active` background/color | `#fff` / `#4f46e5` | `var(--tab-active-bg)` / `var(--primary)` |
| `.form-group label` color | `#374151` | `var(--text-label)` |
| `.form-group input` border | `#e2e8f0` | `var(--input-border)` |
| `.form-group input:focus` border-color/box-shadow | `#4f46e5` / `rgba(...)` | `var(--primary)` / `var(--input-focus-ring)` |
| `.error-msg` background/color | `#fef2f2` / `#dc2626` | `var(--error-bg)` / `var(--error-text)` |
| `.submit-btn` background/color | `#4f46e5` / `#fff` | `var(--primary)` / `#fff` |
| `.submit-btn:hover` background | `#4338ca` | `var(--primary-hover)` |
| `.submit-btn:disabled` background | `#a5b4fc` | `var(--primary-light)` |

### 第 5 步：替换组件内联 style 中的颜色

**NoteDetailView.vue** 中的内联颜色：
- `background: #f8fafc` → `background: var(--summary-bg)` (2处)

**CategoryView.vue** 中的内联颜色（已使用 `var(--text-secondary)` 和 `var(--border)`，无需修改）

**HomeView.vue** 中无颜色相关内联样式

### 第 6 步：添加暗色/亮色模式切换 UI

在 `App.vue` 侧边栏底部（`.sidebar-footer`）添加主题切换按钮：

- 在用户信息区域下方添加一个 🌙/☀️ 切换按钮
- 按钮跟随 sidebar 收缩/展开行为（收缩时只显示 emoji 图标）

### 第 7 步：实现主题切换逻辑（App.vue `<script>` 部分）

```javascript
// 主题管理
const isDark = ref(false)

const initTheme = () => {
  const saved = localStorage.getItem('theme')
  if (saved) {
    isDark.value = saved === 'dark'
  } else {
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}
```

### 第 8 步：添加系统偏好监听

当用户没有手动设置过主题时，跟随系统偏好变化自动切换：

```javascript
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
  if (!localStorage.getItem('theme')) {
    isDark.value = e.matches
    document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
  }
})
```

## 涉及的文件清单

| 文件 | 修改内容 |
|------|---------|
| `frontend/src/styles/main.css` | 扩展 `:root` 变量、新增 `[data-theme="dark"]` 变量、替换 30+ 处硬编码颜色 |
| `frontend/src/views/LoginView.vue` | 替换 scoped 样式中 25 处硬编码颜色为 CSS 变量 |
| `frontend/src/views/NoteDetailView.vue` | 替换 2 处内联 `background: #f8fafc` 为 `var(--summary-bg)` |
| `frontend/src/App.vue` | 添加主题切换按钮 UI + 主题管理 JS 逻辑 |

## 预期效果

1. 侧边栏底部新增 🌙/☀️ 切换按钮
2. 点击按钮即时切换亮色/暗色主题，全局生效
3. 主题偏好保存在 localStorage，下次打开自动恢复
4. 首次使用自动检测系统暗色模式偏好
5. 所有页面（登录页、首页、搜索、分类、详情）均完整适配暗色模式
