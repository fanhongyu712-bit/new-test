import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' }
      },
      {
        path: 'elderly',
        name: 'ElderlyList',
        component: () => import('@/views/elderly/ElderlyList.vue'),
        meta: { title: '老人管理', icon: 'User' }
      },
      {
        path: 'elderly/:id',
        name: 'ElderlyDetail',
        component: () => import('@/views/elderly/ElderlyDetail.vue'),
        meta: { title: '老人详情', hidden: true }
      },
      {
        path: 'health',
        name: 'HealthMonitor',
        component: () => import('@/views/health/HealthMonitor.vue'),
        meta: { title: '健康监测', icon: 'Monitor' }
      },
      {
        path: 'analysis',
        name: 'HealthAnalysis',
        component: () => import('@/views/analysis/HealthAnalysis.vue'),
        meta: { title: '智能分析', icon: 'Cpu' }
      },
      {
        path: 'alerts',
        name: 'AlertCenter',
        component: () => import('@/views/alerts/AlertCenter.vue'),
        meta: { title: '预警中心', icon: 'Bell' }
      },
      {
        path: 'interventions',
        name: 'InterventionList',
        component: () => import('@/views/interventions/InterventionList.vue'),
        meta: { title: '干预管理', icon: 'FirstAidKit' }
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('@/views/reports/Reports.vue'),
        meta: { title: '统计报表', icon: 'DataAnalysis' }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/system/UserManagement.vue'),
        meta: { title: '用户管理', icon: 'UserFilled', roles: ['admin', 'institution_admin'] }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/system/Settings.vue'),
        meta: { title: '系统设置', icon: 'Setting' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/Profile.vue'),
        meta: { title: '个人中心', hidden: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
