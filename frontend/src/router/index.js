import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store/user';
import Login from '@/views/Login.vue';
import Dashboard from '@/views/Dashboard.vue';
import CourseDetail from '@/views/CourseDetail.vue';
import HomeworkView from '@/views/HomeworkView.vue';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/courses/:id',
    name: 'CourseDetail',
    component: CourseDetail,
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/homeworks/:id',
    name: 'HomeworkView',
    component: HomeworkView,
    props: true,
    meta: { requiresAuth: true },
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  const isAuthenticated = userStore.isAuthenticated;

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' });
  } else if (to.name === 'Login' && isAuthenticated) {
    next({ name: 'Dashboard' });
  }
  else {
    next();
  }
});

export default router;
