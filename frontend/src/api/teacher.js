import axios from 'axios';

// 创建一个 axios 实例，用于 API 请求
const apiClient = axios.create({
  baseURL: '/api', // 后端 API 的基础路径
  headers: {
    'Content-Type': 'application/json',
  }
});

// 添加请求拦截器，在每个请求中附加 JWT token
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

/**
 * 获取当前登录教师的个人资料
 * @returns {Promise}
 */
export const getTeacherProfile = () => {
  return apiClient.get('/teachers/me');
};

/**
 * 获取当前教师教授的课程列表
 * @returns {Promise}
 */
export const getTeacherCourses = () => {
  return apiClient.get('/teachers/me/courses');
};

/**
 * 获取指定课程下的所有作业
 * @param {string|number} courseId - 课程ID
 * @returns {Promise}
 */
export const getCourseHomeworks = (courseId) => {
  return apiClient.get(`/teachers/me/courses/${courseId}/homeworks`);
};
