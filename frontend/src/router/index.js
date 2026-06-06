import { createRouter, createWebHistory } from 'vue-router'
import PublicGallery from '../views/PublicGallery.vue'
import LoginView from '../views/LoginView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Gallery',
    component: PublicGallery
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guard to protect dashboard routes
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('artfolio_token')
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      next({ name: 'Login' })
    } else {
      next()
    }
  } else {
    // If already logged in, redirect away from Login to Dashboard
    if (to.name === 'Login' && token) {
      next({ name: 'Dashboard' })
    } else {
      next()
    }
  }
})

export default router
