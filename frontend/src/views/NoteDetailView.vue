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
        </div>
      </div>

      <div class="card">
        <div class="flex-row mb-8" style="flex-wrap: wrap">
          <span class="source-type" :class="'source-' + note.source_type">{{ sourceTypeLabel(note.source_type) }}</span>
          <span class="tag" v-for="tag in note.tags" :key="tag.id">{{ tag.name }}</span>
          <span class="note-date">{{ formatDate(note.created_at) }}</span>
        </div>

        <h1 style="font-size: 22px; margin-bottom: 12px">{{ note.title }}</h1>

        <div v-if="note.summary" style="background: #f8fafc; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid var(--primary)">
          <strong>摘要：</strong>{{ note.summary }}
        </div>

        <div v-if="note.organized_content" class="markdown-content" v-html="renderMarkdown(note.organized_content)"></div>

        <details style="margin-top: 20px">
          <summary style="cursor: pointer; color: var(--text-secondary); font-size: 14px">
            查看原始输入
          </summary>
          <div style="margin-top: 8px; padding: 12px; background: #f8fafc; border-radius: 8px; white-space: pre-wrap; font-size: 14px">
            {{ note.raw_content }}
          </div>
        </details>
      </div>

      <div v-if="researching" class="card mt-16">
        <h3 style="margin-bottom: 12px">🔬 AI 调研中...</h3>
        <div class="loading" style="padding: 20px">正在生成调研内容，请稍候...</div>
      </div>

      <div v-else-if="note.research_content" class="card mt-16">
        <h3 style="margin-bottom: 12px">🔬 AI 调研结果</h3>
        <div class="markdown-content" v-html="renderMarkdown(note.research_content)"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, inject, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { notesApi, aiApi } from '../api'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()

export default {
  name: 'NoteDetailView',
  setup() {
    const toast = inject('toast')
    const route = useRoute()
    const router = useRouter()
    const note = ref(null)
    const loading = ref(true)
    const researching = ref(false)

    const sourceTypes = {
      life: '生活', thought: '感想', knowledge: '知识',
      todo: '待办', idea: '灵感', work: '工作'
    }

    const sourceTypeLabel = (type) => sourceTypes[type] || type || '未分类'

    const renderMarkdown = (content) => content ? md.render(content) : ''

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString('zh-CN')
    }

    const loadNote = async () => {
      loading.value = true
      try {
        const res = await notesApi.get(route.params.id)
        note.value = res.data
      } catch (e) {
        note.value = null
      } finally {
        loading.value = false
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

    const removeNote = async () => {
      if (!confirm('确定删除此笔记？')) return
      try {
        await notesApi.delete(note.value.id)
        toast('删除成功')
        router.push('/')
      } catch (e) {
        toast('删除失败', 'error')
      }
    }

    onMounted(loadNote)

    return {
      note, loading, researching,
      sourceTypeLabel, renderMarkdown, formatDate, doResearch, removeNote,
    }
  },
}
</script>
