import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  { path: '/', redirect: '/login' },
  {
    path: '/login',
    component: () => import('@/views/LoginView.vue')
  },
  {
    path: '/owner',
    component: () => import('@/views/OwnerLayout.vue'),
    meta: { roles: ['owner'] },
    children: [
      { path: '', redirect: '/owner/dashboard' },
      { path: 'dashboard', component: () => import('@/views/OwnerDashboard.vue') },
      { path: 'managers', component: () => import('@/views/ManagersList.vue') },
      { path: 'points', component: () => import('@/views/PointsList.vue') }, // ← добавить
    ]
  },
  {
    path: '/manager',
    component: () => import('@/views/ManagerLayout.vue'),
    meta: { roles: ['manager'] },
    children: [
      { path: '', redirect: '/manager/dashboard' },
      { path: 'dashboard', component: () => import('@/views/ManagerDashboard.vue') },
      { path: 'points', component: () => import('@/views/PointsList.vue') },
      { path: 'points/:id', component: () => import('@/views/PointDetails.vue'), props: true },
      { path: 'tables/:tableId/builder', component: () => import('@/views/TableBuilder.vue'), props: true },
      { path: 'cashiers', component: () => import('@/views/CashiersList.vue') },
    ]
  },
  {
    path: '/cashier',
    component: () => import('@/views/CashierLayout.vue'),
    meta: { roles: ['cashier'] },
    children: [
      { path: '', redirect: '/cashier/register' },
      { path: 'register', component: () => import('@/views/CashRegister.vue') },
      { path: 'tables/:tableId', component: () => import('@/views/TableRows.vue'), props: true },
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from) => {
  const auth = useAuthStore()

  if (to.meta.roles) {
    if (!auth.user) {
      return '/login'
    }
    const requiredRoles = to.meta.roles
    if (!requiredRoles.includes(auth.user.role)) {
      if (auth.user.role === 'owner') return '/owner/dashboard'
      if (auth.user.role === 'manager') return '/manager/dashboard'
      if (auth.user.role === 'cashier') return '/cashier/register'
    }
  }

  if (to.path === '/login' && auth.user) {
    const role = auth.user.role
    if (role === 'owner') return '/owner/dashboard'
    if (role === 'manager') return '/manager/dashboard'
    if (role === 'cashier') return '/cashier/register'
  }

  return true
})

export default router