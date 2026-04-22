<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-brand">📝 <span class="nav-text">Note Summary</span></div>
      <ul class="sidebar-nav">
        <li>
          <router-link to="/" exact-active-class="router-link-active">
            <span>✏️</span><span class="nav-text"> 记录</span>
          </router-link>
        </li>
        <li>
          <router-link to="/search" active-class="router-link-active">
            <span>🔍</span><span class="nav-text"> 搜索</span>
          </router-link>
        </li>
        <li>
          <router-link to="/categories" active-class="router-link-active">
            <span>📁</span><span class="nav-text"> 分类</span>
          </router-link>
        </li>
      </ul>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
    <div class="toast-container">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="toast"
        :class="'toast-' + t.type"
      >
        {{ t.message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, provide } from 'vue'

let toastId = 0

export default {
  name: 'App',
  setup() {
    const toasts = ref([])

    const showToast = (message, type = 'success', duration = 2500) => {
      const id = ++toastId
      toasts.value.push({ id, message, type })
      setTimeout(() => {
        toasts.value = toasts.value.filter(t => t.id !== id)
      }, duration)
    }

    provide('toast', showToast)

    return { toasts }
  },
}
</script>
