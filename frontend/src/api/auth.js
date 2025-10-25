import api from './index';

const plural = (role) => {
  if (!role) return 'students';
  return role === 'teacher' ? 'teachers' : 'students';
};

// login(role, data) where role is 'student' (default) or 'teacher'
export const login = (role = 'student', data) => {
  const path = `/auth/${plural(role)}/login`;
  return api.post(path, data);
};

// register(role, data) where role is 'student' (default) or 'teacher'
export const register = (role = 'student', data) => {
  const path = `/auth/${plural(role)}/register`;
  return api.post(path, data);
};
