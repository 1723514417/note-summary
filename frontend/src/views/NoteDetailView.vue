<template>
  <div>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!note" class="empty-state">
      <h3>笔记未找到</h3>
      <router-link to="/" class="btn btn-primary" style="margin-top: 12px">返回首页</router-link>
    </div>
    <div v-else>
      <div class="flex-between mb-16">
        <button class="btn btn-secondary btn-sm" @click="$router.back()">← 返回</button>
        <div class="flex-row">
          <template v-if="!editing">
            <button class="btn btn-primary btn-sm" @click="startEdit">✏️ 编辑</button>
            <button class="btn btn-secondary btn-sm" @click="handleStar" :disabled="toggling">
              {{ note.is_starred ? '⭐' : '☆' }}
            </button>
            <button class="btn btn-secondary btn-sm" @click="handlePin" :disabled="toggling">
              {{ note.is_pinned ? '📌' : '📍' }}
            </button>
            <button
              v-if="note.research_content"
              class="btn btn-secondary btn-sm"
              disabled
              style="opacity: 0.7; cursor: default;"
            >
              ✅ 已调研
            </button>
            <button
              v-else
              class="btn btn-secondary btn-sm"
              @click="doResearch"
              :disabled="researching"
            >
              {{ researching ? '调研中...' : '🔬 AI 调研' }}
            </button>
            <button class="btn btn-danger btn-sm" @click="removeNote">删除</button>
          </template>
          <template v-else>
            <button class="btn btn-secondary btn-sm" @click="openLinkPicker">🔗 关联笔记</button>
            <button class="btn btn-secondary btn-sm" @click="cancelEdit">取消</button>
            <button class="btn btn-primary btn-sm" @click="saveEdit" :disabled="saving">
              {{ saving ? '保存中...' : '💾 保存' }}
            </button>
          </template>
        </div>
      </div>

      <div class="note-detail-layout">
        <div class="note-main">
          <div class="card" id="section-summary">
            <div class="flex-row mb-8" style="flex-wrap: wrap">
              <template v-if="!editing">
                <span class="source-type" :class="'source-' + note.source_type">{{ sourceTypeLabel(note.source_type) }}</span>
                <span class="tag" v-for="tag in note.tags" :key="tag.id">{{ tag.name }}</span>
              </template>
              <template v-else>
                <select v-model="editForm.source_type" class="btn btn-secondary btn-sm" style="font-size: 12px">
                  <option value="">未分类</option>
                  <option v-for="(label, key) in sourceTypes" :key="key" :value="key">{{ label }}</option>
                </select>
                <div class="edit-tags">
                  <span class="tag" v-for="(tag, idx) in editForm.tags" :key="idx">
                    {{ tag }}
                    <span class="tag-remove" @click="editForm.tags.splice(idx, 1)">×</span>
                  </span>
                  <input
                    v-model="newTag"
                    class="tag-input"
                    placeholder="+ 标签"
                    @keydown.enter.prevent="addTag"
                    @blur="addTag"
                  />
                </div>
              </template>
              <span class="note-date">{{ formatDate(note.created_at) }}</span>
            </div>

            <template v-if="!editing">
              <h1 style="font-size: 22px; margin-bottom: 12px">{{ note.title }}</h1>
            </template>
            <template v-else>
              <input v-model="editForm.title" class="edit-title" placeholder="标题" />
            </template>

            <template v-if="!editing">
              <div v-if="note.summary" style="background: var(--summary-bg); padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid var(--primary)">
                <strong>摘要：</strong>{{ note.summary }}
              </div>
            </template>
            <template v-else>
              <div style="margin-bottom: 16px">
                <label style="font-size: 13px; font-weight: 500; color: var(--text-label); display: block; margin-bottom: 6px">摘要</label>
                <textarea v-model="editForm.summary" rows="3" style="min-height: 80px; background: var(--summary-bg); padding: 12px 16px; border-radius: 8px; border-left: 4px solid var(--primary)"></textarea>
              </div>
            </template>
          </div>

          <div class="card mt-16" id="section-content">
            <template v-if="!editing">
              <div v-if="note.organized_content" class="markdown-content" v-html="renderMarkdown(note.organized_content)"></div>
            </template>
            <template v-else>
              <label style="font-size: 13px; font-weight: 500; color: var(--text-label); display: block; margin-bottom: 6px">整理内容（Markdown）</label>
              <textarea ref="contentTextarea" v-model="editForm.organized_content" rows="15" style="min-height: 300px; font-family: monospace; font-size: 13px; line-height: 1.6"></textarea>
            </template>

            <template v-if="!editing">
              <details style="margin-top: 20px">
                <summary style="cursor: pointer; color: var(--text-secondary); font-size: 14px">
                  查看原始输入
                </summary>
                <div style="margin-top: 8px; padding: 12px; background: var(--summary-bg); border-radius: 8px; white-space: pre-wrap; font-size: 14px">
                  {{ note.raw_content }}
                </div>
              </details>
            </template>

            <template v-if="editing">
              <div style="margin-top: 16px">
                <label style="font-size: 13px; font-weight: 500; color: var(--text-label); display: block; margin-bottom: 6px">分类</label>
                <select v-model="editForm.category_id" class="btn btn-secondary" style="font-size: 14px">
                  <option :value="null">无分类</option>
                  <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                </select>
              </div>
            </template>
          </div>

          <div v-if="!editing && researching" class="card mt-16" id="section-research">
            <h3 style="margin-bottom: 12px">🔬 AI 调研中...</h3>
            <div class="research-progress">
              <div class="research-stage">{{ researchStage }}</div>
              <div class="research-dots">
                <span class="dot dot1">●</span>
                <span class="dot dot2">●</span>
                <span class="dot dot3">●</span>
              </div>
            </div>
          </div>

          <div v-else-if="!editing && note.research_content" class="card mt-16" id="section-research">
            <h3 style="margin-bottom: 12px">🔬 AI 调研结果</h3>
            <div class="markdown-content" v-html="renderMarkdown(note.research_content)"></div>
          </div>

          <div v-if="!editing" class="card mt-16" id="section-links">
            <h3 style="margin-bottom: 12px; font-size: 16px">🔗 笔记关联</h3>
            <div v-if="links.backlinks.length > 0 || links.outgoing.length > 0">
              <div v-if="links.backlinks.length > 0" style="margin-bottom: 16px">
                <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px">
                  反向引用（{{ links.backlinks.length }} 篇笔记引用了本篇）
                </div>
                <div class="link-list">
                  <router-link
                    v-for="bl in links.backlinks"
                    :key="bl.id"
                    :to="`/notes/${bl.id}`"
                    class="link-item"
                  >
                    <span class="link-title">{{ bl.title }}</span>
                    <span v-if="bl.summary" class="link-summary">{{ bl.summary.slice(0, 60) }}{{ bl.summary.length > 60 ? '...' : '' }}</span>
                  </router-link>
                </div>
              </div>
              <div v-if="links.outgoing.length > 0">
                <div style="font-size: 13px; color: var(--text-secondary); margin-bottom: 8px">
                  出链（本篇引用了 {{ links.outgoing.length }} 篇笔记）
                </div>
                <div class="link-list">
                  <router-link
                    v-for="ol in links.outgoing"
                    :key="ol.id"
                    :to="`/notes/${ol.id}`"
                    class="link-item"
                  >
                    <span class="link-title">{{ ol.title }}</span>
                  </router-link>
                </div>
              </div>
            </div>
            <div v-else style="color: var(--text-secondary); font-size: 14px">
              暂无关联。编辑时点击「🔗 关联笔记」或使用 <code style="background: var(--tag-bg); padding: 2px 6px; border-radius: 4px">[[标题]]</code> 建立链接。
            </div>
          </div>
        </div>

        <div v-if="!editing" class="note-sidebar">
          <div class="card toc-card">
            <h4 class="toc-title">📑 目录索引</h4>
            <nav class="toc-nav">
              <a v-if="note.summary" class="toc-item" @click="scrollToSection('section-summary')">
                <span class="toc-icon">📋</span> 摘要
              </a>
              <a v-if="note.organized_content" class="toc-item" @click="scrollToSection('section-content')">
                <span class="toc-icon">📄</span> 正文
              </a>
              <a v-if="note.research_content" class="toc-item" @click="scrollToSection('section-research')">
                <span class="toc-icon">🔬</span> AI 调研结果
              </a>
              <a class="toc-item" @click="scrollToSection('section-links')">
                <span class="toc-icon">🔗</span> 笔记关联
                <span v-if="links.backlinks.length + links.outgoing.length > 0" class="toc-badge">
                  {{ links.backlinks.length + links.outgoing.length }}
                </span>
              </a>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <div v-if="linkPickerOpen" class="modal-overlay" @click.self="linkPickerOpen = false">
      <div class="modal-card modal-card--picker">
        <h3>
          <span style="font-size: 18px">🔗</span>
          选择要关联的笔记
        </h3>
        <div class="modal-body">
          <div class="picker-search-wrap">
            <span class="picker-search-icon">🔍</span>
            <input
              ref="pickerSearchInput"
              v-model="linkPickerQuery"
              class="form-input"
              placeholder="搜索笔记标题或内容..."
              @input="searchNotesForLink"
            />
          </div>
          <div v-if="linkPickerLoading" class="picker-empty">
            <div class="picker-empty-icon">⏳</div>
            <div class="picker-empty-text">正在搜索...</div>
          </div>
          <div v-else-if="linkPickerResults.length === 0 && linkPickerQuery" class="picker-empty">
            <div class="picker-empty-icon">🔍</div>
            <div class="picker-empty-text">未找到匹配的笔记</div>
            <div class="picker-empty-hint">试试其他关键词，或在编辑器中直接输入 [[标题]]</div>
          </div>
          <div v-else-if="linkPickerResults.length === 0" class="picker-empty">
            <div class="picker-empty-icon">📝</div>
            <div class="picker-empty-text">输入关键词搜索笔记</div>
            <div class="picker-empty-hint">选中后将以 [[标题]] 格式插入到内容中</div>
          </div>
          <template v-else>
            <div class="picker-count">找到 {{ linkPickerResults.length }} 条笔记</div>
            <div class="picker-list">
              <div
                v-for="item in linkPickerResults"
                :key="item.id"
                class="picker-item"
                @click="selectNoteToLink(item)"
              >
                <div class="picker-item-icon" :class="'source-' + (item.source_type || 'knowledge')">
                  {{ sourceTypeIcon(item.source_type) }}
                </div>
                <div class="picker-item-body">
                  <span class="picker-title">{{ item.title }}</span>
                  <span v-if="item.summary" class="picker-summary">{{ item.summary }}</span>
                  <div class="picker-meta">
                    <span class="picker-source-badge" :class="'source-' + (item.source_type || 'knowledge')">
                      {{ sourceTypeLabel(item.source_type) }}
                    </span>
                    <span class="picker-date">{{ formatDate(item.created_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
        <div class="modal-actions">
          <span></span>
          <button class="btn-cancel" @click="linkPickerOpen = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, inject, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { notesApi, categoriesApi } from '../api'
import MarkdownIt from 'markdown-it'

function wikiLinkPlugin(md, options) {
  const linkMap = options.linkMap || {}
  md.inline.ruler.push('wiki_link', function (state, silent) {
    const start = state.pos
    if (state.src.charCodeAt(start) !== 0x5B) return false
    if (state.src.charCodeAt(start + 1) !== 0x5B) return false
    let pos = start + 2
    const max = state.posMax
    let depth = 0
    while (pos < max) {
      if (state.src.charCodeAt(pos) === 0x5D) {
        if (depth === 0 && pos + 1 < max && state.src.charCodeAt(pos + 1) === 0x5D) break
        depth--
      } else if (state.src.charCodeAt(pos) === 0x5B) { depth++ }
      pos++
    }
    if (pos >= max) return false
    const title = state.src.slice(start + 2, pos).trim()
    if (!title) return false
    if (!silent) {
      const token = state.push('wiki_link', 'a', 0)
      token.attrSet('href', '#')
      token.attrSet('class', 'wiki-link')
      token.attrSet('data-title', title)
      const targetId = linkMap[title]
      if (targetId) {
        token.attrSet('data-id', String(targetId))
        token.attrSet('class', 'wiki-link resolved')
      }
      token.content = title
    }
    state.pos = pos + 2
    return true
  })
  md.renderer.rules.wiki_link = function (tokens, idx) {
    const token = tokens[idx]
    const title = token.content
    const targetId = token.attrGet('data-id')
    if (targetId) {
      return `<a href="#/notes/${targetId}" class="wiki-link resolved" data-id="${targetId}">${title}</a>`
    }
    return `<span class="wiki-link unresolved">${title}</span>`
  }
}

export default {
  name: 'NoteDetailView',
  setup() {
    const toast = inject('toast')
    const route = useRoute()
    const router = useRouter()
    const note = ref(null)
    const loading = ref(true)
    const researching = ref(false)
    const researchStage = ref('')
    const editing = ref(false)
    const saving = ref(false)
    const toggling = ref(false)
    const categories = ref([])
    const newTag = ref('')
    const links = ref({ backlinks: [], outgoing: [] })
    const contentTextarea = ref(null)
    const pickerSearchInput = ref(null)

    const linkPickerOpen = ref(false)
    const linkPickerQuery = ref('')
    const linkPickerResults = ref([])
    const linkPickerLoading = ref(false)
    let linkPickerTimer = null

    const editForm = ref({
      title: '', summary: '', organized_content: '',
      source_type: '', category_id: null, tags: [],
    })

    const sourceTypes = {
      life: '生活', thought: '感想', knowledge: '知识',
      todo: '待办', idea: '灵感', work: '工作'
    }
    const sourceTypeLabel = (type) => sourceTypes[type] || type || '未分类'
    const sourceTypeIcons = {
      life: '🌿', thought: '💭', knowledge: '📚',
      todo: '✅', idea: '💡', work: '💼'
    }
    const sourceTypeIcon = (type) => sourceTypeIcons[type] || '📄'

    const renderMarkdown = (content) => {
      if (!content) return ''
      const linkMap = {}
      for (const ol of links.value.outgoing) { linkMap[ol.title] = ol.id }
      const localMd = new MarkdownIt({ html: false, linkify: true, breaks: true })
      localMd.use(wikiLinkPlugin, { linkMap })
      return localMd.render(content)
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString('zh-CN')
    }

    const scrollToSection = (id) => {
      const el = document.getElementById(id)
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }

    const loadNote = async () => {
      loading.value = true
      try {
        const res = await notesApi.get(route.params.id)
        note.value = res.data
        loadLinks()
      } catch (e) { note.value = null }
      finally { loading.value = false }
    }

    const loadLinks = async () => {
      if (!note.value) return
      try {
        const res = await notesApi.links(note.value.id)
        links.value = res.data
      } catch (e) { links.value = { backlinks: [], outgoing: [] } }
    }

    const loadCategories = async () => {
      try {
        const res = await categoriesApi.list()
        categories.value = res.data
      } catch (e) { categories.value = [] }
    }

    const startEdit = () => {
      editForm.value = {
        title: note.value.title || '', summary: note.value.summary || '',
        organized_content: note.value.organized_content || '',
        source_type: note.value.source_type || '',
        category_id: note.value.category_id || null,
        tags: (note.value.tags || []).map(t => t.name),
      }
      newTag.value = ''
      editing.value = true
      loadCategories()
    }

    const cancelEdit = () => { editing.value = false }

    const addTag = () => {
      const tag = newTag.value.trim()
      if (tag && !editForm.value.tags.includes(tag)) { editForm.value.tags.push(tag) }
      newTag.value = ''
    }

    const saveEdit = async () => {
      if (!editForm.value.title.trim()) { toast('标题不能为空', 'error'); return }
      saving.value = true
      try {
        const data = {
          title: editForm.value.title, summary: editForm.value.summary,
          organized_content: editForm.value.organized_content,
          source_type: editForm.value.source_type || null,
          category_id: editForm.value.category_id, tags: editForm.value.tags,
        }
        const res = await notesApi.update(note.value.id, data)
        note.value = res.data
        editing.value = false
        loadLinks()
        toast('保存成功', 'success', 3000)
      } catch (e) { toast('保存失败: ' + (e.response?.data?.detail || e.message), 'error') }
      finally { saving.value = false }
    }

    const searchNotesForLink = () => {
      if (linkPickerTimer) clearTimeout(linkPickerTimer)
      if (!linkPickerQuery.value.trim()) { linkPickerResults.value = []; return }
      linkPickerTimer = setTimeout(async () => {
        linkPickerLoading.value = true
        try {
          const res = await notesApi.list({ keyword: linkPickerQuery.value, limit: 20 })
          linkPickerResults.value = (res.data.notes || []).filter(n => n.id !== note.value.id)
        } catch (e) { linkPickerResults.value = [] }
        finally { linkPickerLoading.value = false }
      }, 300)
    }

    const openLinkPicker = () => {
      linkPickerQuery.value = ''
      linkPickerResults.value = []
      linkPickerOpen.value = true
      nextTick(() => { pickerSearchInput.value?.focus() })
    }

    const selectNoteToLink = (item) => {
      const wikiLink = `[[${item.title}]]`
      const textarea = contentTextarea.value
      if (textarea) {
        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        const content = editForm.value.organized_content
        editForm.value.organized_content = content.slice(0, start) + wikiLink + content.slice(end)
        const newPos = start + wikiLink.length
        setTimeout(() => { textarea.focus(); textarea.setSelectionRange(newPos, newPos) }, 0)
      } else {
        editForm.value.organized_content += '\n' + wikiLink
      }
      linkPickerOpen.value = false
    }

    const doResearch = async () => {
      researching.value = true
      researchStage.value = '正在准备...'
      try {
        const token = localStorage.getItem('token')
        const response = await fetch('/api/ai/research', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ note_id: note.value.id }),
        })
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                if (data.stage === 'complete') { note.value.research_content = data.research_content; toast('调研完成') }
                else if (data.stage === 'error') { toast('调研失败: ' + data.message, 'error') }
                else { researchStage.value = data.message }
              } catch (e) { /* ignore */ }
            }
          }
        }
      } catch (e) { toast('调研失败: ' + e.message, 'error') }
      finally { researching.value = false; researchStage.value = '' }
    }

    const handleStar = async () => {
      toggling.value = true
      try { const res = await notesApi.toggleStar(note.value.id); note.value = res.data; toast(note.value.is_starred ? '已收藏' : '已取消收藏') }
      catch (e) { toast('操作失败', 'error') }
      finally { toggling.value = false }
    }

    const handlePin = async () => {
      toggling.value = true
      try { const res = await notesApi.togglePin(note.value.id); note.value = res.data; toast(note.value.is_pinned ? '已置顶' : '已取消置顶') }
      catch (e) { toast('操作失败', 'error') }
      finally { toggling.value = false }
    }

    const removeNote = async () => {
      if (!confirm('确定删除此笔记？将移至回收站')) return
      try { await notesApi.delete(note.value.id); toast('已移至回收站'); router.push('/') }
      catch (e) { toast('删除失败', 'error') }
    }

    onMounted(() => { loadNote() })
    onUnmounted(() => {})
    watch(() => route.params.id, (newId) => { if (newId) loadNote() })

    return {
      note, loading, researching, researchStage, editing, saving, toggling, categories, newTag, editForm, links,
      contentTextarea, pickerSearchInput,
      linkPickerOpen, linkPickerQuery, linkPickerResults, linkPickerLoading,
      sourceTypes, sourceTypeLabel, sourceTypeIcon, renderMarkdown, formatDate, scrollToSection,
      startEdit, cancelEdit, addTag, saveEdit,
      openLinkPicker, searchNotesForLink, selectNoteToLink,
      handleStar, handlePin, doResearch, removeNote,
    }
  },
}
</script>
