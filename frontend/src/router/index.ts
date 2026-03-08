import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import ChatPage from '../pages/ChatPage.vue'
import KnowledgeBasePage from '../pages/KnowledgeBasePage.vue'
import SettingsPage from '../pages/SettingsPage.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'chat',
    component: ChatPage,
    meta: { title: '对话' }
  },
  {
    path: '/knowledge-base',
    name: 'knowledge-base',
    component: KnowledgeBasePage,
    meta: { title: '知识库' }
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsPage,
    meta: { title: '设置' }
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'RAG Agent'} - 智能助手`
  next()
})

export default router
