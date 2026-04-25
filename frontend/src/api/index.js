import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 0,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
  changePassword: (data) => api.post('/auth/change-password', data),
}

export const notesApi = {
  create: (data) => api.post('/notes', data),
  list: (params) => api.get('/notes', { params }),
  get: (id) => api.get(`/notes/${id}`),
  update: (id, data) => api.put(`/notes/${id}`, data),
  delete: (id) => api.delete(`/notes/${id}`),
  trashList: (params) => api.get('/notes/trash/list', { params }),
  trashCount: () => api.get('/notes/trash/count'),
  restore: (id) => api.post(`/notes/${id}/restore`),
  permanentDelete: (id) => api.delete(`/notes/${id}/permanent`),
  toggleStar: (id) => api.post(`/notes/${id}/star`),
  togglePin: (id) => api.post(`/notes/${id}/pin`),
  links: (id) => api.get(`/notes/${id}/links`),
}

export const searchApi = {
  search: (params) => api.get('/search', { params }),
}

export const categoriesApi = {
  list: () => api.get('/categories'),
  create: (data) => api.post('/categories', data),
  update: (id, data) => api.put(`/categories/${id}`, data),
  delete: (id) => api.delete(`/categories/${id}`),
}

export const tagsApi = {
  list: () => api.get('/tags'),
  getNotes: (tagId, params) => api.get(`/tags/${tagId}/notes`, { params }),
}

export const aiApi = {
  organize: (data) => api.post('/ai/organize', data),
  research: (data) => api.post('/ai/research', data),
}

export default api
