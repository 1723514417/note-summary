<template>
  <div>
    <h1 class="page-title">记录新内容</h1>

    <div class="card mb-16">
      <div class="input-layout">
        <div class="input-left">
          <textarea
            v-model="rawContent"
            placeholder="在这里输入你想记录的内容...&#10;&#10;可以是生活琐事、个人感想、学到的知识、灵感创意等任何内容。&#10;AI 会自动帮你整理、分类并生成摘要。&#10;&#10;支持 Markdown 格式，右侧可实时预览。"
            rows="12"
          ></textarea>
          <div class="flex-between mt-12">
            <div class="flex-row">
              <select v-model="sourceType" class="btn btn-secondary">
                <option value="">自动识别类型</option>
                <option value="life">生活</option>
                <option value="thought">感想</option>
                <option value="knowledge">知识</option>
                <option value="todo">待办</option>
                <option value="idea">灵感</option>
                <option value="work">工作</option>
              </select>
            </div>
            <div class="flex-row">
              <button class="btn btn-secondary" @click="previewOrganize" :disabled="!rawContent.trim() || loading">
                👁️ 预览整理
              </button>
              <button class="btn btn-primary" @click="submitNote" :disabled="!rawContent.trim() || loading">
                {{ loading ? '⏳ AI 整理中...' : '💾 保存记录' }}
              </button>
            </div>
          </div>
        </div>
        <div class="input-right">
          <div v-if="rawContent.trim()" class="preview-panel">
            <div class="preview-header">实时预览</div>
            <div class="markdown-content preview-body" v-html="renderMarkdown(rawContent)"></div>
          </div>
          <div v-else class="tips-panel">
            <div class="tips-header">💡 使用提示</div>
            <div class="tips-list">
              <div class="tip-item">
                <span class="tip-icon">✍️</span>
                <div>
                  <div class="tip-title">自由输入</div>
                  <div class="tip-desc">输入任意内容，AI 自动整理归类</div>
                </div>
              </div>
              <div class="tip-item">
                <span class="tip-icon">📝</span>
                <div>
                  <div class="tip-title">Markdown 支持</div>
                  <div class="tip-desc">支持标题、列表、代码块等格式</div>
                </div>
              </div>
              <div class="tip-item">
                <span class="tip-icon">🏷️</span>
                <div>
                  <div class="tip-title">智能分类</div>
                  <div class="tip-desc">自动生成标题、摘要、标签和分类</div>
                </div>
              </div>
              <div class="tip-item">
                <span class="tip-icon">🔍</span>
                <div>
                  <div class="tip-title">语义搜索</div>
                  <div class="tip-desc">用自然语言模糊搜索你的知识库</div>
                </div>
              </div>
            </div>
            <div v-if="recentNotes.length > 0" class="tips-stats">
              <div class="stat-item">
                <span class="stat-num">{{ recentNotes.length }}</span>
                <span class="stat-label">条记录</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="preview" class="card mb-16">
      <h3 style="margin-bottom: 12px">📋 AI 整理预览</h3>
      <div class="flex-row mb-8" style="flex-wrap: wrap">
        <span class="source-type" :class="'source-' + preview.source_type">{{ sourceTypeLabel(preview.source_type) }}</span>
        <span class="tag" v-for="tag in preview.suggested_tags" :key="tag">{{ tag }}</span>
      </div>
      <h2 style="margin-bottom: 8px">{{ preview.title }}</h2>
      <p class="note-summary mb-8">{{ preview.summary }}</p>
      <div class="markdown-content" v-html="renderMarkdown(preview.organized_content)"></div>
    </div>

    <h2 class="page-title" style="font-size: 18px; margin-top: 24px">最近记录</h2>
    <div v-if="loadingNotes" class="loading">加载中...</div>
    <div v-else-if="recentNotes.length === 0" class="empty-state">
      <h3>还没有记录</h3>
      <p>在上方输入内容，开始构建你的个人知识库吧！</p>
    </div>
    <div v-else>
      <div
        v-for="note in recentNotes"
        :key="note.id"
        class="note-list-item"
        @click="$router.push(`/notes/${note.id}`)"
      >
        <div class="note-title">{{ note.title }}</div>
        <div class="note-summary">{{ note.summary }}</div>
        <div class="note-meta">
          <span class="source-type" :class="'source-' + note.source_type">{{ sourceTypeLabel(note.source_type) }}</span>
          <span class="note-date">{{ formatDate(note.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { notesApi, aiApi } from '../api'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()

export default {
  name: 'HomeView',
  setup() {
    const rawContent = ref('')
    const sourceType = ref('')
    const loading = ref(false)
    const loadingNotes = ref(false)
    const preview = ref(null)
    const recentNotes = ref([])

    const sourceTypes = {
      life: '生活', thought: '感想', knowledge: '知识',
      todo: '待办', idea: '灵感', work: '工作'
    }

    const sourceTypeLabel = (type) => sourceTypes[type] || type || '未分类'

    const renderMarkdown = (content) => {
      return content ? md.render(content) : ''
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return d.toLocaleString('zh-CN')
    }

    const loadRecentNotes = async () => {
      loadingNotes.value = true
      try {
        const res = await notesApi.list({ limit: 10 })
        recentNotes.value = res.data.notes || []
      } catch (e) {
        console.error(e)
      } finally {
        loadingNotes.value = false
      }
    }

    const previewOrganize = async () => {
      if (!rawContent.value.trim()) return
      loading.value = true
      preview.value = null
      try {
        const res = await aiApi.organize({ raw_content: rawContent.value })
        preview.value = res.data
      } catch (e) {
        alert('AI 整理失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        loading.value = false
      }
    }

    const submitNote = async () => {
      if (!rawContent.value.trim()) return
      loading.value = true
      preview.value = null
      try {
        await notesApi.create({
          raw_content: rawContent.value,
          source_type: sourceType.value || null,
        })
        rawContent.value = ''
        sourceType.value = ''
        alert('保存成功！')
        loadRecentNotes()
      } catch (e) {
        alert('保存失败: ' + (e.response?.data?.detail || e.message))
      } finally {
        loading.value = false
      }
    }

    onMounted(loadRecentNotes)

    return {
      rawContent, sourceType, loading, loadingNotes, preview, recentNotes,
      sourceTypeLabel, renderMarkdown, formatDate, previewOrganize, submitNote,
    }
  },
}
</script>
