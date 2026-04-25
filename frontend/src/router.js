import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import SearchView from './views/SearchView.vue'
import CategoryView from './views/CategoryView.vue'
import LoginView from './views/LoginView.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
  { path: '/', name: 'home', component: HomeView },
  { path: '/search', name: 'search', component: SearchView },
  { path: '/categories', name: 'categories', component: CategoryView },
  { path: '/stats', name: 'stats', component: () => import('./views/StatsView.vue') },
  { path: '/tags', name: 'tags', component: () => import('./views/TagsView.vue') },
  { path: '/trash', name: 'trash', component: () => import('./views/TrashView.vue') },
  { path: '/notes/:id', name: 'note-detail', component: () => import('./views/NoteDetailView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    next({ name: 'login' })
  } else if (to.meta.public && token && to.name === 'login') {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
