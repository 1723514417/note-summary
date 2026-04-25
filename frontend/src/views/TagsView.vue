<template>
  <div>
    <div class="flex-between mb-16">
      <h1 class="page-title">🏷️ 标签管理</h1>
      <span style="font-size: 13px; color: var(--text-secondary)">共 {{ tags.length }} 个标签</span>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="tags.length === 0" class="empty-state">
      <h3>暂无标签</h3>
      <p style="margin-top: 8px; color: var(--text-secondary)">创建笔记时 AI 会自动生成标签</p>
    </div>

    <template v-else>
      <div class="tag-grid">
        <div
          v-for="tag in tags"
          :key="tag.id"
          class="tag-manage-item"
        >
          <span class="tag-manage-name">{{ tag.name }}</span>
          <div class="tag-manage-actions">
            <button class="btn btn-secondary btn-sm" @click="startRename(tag)">重命名</button>
            <button class="btn btn-danger btn-sm" @click="handleDelete(tag)">删除</button>
          </div>
        </div>
      </div>

      <div v-if="renaming" class="modal-overlay" @click.self="renaming = null">
        <div class="modal-card">
          <h3>重命名标签</h3>
          <div class="form-group">
            <input v-model="renameName" class="form-input" @keydown.enter="doRename" />
          </div>
          <div class="modal-actions">
            <button class="btn-cancel" @click="renaming = null">取消</button>
            <button class="btn-confirm" @click="doRename">确认</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, inject, onMounted } from 'vue'
import { tagsApi } from '../api'

export default {
  name: 'TagsView',
  setup() {
    const toast = inject('toast')
    const tags = ref([])
    const loading = ref(true)
    const renaming = ref(null)
    const renameName = ref('')

    const loadTags = async () => {
      loading.value = true
      try {
        const res = await tagsApi.list()
        tags.value = res.data
      } catch (e) {
        toast('加载失败', 'error')
      } finally {
        loading.value = false
      }
    }

    const startRename = (tag) => {
      renaming.value = tag
      renameName.value = tag.name
    }

    const doRename = async () => {
      if (!renameName.value.trim()) { toast('标签名不能为空', 'error'); return }
      try {
        await tagsApi.rename(renaming.value.id, { name: renameName.value.trim() })
        toast('重命名成功')
        renaming.value = null
        loadTags()
      } catch (e) {
        toast(e.response?.data?.detail || '重命名失败', 'error')
      }
    }

    const handleDelete = async (tag) => {
      if (!confirm(`确定删除标签「${tag.name}」？将从所有笔记中移除此标签。`)) return
      try {
        await tagsApi.delete(tag.id)
        toast('已删除标签')
        loadTags()
      } catch (e) {
        toast('删除失败', 'error')
      }
    }

    onMounted(loadTags)

    return { tags, loading, renaming, renameName, startRename, doRename, handleDelete }
  },
}
</script>
