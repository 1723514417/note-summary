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
            <button class="btn btn-secondary btn-sm" @click="cancelEdit">取消</button>
            <button class="btn btn-primary btn-sm" @click="saveEdit" :disabled="saving">
              {{ saving ? '保存中...' : '💾 保存' }}
            </button>
          </template>
        </div>
      </div>

      <div class="card">
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

        <template v-if="!editing">
          <div v-if="note.organized_content" class="markdown-content" v-html="renderMarkdown(note.organized_content)"></div>
        </template>
        <template v-else>
          <label style="font-size: 13px; font-weight: 500; color: var(--text-label); display: block; margin-bottom: 6px">整理内容（Markdown）</label>
          <textarea v-model="editForm.organized_content" rows="15" style="min-height: 300px; font-family: monospace; font-size: 13px; line-height: 1.6"></textarea>
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

      <div v-if="!editing && researching" class="card mt-16">
        <h3 style="margin-bottom: 12px">🔬 AI 调研中...</h3>
        <div class="loading" style="padding: 20px">正在生成调研内容，请稍候...</div>
      </div>

      <div v-else-if="!editing && note.research_content" class="card mt-16">
        <h3 style="margin-bottom: 12px">🔬 AI 调研结果</h3>
        <div class="markdown-content" v-html="renderMarkdown(note.research_content)"></div>
      </div>

      <div v-if="!editing" class="card mt-16">
        <div v-if="links.backlinks.length > 0 || links.outgoing.length > 0">
          <h3 style="margin-bottom: 12px; font-size: 16px">🔗 笔记关联</h3>

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
          🔗 暂无关联笔记。在内容中使用 <code style="background: var(--tag-bg); padding: 2px 6px; border-radius: 4px">[[笔记标题]]</code> 可建立笔记间的链接。
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, inject, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { notesApi, categoriesApi, aiApi } from '../api'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({ html: false, linkify: true, breaks: true })

function wikiLinkPlugin(md, options) {
  const linkMap = options.linkMap || {}
  md.inline.ruler.push('wiki_link', function (state, silent) {
    const start = state.pos
    if (state.src.charCodeAt(start) !== 0x5B /* [ */) return false
    if (state.src.charCodeAt(start + 1) !== 0x5B /* [ */) return false

    let pos = start + 2
    const max = state.posMax
    let depth = 0
    while (pos < max) {
      if (state.src.charCodeAt(pos) === 0x5D /* ] */) {
        if (depth === 0 && pos + 1 < max && state.src.charCodeAt(pos + 1) === 0x5D) {
          break
        }
        depth--
      } else if (state.src.charCodeAt(pos) === 0x5B) {
        depth++
      }
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
    const editing = ref(false)
    const saving = ref(false)
    const toggling = ref(false)
    const categories = ref([])
    const newTag = ref('')
    const links = ref({ backlinks: [], outgoing: [] })

    const editForm = ref({
      title: '',
      summary: '',
      organized_content: '',
      source_type: '',
      category_id: null,
      tags: [],
    })

    const sourceTypes = {
      life: '生活', thought: '感想', knowledge: '知识',
      todo: '待办', idea: '灵感', work: '工作'
    }

    const sourceTypeLabel = (type) => sourceTypes[type] || type || '未分类'

    const renderMarkdown = (content) => {
      if (!content) return ''
      const linkMap = {}
      for (const ol of links.value.outgoing) {
        linkMap[ol.title] = ol.id
      }
      const localMd = new MarkdownIt({ html: false, linkify: true, breaks: true })
      localMd.use(wikiLinkPlugin, { linkMap })
      return localMd.render(content)
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString('zh-CN')
    }

    const loadNote = async () => {
      loading.value = true
      try {
        const res = await notesApi.get(route.params.id)
        note.value = res.data
        loadLinks()
      } catch (e) {
        note.value = null
      } finally {
        loading.value = false
      }
    }

    const loadLinks = async () => {
      if (!note.value) return
      try {
        const res = await notesApi.links(note.value.id)
        links.value = res.data
      } catch (e) {
        links.value = { backlinks: [], outgoing: [] }
      }
    }

    const loadCategories = async () => {
      try {
        const res = await categoriesApi.list()
        categories.value = res.data
      } catch (e) {
        categories.value = []
      }
    }

    const startEdit = () => {
      editForm.value = {
        title: note.value.title || '',
        summary: note.value.summary || '',
        organized_content: note.value.organized_content || '',
        source_type: note.value.source_type || '',
        category_id: note.value.category_id || null,
        tags: (note.value.tags || []).map(t => t.name),
      }
      newTag.value = ''
      editing.value = true
      loadCategories()
    }

    const cancelEdit = () => {
      editing.value = false
    }

    const addTag = () => {
      const tag = newTag.value.trim()
      if (tag && !editForm.value.tags.includes(tag)) {
        editForm.value.tags.push(tag)
      }
      newTag.value = ''
    }

    const saveEdit = async () => {
      if (!editForm.value.title.trim()) {
        toast('标题不能为空', 'error')
        return
      }
      saving.value = true
      try {
        const data = {
          title: editForm.value.title,
          summary: editForm.value.summary,
          organized_content: editForm.value.organized_content,
          source_type: editForm.value.source_type || null,
          category_id: editForm.value.category_id,
          tags: editForm.value.tags,
        }
        const res = await notesApi.update(note.value.id, data)
        note.value = res.data
        editing.value = false
        loadLinks()
        toast('保存成功', 'success', 3000)
      } catch (e) {
        toast('保存失败: ' + (e.response?.data?.detail || e.message), 'error')
      } finally {
        saving.value = false
      }
    }

    const doResearch = async () => {
      researching.value = true
      try {
        const res = await aiApi.research({ note_id: note.value.id })
        note.value.research_content = res.data.research_content
      } catch (e) {
        alert('调研失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        researching.value = false
      }
    }

    const handleStar = async () => {
      toggling.value = true
      try {
        const res = await notesApi.toggleStar(note.value.id)
        note.value = res.data
        toast(note.value.is_starred ? '已收藏' : '已取消收藏')
      } catch (e) {
        toast('操作失败', 'error')
      } finally {
        toggling.value = false
      }
    }

    const handlePin = async () => {
      toggling.value = true
      try {
        const res = await notesApi.togglePin(note.value.id)
        note.value = res.data
        toast(note.value.is_pinned ? '已置顶' : '已取消置顶')
      } catch (e) {
        toast('操作失败', 'error')
      } finally {
        toggling.value = false
      }
    }

    const removeNote = async () => {
      if (!confirm('确定删除此笔记？将移至回收站')) return
      try {
        await notesApi.delete(note.value.id)
        toast('已移至回收站')
        router.push('/')
      } catch (e) {
        toast('删除失败', 'error')
      }
    }

    onMounted(loadNote)
    watch(() => route.params.id, (newId) => {
      if (newId) loadNote()
    })

    return {
      note, loading, researching, editing, saving, toggling, categories, newTag, editForm, links,
      sourceTypes, sourceTypeLabel, renderMarkdown, formatDate,
      startEdit, cancelEdit, addTag, saveEdit,
      handleStar, handlePin, doResearch, removeNote,
    }
  },
}
</script>
