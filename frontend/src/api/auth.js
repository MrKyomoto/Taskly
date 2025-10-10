import api from './index';

export const login = (data) => {
  return api.post('/auth/students/login', data);
};

export const register = (data) => {
  return api.post('/auth/students/register', data);
};
