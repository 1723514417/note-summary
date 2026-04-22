<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <span class="login-logo">📝</span>
        <h1>Note Summary</h1>
        <p>个人知识库</p>
      </div>
      <div class="login-tabs">
        <button
          :class="['tab-btn', { active: mode === 'login' }]"
          @click="mode = 'login'"
        >登录</button>
        <button
          :class="['tab-btn', { active: mode === 'register' }]"
          @click="mode = 'register'"
        >注册</button>
      </div>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>用户名</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            required
            autocomplete="username"
          />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            :placeholder="mode === 'register' ? '请输入密码（至少6位）' : '请输入密码'"
            required
            :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
          />
        </div>
        <div v-if="mode === 'register'" class="form-group">
          <label>确认密码</label>
          <input
            v-model="form.confirm_password"
            type="password"
            placeholder="请再次输入密码"
            required
            autocomplete="new-password"
          />
        </div>
        <div v-if="error" class="error-msg">{{ error }}</div>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '处理中...' : (mode === 'login' ? '登录' : '注册') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api'

export default {
  name: 'LoginView',
  setup() {
    const router = useRouter()
    const mode = ref('login')
    const form = ref({ username: '', password: '', confirm_password: '' })
    const error = ref('')
    const loading = ref(false)

    watch(mode, () => { error.value = '' })

    const handleSubmit = async () => {
      error.value = ''

      if (mode.value === 'register') {
        if (form.value.password.length < 6) {
          error.value = '密码长度不能少于6位'
          return
        }
        if (form.value.password !== form.value.confirm_password) {
          error.value = '两次密码输入不一致'
          return
        }
      }

      loading.value = true
      try {
        const api = mode.value === 'login' ? authApi.login : authApi.register
        const payload = {
          username: form.value.username,
          password: form.value.password,
          ...(mode.value === 'register' ? { confirm_password: form.value.confirm_password } : {}),
        }
        const res = await api(payload)
        localStorage.setItem('token', res.data.access_token)
        localStorage.setItem('user', JSON.stringify(res.data.user))
        router.push('/')
      } catch (err) {
        const detail = err.response?.data?.detail
        if (typeof detail === 'string') {
          error.value = detail
        } else {
          error.value = mode.value === 'login' ? '用户名或密码错误' : '注册失败，请重试'
        }
      } finally {
        loading.value = false
      }
    }

    return { mode, form, error, loading, handleSubmit }
  },
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--login-gradient, linear-gradient(135deg, #667eea 0%, #764ba2 100%));
}

.login-card {
  width: 400px;
  background: var(--card-bg);
  border-radius: 12px;
  padding: 40px;
  box-shadow: var(--modal-shadow);
}

.login-header {
  text-align: center;
  margin-bottom: 28px;
}

.login-logo {
  font-size: 40px;
}

.login-header h1 {
  font-size: 22px;
  font-weight: 700;
  color: var(--text);
  margin: 8px 0 4px;
}

.login-header p {
  color: var(--text-secondary);
  font-size: 14px;
}

.login-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 24px;
  background: var(--tab-bg);
  border-radius: 8px;
  padding: 3px;
}

.tab-btn {
  flex: 1;
  padding: 8px;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: var(--tab-active-bg);
  color: var(--primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-label);
  margin-bottom: 6px;
}

.form-group input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--input-border);
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
  background: var(--input-bg);
  color: var(--text);
}

.form-group input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--input-focus-ring);
}

.error-msg {
  background: var(--error-bg);
  color: var(--error-text);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 16px;
}

.submit-btn {
  width: 100%;
  padding: 10px;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover {
  background: var(--primary-hover);
}

.submit-btn:disabled {
  background: var(--primary-light);
  cursor: not-allowed;
}
</style>
