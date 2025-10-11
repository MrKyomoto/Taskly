import { defineStore } from 'pinia';
import { login as apiLogin, register as apiRegister } from '@/api/auth';
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
    async login(credentials) {
      try {
  const response = await apiLogin(credentials);
  const { access_token, student } = response.data;
  this.token = access_token;
  this.user = student;
  localStorage.setItem('token', access_token);
  localStorage.setItem('user', JSON.stringify(student));
  router.push({ name: 'StudentHome' });
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },
    async register(userInfo) {
        try {
            await apiRegister(userInfo);
            // 注册后可以自动登录或提示用户登录
            // 这里我们选择让用户手动登录
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
