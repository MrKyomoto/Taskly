import { defineStore } from 'pinia';
import { login as loginApi, register as registerApi } from '@/api/auth';
import router from '@/router';

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    // credentials: object, role: 'student' | 'teacher'
    async login(credentials, role = 'student') {
      try {
        const response = await loginApi(role, credentials);
        const { access_token, student, teacher } = response.data;
        const userObj = student || teacher || null;
        const userRole = student ? 'student' : teacher ? 'teacher' : role;
        this.token = access_token;
        this.user = userObj ? { ...userObj, role: userRole } : null;
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(this.user));
        // currently route to the main home (student home). If you add a teacher home, switch based on role here.
        router.push({ name: 'StudentHome' });
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },

    // userInfo: object, role: 'student' | 'teacher'
    async register(userInfo, role = 'student') {
      try {
        await registerApi(role, userInfo);
        // 保持原有行为：注册成功后让用户手动登录（Login.vue 会提示）
      } catch (error) {
        console.error('Registration failed:', error);
        throw error;
      }
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      router.push({ name: 'Login' });
    },
    initialize() {
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');
        if (token && user) {
            this.token = token;
            this.user = JSON.parse(user);
        }
    }
  },
});
