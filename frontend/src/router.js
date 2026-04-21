import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import SearchView from './views/SearchView.vue'
import CategoryView from './views/CategoryView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/search', name: 'search', component: SearchView },
  { path: '/categories', name: 'categories', component: CategoryView },
  { path: '/notes/:id', name: 'note-detail', component: () => import('./views/NoteDetailView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
