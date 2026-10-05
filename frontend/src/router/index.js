import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/Register.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/views/Dashboard.vue'),
  },
  {
    path: '/goal',
    name: 'goal',
    component: () => import('@/views/GoalSetup.vue'),
  },
  {
    path: '/meals',
    name: 'meals',
    component: () => import('@/views/MealLog.vue'),
  },
  {
    path: '/workouts',
    name: 'workouts',
    component: () => import('@/views/WorkoutLog.vue'),
  },
  {
    path: '/charts',
    name: 'charts',
    component: () => import('@/views/Charts.vue'),
  },
  {
    path: '/recommendations',
    name: 'recommendations',
    component: () => import('@/views/Recommendations.vue'),
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/Profile.vue'),
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard: protected pages need a JWT; logged-in users skip auth pages.
router.beforeEach((to) => {
  const authed = store.getters['auth/isAuthenticated']
  if (!to.meta.public && !authed) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.public && authed) {
    return { name: 'dashboard' }
  }
  return true
})

export default router
