<template>
  <div>
    <h1 class="page-title">搜索知识库</h1>

    <div class="card mb-16">
      <div class="flex-row">
        <input
          type="search"
          v-model="query"
          placeholder="输入关键词或自然语言描述来搜索..."
          @keyup.enter="doSearch"
          style="flex: 1"
        />
        <select v-model="searchMode" class="btn btn-secondary">
          <option value="hybrid">混合搜索</option>
          <option value="fts">关键词搜索</option>
          <option value="semantic">语义搜索</option>
        </select>
        <button class="btn btn-primary" @click="doSearch" :disabled="!query.trim() || loading">
          🔍 搜索
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">搜索中...</div>
    <div v-else-if="searched">
      <p class="mb-16" style="color: var(--text-secondary)">
        找到 {{ total }} 条结果
      </p>
      <div v-if="results.length === 0" class="empty-state">
        <h3>没有找到相关内容</h3>
        <p>试试换个关键词搜索</p>
      </div>
      <div
        v-for="note in results"
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
import { ref } from 'vue'
import { searchApi } from '../api'

export default {
  name: 'SearchView',
  setup() {
    const query = ref('')
    const searchMode = ref('hybrid')
    const loading = ref(false)
    const searched = ref(false)
    const results = ref([])
    const total = ref(0)

    const sourceTypes = {
      life: '生活', thought: '感想', knowledge: '知识',
      todo: '待办', idea: '灵感', work: '工作'
    }

    const sourceTypeLabel = (type) => sourceTypes[type] || type || '未分类'

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString('zh-CN')
    }

    const doSearch = async () => {
      if (!query.value.trim()) return
      loading.value = true
      searched.value = true
      try {
        const res = await searchApi.search({
          q: query.value,
          mode: searchMode.value,
          limit: 20,
        })
        results.value = res.data.notes || []
        total.value = res.data.total || 0
      } catch (e) {
        console.error(e)
        results.value = []
        total.value = 0
      } finally {
        loading.value = false
      }
    }

    return {
      query, searchMode, loading, searched, results, total,
      sourceTypeLabel, formatDate, doSearch,
    }
  },
}
</script>
