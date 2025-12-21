import { defineStore } from 'pinia';
import { login as loginApi, register as registerApi } from '@/api/auth';
import router from '@/router';
import { ElMessage } from 'element-plus';
import { usePersonalizationStore } from './personalization';

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
    async login(credentials, selectedRole = null) {
      try {
        const response = await loginApi(credentials);
        const { access_token, role, student, teacher, admin } = response.data;
        
        // 根据返回的角色获取用户信息
        const userObj = student || teacher || admin || null;
        this.token = access_token;
        this.user = userObj ? { ...userObj, role } : null;
        
        localStorage.setItem('token', access_token);
        localStorage.setItem('user', JSON.stringify(this.user));
        
        // 加载当前用户的个性化设置
        const personalizationStore = usePersonalizationStore();
        personalizationStore.loadUserSettings();
        
        // 如果是助教且未选择角色，返回特殊标识，让前端显示选择对话框
        if (role === 'ta' && !selectedRole) {
          return { needsRoleSelection: true, role: 'ta' };
        }
        
        // 根据角色或选择自动跳转
        const targetRole = selectedRole || role;
        if (targetRole === 'admin') {
          router.push({ name: 'AdminDashboard' });
        } else if (targetRole === 'teacher' || (targetRole === 'ta' && selectedRole === 'teacher')) {
          // 助教选择教师端，跳转到教师端
          router.push({ name: 'TeacherHome' });
        } else if (targetRole === 'ta' && selectedRole === 'student') {
          // 助教选择学生端，跳转到学生端
          router.push({ name: 'StudentHome' });
        } else {
        router.push({ name: 'StudentHome' });
        }
        
        return { needsRoleSelection: false };
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
    },
    // 助教切换角色（学生端 <-> 教师端）
    switchTARole() {
      if (this.user?.role !== 'ta') {
        ElMessage.warning('只有助教可以切换角色');
        return;
      }
      
      // 获取当前路由名称，判断当前在哪个端
      const currentRoute = router.currentRoute.value.name;
      const isInTeacherMode = currentRoute === 'TeacherHome' || currentRoute?.startsWith('Teacher');
      
      // 切换角色
      if (isInTeacherMode) {
        // 当前在教师端，切换到学生端
        router.push({ name: 'StudentHome' });
        ElMessage.success('已切换到学生端');
      } else {
        // 当前在学生端，切换到教师端
        router.push({ name: 'TeacherHome' });
        ElMessage.success('已切换到教师端');
        }
    }
  },
});
