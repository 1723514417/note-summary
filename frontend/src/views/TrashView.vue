<template>
  <div>
    <div class="flex-between mb-16">
      <h1 class="page-title">🗑️ 回收站</h1>
      <span v-if="total > 0" class="trash-hint">30天后自动清理</span>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="notes.length === 0" class="empty-state">
      <h3>回收站为空</h3>
      <p style="margin-top: 8px">删除的笔记会暂存在这里</p>
    </div>

    <div v-else>
      <div
        v-for="note in notes"
        :key="note.id"
        class="note-list-item trash-item"
      >
        <div class="flex-between">
          <div class="note-title">{{ note.title }}</div>
          <div class="trash-actions">
            <button class="btn btn-primary btn-sm" @click="handleRestore(note.id)">恢复</button>
            <button class="btn btn-danger btn-sm" @click="handlePermanentDelete(note.id, note.title)">彻底删除</button>
          </div>
        </div>
        <div v-if="note.summary" class="note-summary">{{ note.summary }}</div>
        <div class="note-meta">
          <span v-if="note.source_type" class="source-type" :class="'source-' + note.source_type">{{ sourceTypeLabel(note.source_type) }}</span>
          <span class="tag" v-for="tag in note.tags" :key="tag.id">{{ tag.name }}</span>
          <span class="note-date">删除于 {{ formatDate(note.deleted_at) }}</span>
          <span class="note-date">创建于 {{ formatDate(note.created_at) }}</span>
        </div>
      </div>

      <div v-if="hasMore" class="load-more">
        <button class="btn btn-secondary" @click="loadMore" :disabled="loadingMore">
          {{ loadingMore ? '加载中...' : '加载更多' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, inject, onMounted } from 'vue'
import { notesApi } from '../api'

export default {
  name: 'TrashView',
  setup() {
    const toast = inject('toast')
    const notes = ref([])
    const total = ref(0)
    const loading = ref(true)
    const loadingMore = ref(false)
    const skip = ref(0)
    const limit = 20
    const hasMore = ref(false)

    const sourceTypes = {
      life: '生活', thought: '感想', knowledge: '知识',
      todo: '待办', idea: '灵感', work: '工作'
    }

    const sourceTypeLabel = (type) => sourceTypes[type] || type || '未分类'

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString('zh-CN')
    }

    const loadTrash = async (append = false) => {
      if (!append) loading.value = true
      else loadingMore.value = true

      try {
        const res = await notesApi.trashList({ skip: skip.value, limit })
        if (append) {
          notes.value = [...notes.value, ...res.data.notes]
        } else {
          notes.value = res.data.notes
        }
        total.value = res.data.total
        hasMore.value = notes.value.length < total.value
      } catch (e) {
        toast('加载失败', 'error')
      } finally {
        loading.value = false
        loadingMore.value = false
      }
    }

    const loadMore = () => {
      skip.value += limit
      loadTrash(true)
    }

    const handleRestore = async (id) => {
      try {
        await notesApi.restore(id)
        toast('已恢复笔记')
        notes.value = notes.value.filter(n => n.id !== id)
        total.value--
        hasMore.value = notes.value.length < total.value
      } catch (e) {
        toast('恢复失败', 'error')
      }
    }

    const handlePermanentDelete = async (id, title) => {
      if (!confirm(`确定彻底删除「${title}」？此操作不可恢复！`)) return
      try {
        await notesApi.permanentDelete(id)
        toast('已彻底删除')
        notes.value = notes.value.filter(n => n.id !== id)
        total.value--
      } catch (e) {
        toast('删除失败', 'error')
      }
    }

    onMounted(() => loadTrash())

    return {
      notes, total, loading, loadingMore, hasMore,
      sourceTypeLabel, formatDate,
      loadMore, handleRestore, handlePermanentDelete,
    }
  },
}
</script>
