import api from './index';

// 统一登录接口
export const login = (credentials) => {
  return api.post('/auth/login', credentials);
};

// 注册接口（保留原有功能，用于学生和教师注册）
const plural = (role) => {
  if (!role) return 'students';
  return role === 'teacher' ? 'teachers' : 'students';
};

export const register = (role = 'student', data) => {
  const path = `/auth/${plural(role)}/register`;
  return api.post(path, data);
};

// resetPassword(data) 重置密码接口（登录界面使用）
export const resetPassword = (data) => {
  return api.post('/auth/students/reset-password', data);
};
