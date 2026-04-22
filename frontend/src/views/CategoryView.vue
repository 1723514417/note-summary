<template>
  <div>
    <h1 class="page-title">分类浏览</h1>

    <div class="card mb-16">
      <div class="flex-between">
        <div class="flex-row">
          <input
            type="text"
            v-model="newCategoryName"
            placeholder="新分类名称"
            style="width: 200px"
          />
          <button class="btn btn-primary btn-sm" @click="addCategory" :disabled="!newCategoryName.trim()">
            + 新增分类
          </button>
        </div>
      </div>
    </div>

    <div v-if="loadingCategories" class="loading">加载中...</div>
    <div v-else-if="categories.length === 0" class="empty-state">
      <h3>暂无分类</h3>
      <p>添加第一个分类来组织你的知识吧</p>
    </div>
    <div v-else>
      <div v-for="cat in categories" :key="cat.id" class="card">
        <div class="flex-between mb-8">
          <h3 style="font-size: 16px; cursor: pointer" @click="loadCategoryNotes(cat.id)">
            📁 {{ cat.name }}
            <span v-if="cat.description" style="font-weight: normal; color: var(--text-secondary); font-size: 13px">
              - {{ cat.description }}
            </span>
          </h3>
          <button class="btn btn-danger btn-sm" @click="removeCategory(cat.id, cat.name)">删除</button>
        </div>
        <div v-if="cat.children && cat.children.length">
          <div v-for="child in cat.children" :key="child.id" style="margin-left: 20px; padding: 8px 0; border-bottom: 1px solid var(--border)">
            <span style="cursor: pointer" @click="loadCategoryNotes(child.id)">
              📂 {{ child.name }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedNotes.length" style="margin-top: 20px">
      <h2 style="font-size: 18px; margin-bottom: 12px">分类下的笔记</h2>
      <div
        v-for="note in selectedNotes"
        :key="note.id"
        class="note-list-item"
        @click="$router.push(`/notes/${note.id}`)"
      >
        <div class="note-title">{{ note.title }}</div>
        <div class="note-summary">{{ note.summary }}</div>
        <div class="note-meta">
          <span class="note-date">{{ formatDate(note.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, inject, onMounted } from 'vue'
import { categoriesApi, notesApi } from '../api'

export default {
  name: 'CategoryView',
  setup() {
    const toast = inject('toast')
    const categories = ref([])
    const loadingCategories = ref(false)
    const newCategoryName = ref('')
    const selectedNotes = ref([])

    const loadCategories = async () => {
      loadingCategories.value = true
      try {
        const res = await categoriesApi.list()
        categories.value = res.data
      } catch (e) {
        console.error(e)
      } finally {
        loadingCategories.value = false
      }
    }

    const addCategory = async () => {
      if (!newCategoryName.value.trim()) return
      try {
        await categoriesApi.create({ name: newCategoryName.value })
        newCategoryName.value = ''
        toast('分类创建成功')
        loadCategories()
      } catch (e) {
        toast('创建失败: ' + (e.response?.data?.detail || e.message), 'error')
      }
    }

    const removeCategory = async (id, name) => {
      if (!confirm(`确定删除分类「${name}」及其下所有笔记？`)) return
      try {
        let res = await notesApi.list({ category_id: id, limit: 1000 })
        const notes = res.data.notes || []
        for (const note of notes) {
          await notesApi.delete(note.id)
        }
        await categoriesApi.delete(id)
        selectedNotes.value = []
        toast(`已删除分类「${name}」及 ${notes.length} 条笔记`)
        loadCategories()
      } catch (e) {
        toast('删除失败', 'error')
      }
    }

    const loadCategoryNotes = async (categoryId) => {
      try {
        const res = await notesApi.list({ category_id: categoryId, limit: 50 })
        selectedNotes.value = res.data.notes || []
      } catch (e) {
        console.error(e)
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString('zh-CN')
    }

    onMounted(loadCategories)

    return {
      categories, loadingCategories, newCategoryName, selectedNotes,
      addCategory, removeCategory, loadCategoryNotes, formatDate,
    }
  },
}
</script>
