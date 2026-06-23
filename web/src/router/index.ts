import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/register/:slug',
      name: 'register-enterprise',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/reset_password/:token/:first_setup',
      name: 'reset_password',
      component: () => import('../views/ResetPasswordView.vue')
    },
    {
      path: '/notifications',
      name: 'notifications',
      component: () => import('../views/NotificationsView.vue')
    },
    {
      path: '/',
      name: 'reservations',
      component: () => import('../views/ReservationsView.vue')
    },
    {
      path: '/shops',
      name: 'shops',
      component: () => import('../views/ShopsView.vue')
    },
    {
      path: '/shops/:id/:week',
      name: 'shop',
      component: () => import('../views/ShopView.vue')
    },
    {
      path: '/admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      children: [
        {
          path: 'shops',
          name: 'admin-shops',
          component: () => import('../views/admin/AdminShopsView.vue')
        },
        {
          path: 'reservations',
          name: 'admin-reservations',
          component: () => import('../views/admin/AdminReservationsView.vue')
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('../views/admin/AdminUsersView.vue')
        },
        {
          path: 'enterprises',
          name: 'admin-enterprises',
          component: () => import('../views/admin/AdminEnterprisesView.vue')
        },
        {
          path: 'documents',
          name: 'admin-documents',
          component: () => import('../views/admin/AdminDocumentsView.vue')
        },
        {
          path: 'mail-templates',
          name: 'admin-mail-templates',
          component: () => import('../views/admin/AdminMailTemplatesView.vue')
        },
        {
          path: 'settings',
          name: 'admin-settings',
          component: () => import('../views/admin/AdminSettingsView.vue')
        }
      ]
    }
  ]
})

router.onError((error, to) => {
  if (error.message.includes('Failed to fetch dynamically imported module') || error.message.includes("Importing a module script failed") || error.message.includes("Loading chunk") || error.message.includes("dynamically imported module")) {
    window.location.href = to.fullPath
  }
})

export default router
