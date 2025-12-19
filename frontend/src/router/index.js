import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store/user';
import { ElMessage } from 'element-plus';
import Login from '@/views/Login.vue';
import StudentHome from '@/views/StudentHome.vue';
import CourseDetail from '@/views/CourseDetail.vue';
import HomeworkView from '@/views/HomeworkView.vue';
import TeacherHome from '../views/TeacherHome.vue';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'StudentHome',
    component: StudentHome,
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
  },
  {
    path: '/homeworks/:id/submission',
    name: 'SubmissionView',
    component: () => import('@/views/SubmissionView.vue'),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/homeworks',
    name: 'AllHomeworksView',
    component: () => import('@/views/AllHomeworksView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/homeworks/pending',
    name: 'PendingHomeworksView',
    component: () => import('@/views/AllHomeworksView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/homeworks/submitted',
    name: 'SubmittedHomeworksView',
    component: () => import('@/views/AllHomeworksView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/homeworks/completed',
    name: 'CompletedHomeworksView',
    component: () => import('@/views/AllHomeworksView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/homeworks/date/:date/pending',
    name: 'DatePendingHomeworksView',
    component: () => import('@/views/DatePendingHomeworksView.vue'),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/teacher/home',
    name: 'TeacherHome',
    component: TeacherHome,
    meta: { requiresAuth: true, roles: ['teacher', 'ta'] },
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: () => import('@/views/AdminDashboard.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
  },
  {
    path: '/teacher/courses/:id',
    name: 'TeacherCourseDetail',
    component: () => import('@/views/TeacherCourseDetail.vue'),
    props: true,
    meta: { requiresAuth: true, roles: ['teacher', 'ta'] },
  },
  {
    path: '/teacher/courses/:courseId/homeworks/:homeworkId/grading',
    name: 'GradingView',
    component: () => import('@/views/GradingView.vue'),
    props: true,
    meta: { requiresAuth: true, roles: ['teacher', 'ta'] },
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  const isAuthenticated = userStore.isAuthenticated;
  const user = userStore.user;
  const userRole = user?.role;

  // 如果未登录且需要认证，跳转到登录页
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Login' });
    return;
  }

  // 如果访问登录页
  if (to.name === 'Login') {
    // 如果已登录，需要判断是否是从其他页面跳转过来的（logout场景）
    if (isAuthenticated) {
      // 如果 from.name 不存在，说明是直接访问或刷新，需要重定向到对应首页
      if (!from.name) {
        if (userRole === 'admin') {
          next({ name: 'AdminDashboard' });
        } else if (userRole === 'teacher' || userRole === 'ta') {
          next({ name: 'TeacherHome' });
        } else {
    next({ name: 'StudentHome' });
  }
        return;
      }
      // 如果 from.name 存在，说明是从其他页面跳转过来的
      // 但此时如果 isAuthenticated 为 true，可能是状态还没更新
      // 再次检查一次，如果确实已登录，重定向；否则允许访问登录页
      // 这里允许访问登录页，因为可能是 logout 触发的跳转
      next();
      return;
    }
    // 如果未登录，直接允许访问登录页
    next();
    return;
  }

  // 角色权限检查
  if (to.meta.requiresAuth && to.meta.roles) {
    const allowedRoles = to.meta.roles;
    if (!userRole || !allowedRoles.includes(userRole)) {
      ElMessage.warning('您没有权限访问该页面');
      // 根据角色跳转到对应首页
      if (userRole === 'admin') {
        next({ name: 'AdminDashboard' });
      } else if (userRole === 'teacher' || userRole === 'ta') {
        next({ name: 'TeacherHome' });
      } else {
        next({ name: 'StudentHome' });
      }
      return;
    }
  }

  next();
});

export default router;
