<template>
  <div class="app-layout">
    <button class="mobile-menu-btn" @click="sidebarOpen = true">☰</button>
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>
    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="sidebar-brand">📝 <span class="nav-text">Note Summary</span></div>
      <ul class="sidebar-nav">
        <li>
          <router-link to="/" custom v-slot="{ navigate }">
            <a @click="navigate(); sidebarOpen = false" :class="{ 'router-link-active': $route.path === '/' && !$route.query.starred }">
              <span>✏️</span><span class="nav-text"> 记录</span>
            </a>
          </router-link>
        </li>
        <li>
          <router-link to="/search" active-class="router-link-active" @click="sidebarOpen = false">
            <span>🔍</span><span class="nav-text"> 搜索</span>
          </router-link>
        </li>
        <li>
          <router-link to="/categories" active-class="router-link-active" @click="sidebarOpen = false">
            <span>📁</span><span class="nav-text"> 分类</span>
          </router-link>
        </li>
        <li>
          <router-link to="/tags" active-class="router-link-active" @click="sidebarOpen = false">
            <span>🏷️</span><span class="nav-text"> 标签</span>
          </router-link>
        </li>
        <li>
          <router-link to="/stats" active-class="router-link-active" @click="sidebarOpen = false">
            <span>📊</span><span class="nav-text"> 统计</span>
          </router-link>
        </li>
        <li>
          <router-link to="/?starred=true" custom v-slot="{ navigate }">
            <a @click="navigate(); sidebarOpen = false" :class="{ 'router-link-active': $route.query.starred === 'true' }">
              <span>⭐</span><span class="nav-text"> 已收藏</span>
            </a>
          </router-link>
        </li>
        <li>
          <router-link to="/trash" active-class="router-link-active" class="trash-link" @click="sidebarOpen = false">
            <span>🗑️</span><span class="nav-text"> 回收站</span>
            <span v-if="trashCount > 0" class="trash-badge">{{ trashCount }}</span>
          </router-link>
        </li>
      </ul>
      <div class="sidebar-footer">
        <div class="user-info">
          <span class="user-icon">👤</span>
          <span class="nav-text user-name">{{ username }}</span>
        </div>
        <button class="theme-btn" @click="toggleTheme" :title="isDark ? '切换亮色模式' : '切换暗色模式'">
          <span>{{ isDark ? '☀️' : '🌙' }}</span>
          <span class="nav-text">{{ isDark ? ' 亮色' : ' 暗色' }}</span>
        </button>
        <button class="logout-btn" @click="showPasswordModal = true" title="修改密码">
          <span>🔑</span>
          <span class="nav-text"> 改密</span>
        </button>
        <button class="logout-btn" @click="handleLogout" title="退出登录">
          <span>🚪</span>
          <span class="nav-text"> 退出</span>
        </button>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>

    <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
      <div class="modal-card">
        <h3>修改密码</h3>
        <form @submit.prevent="handleChangePassword">
          <div class="form-group">
            <label>原密码</label>
            <input v-model="pwdForm.old_password" type="password" required placeholder="请输入原密码" />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input v-model="pwdForm.new_password" type="password" required placeholder="请输入新密码（至少6位）" />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input v-model="pwdForm.confirm_password" type="password" required placeholder="请再次输入新密码" />
          </div>
          <div v-if="pwdError" class="error-msg">{{ pwdError }}</div>
          <div v-if="pwdSuccess" class="success-msg">{{ pwdSuccess }}</div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showPasswordModal = false">取消</button>
            <button type="submit" class="btn-confirm" :disabled="pwdLoading">
              {{ pwdLoading ? '处理中...' : '确认修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="toast-container">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="toast"
        :class="['toast-' + t.type, { 'toast-removing': t.removing }]"
      >
        {{ t.message }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, provide, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi, notesApi } from './api'

let toastId = 0

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const toasts = ref([])

    const showToast = (message, type = 'success', duration = 2500) => {
      const id = ++toastId
      toasts.value.push({ id, message, type, removing: false })
      setTimeout(() => {
        const t = toasts.value.find(t => t.id === id)
        if (t) t.removing = true
        setTimeout(() => {
          toasts.value = toasts.value.filter(t => t.id !== id)
        }, 300)
      }, duration)
    }

    const username = computed(() => {
      try {
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        return user.username || ''
      } catch {
        return ''
      }
    })

    const handleLogout = () => {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }

    const isDark = ref(false)

    const applyTheme = () => {
      document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
    }

    const toggleTheme = () => {
      isDark.value = !isDark.value
      applyTheme()
      localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
    }

    const handleSystemThemeChange = (e) => {
      if (!localStorage.getItem('theme')) {
        isDark.value = e.matches
        applyTheme()
      }
    }

    let mediaQuery = null

    const trashCount = ref(0)
    let trashInterval = null
    const sidebarOpen = ref(false)

    const fetchTrashCount = async () => {
      try {
        const res = await notesApi.trashCount()
        trashCount.value = res.data.count
      } catch (e) {
        trashCount.value = 0
      }
    }

    onMounted(() => {
      const saved = localStorage.getItem('theme')
      if (saved) {
        isDark.value = saved === 'dark'
      } else {
        isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
      }
      applyTheme()
      mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      mediaQuery.addEventListener('change', handleSystemThemeChange)
      fetchTrashCount()
      trashInterval = setInterval(fetchTrashCount, 30000)
    })

    onUnmounted(() => {
      if (mediaQuery) {
        mediaQuery.removeEventListener('change', handleSystemThemeChange)
      }
      if (trashInterval) {
        clearInterval(trashInterval)
      }
    })

    const showPasswordModal = ref(false)
    const pwdForm = ref({ old_password: '', new_password: '', confirm_password: '' })
    const pwdError = ref('')
    const pwdSuccess = ref('')
    const pwdLoading = ref(false)

    const handleChangePassword = async () => {
      pwdError.value = ''
      pwdSuccess.value = ''

      if (pwdForm.value.new_password.length < 6) {
        pwdError.value = '新密码长度不能少于6位'
        return
      }
      if (pwdForm.value.new_password !== pwdForm.value.confirm_password) {
        pwdError.value = '两次密码输入不一致'
        return
      }

      pwdLoading.value = true
      try {
        await authApi.changePassword(pwdForm.value)
        pwdSuccess.value = '密码修改成功'
        pwdForm.value = { old_password: '', new_password: '', confirm_password: '' }
        setTimeout(() => { showPasswordModal.value = false }, 1500)
      } catch (err) {
        pwdError.value = err.response?.data?.detail || '修改失败'
      } finally {
        pwdLoading.value = false
      }
    }

    provide('toast', showToast)

    return {
      toasts, username, handleLogout,
      isDark, toggleTheme, trashCount, sidebarOpen,
      showPasswordModal, pwdForm, pwdError, pwdSuccess, pwdLoading, handleChangePassword,
    }
  },
}
</script>
