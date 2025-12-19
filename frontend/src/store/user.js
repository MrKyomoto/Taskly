import { defineStore } from 'pinia';
import { login as loginApi, register as registerApi } from '@/api/auth';
import router from '@/router';
import { ElMessage } from 'element-plus';

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: (() => {
      try {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
      } catch (e) {
        return null;
      }
    })(),
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    // 统一登录接口，自动识别角色并分流
    async login(credentials) {
      try {
        const response = await loginApi(credentials);
        const { access_token, role, student, teacher, admin } = response.data;
        
        // 根据返回的角色获取用户信息
        const userObj = student || teacher || admin || null;
        this.token = access_token;
        this.user = userObj ? { ...userObj, role } : null;
        
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(this.user));
        
        // 根据角色自动跳转
        if (role === 'admin') {
          router.push({ name: 'AdminDashboard' });
        } else if (role === 'teacher' || role === 'ta') {
          router.push({ name: 'TeacherHome' });
        } else {
        router.push({ name: 'StudentHome' });
        }
      } catch (error) {
        console.error('Login failed:', error);
        // 不在这里显示错误消息，让调用方处理
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
    logout(forceReload = true) {
      // 先清除状态
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      // 如果 forceReload 为 true，使用 window.location 强制刷新页面
      // 如果为 false，使用 router 跳转（用于登录前清除状态等场景）
      if (forceReload) {
        window.location.href = '/login';
      } else {
        router.replace({ name: 'Login' });
      }
    },
    initialize() {
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');
        if (token && user) {
            try {
                this.token = token;
                this.user = JSON.parse(user);
            } catch (e) {
                // 如果解析失败，清除无效数据
                localStorage.removeItem('token');
                localStorage.removeItem('user');
                this.token = null;
                this.user = null;
            }
        }
    }
  },
});
