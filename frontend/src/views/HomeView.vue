<template>
  <div>
    <h1 class="page-title">{{ isStarred ? '⭐ 已收藏' : '记录新内容' }}</h1>

    <template v-if="!isStarred">
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
              <button class="btn btn-secondary" @click="homeLinkPickerOpen = true">🔗 关联</button>
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
    </template>

    <h2 class="page-title" style="font-size: 18px; margin-top: 24px">
      {{ isStarred ? '' : '最近记录' }}
    </h2>
    <div v-if="loadingNotes" class="loading">加载中...</div>
    <div v-else-if="recentNotes.length === 0" class="empty-state">
      <h3>{{ isStarred ? '暂无收藏' : '还没有记录' }}</h3>
      <p>{{ isStarred ? '点击笔记详情中的⭐即可收藏' : '在上方输入内容，开始构建你的个人知识库吧！' }}</p>
    </div>
    <div v-else>
      <div
        v-for="note in recentNotes"
        :key="note.id"
        class="note-list-item"
        @click="$router.push(`/notes/${note.id}`)"
      >
        <div class="note-title">
          <span v-if="note.is_pinned" class="note-badge pin-badge" title="已置顶">📌</span>
          <span v-if="note.is_starred" class="note-badge star-badge" title="已收藏">⭐</span>
          {{ note.title }}
        </div>
        <div class="note-summary">{{ note.summary }}</div>
        <div class="note-meta">
          <span class="source-type" :class="'source-' + note.source_type">{{ sourceTypeLabel(note.source_type) }}</span>
          <span class="note-date">{{ formatDate(note.created_at) }}</span>
        </div>
      </div>
    </div>

    <div v-if="homeLinkPickerOpen" class="modal-overlay" @click.self="homeLinkPickerOpen = false" @keydown.esc="homeLinkPickerOpen = false">
      <div class="modal-card modal-card--picker">
        <h3>
          <span style="font-size: 18px">🔗</span>
          选择要关联的笔记
        </h3>
        <div class="modal-body">
          <div class="picker-search-wrap">
            <span class="picker-search-icon">🔍</span>
            <input
              v-model="homeLinkQuery"
              class="form-input"
              placeholder="搜索笔记标题或内容..."
              @input="searchForHomeLink"
              autofocus
            />
          </div>
          <div v-if="homeLinkLoading" class="picker-empty">
            <div class="picker-empty-icon">⏳</div>
            <div class="picker-empty-text">正在搜索...</div>
          </div>
          <div v-else-if="homeLinkResults.length === 0 && homeLinkQuery" class="picker-empty">
            <div class="picker-empty-icon">🔍</div>
            <div class="picker-empty-text">未找到匹配的笔记</div>
            <div class="picker-empty-hint">试试其他关键词</div>
          </div>
          <div v-else-if="homeLinkResults.length === 0" class="picker-empty">
            <div class="picker-empty-icon">📝</div>
            <div class="picker-empty-text">输入关键词搜索笔记</div>
            <div class="picker-empty-hint">选中后将以 [[标题]] 格式插入到内容中</div>
          </div>
          <template v-else>
            <div class="picker-count">找到 {{ homeLinkResults.length }} 条笔记</div>
            <div class="picker-list">
              <div
                v-for="item in homeLinkResults"
                :key="item.id"
                class="picker-item"
                @click="selectHomeLink(item)"
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
          <div class="picker-footer-hint">
            <kbd>Esc</kbd> 关闭 &nbsp;·&nbsp; 点击笔记插入链接
          </div>
          <button class="btn-cancel" @click="homeLinkPickerOpen = false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, inject, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { notesApi, aiApi } from '../api'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()

export default {
  name: 'HomeView',
  setup() {
    const toast = inject('toast')
    const route = useRoute()
    const rawContent = ref('')
    const sourceType = ref('')
    const loading = ref(false)
    const loadingNotes = ref(false)
    const preview = ref(null)
    const recentNotes = ref([])
    const homeLinkPickerOpen = ref(false)
    const homeLinkQuery = ref('')
    const homeLinkResults = ref([])
    const homeLinkLoading = ref(false)
    let homeLinkTimer = null

    const isStarred = computed(() => route.query.starred === 'true')

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
        const params = isStarred.value
          ? { starred: true, limit: 50 }
          : { limit: 10 }
        const res = await notesApi.list(params)
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
        toast('AI 整理失败: ' + (e.response?.data?.detail || e.message), 'error')
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
        toast('保存成功！', 'success', 3000)
        loadRecentNotes()
      } catch (e) {
        toast('保存失败: ' + (e.response?.data?.detail || e.message), 'error')
      } finally {
        loading.value = false
      }
    }

    onMounted(loadRecentNotes)
    watch(() => route.query.starred, loadRecentNotes)

    const searchForHomeLink = () => {
      if (homeLinkTimer) clearTimeout(homeLinkTimer)
      if (!homeLinkQuery.value.trim()) {
        homeLinkResults.value = []
        return
      }
      homeLinkTimer = setTimeout(async () => {
        homeLinkLoading.value = true
        try {
          const res = await notesApi.list({ keyword: homeLinkQuery.value, limit: 20 })
          homeLinkResults.value = res.data.notes || []
        } catch (e) {
          homeLinkResults.value = []
        } finally {
          homeLinkLoading.value = false
        }
      }, 300)
    }

    const selectHomeLink = (item) => {
      const wikiLink = `[[${item.title}]]`
      rawContent.value += (rawContent.value ? '\n' : '') + wikiLink
      homeLinkPickerOpen.value = false
      toast(`已添加关联：${item.title}`)
    }

    return {
      rawContent, sourceType, loading, loadingNotes, preview, recentNotes,
      isStarred, sourceTypeLabel, sourceTypeIcon, renderMarkdown, formatDate, previewOrganize, submitNote,
      homeLinkPickerOpen, homeLinkQuery, homeLinkResults, homeLinkLoading,
      searchForHomeLink, selectHomeLink,
    }
  },
}
</script>
