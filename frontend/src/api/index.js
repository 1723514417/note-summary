import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 0,
})

export const notesApi = {
  create: (data) => api.post('/notes', data),
  list: (params) => api.get('/notes', { params }),
  get: (id) => api.get(`/notes/${id}`),
  update: (id, data) => api.put(`/notes/${id}`, data),
  delete: (id) => api.delete(`/notes/${id}`),
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
