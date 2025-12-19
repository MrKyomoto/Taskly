import { request } from './index';

/**
 * 获取所有学生
 */
export const fetchAllStudents = () => request.get('/admins/students');

/**
 * 获取所有教职工（包括教师和助教）
 */
export const fetchAllStaff = () => request.get('/admins/staff');

/**
 * 获取所有教师
 */
export const fetchAllTeachers = () => request.get('/admins/teachers');

/**
 * 获取所有课程
 */
export const fetchAllCourses = () => request.get('/admins/courses');

/**
 * 创建教职工
 * @param {Object} data - 包含 staff_no, name, password, role, email, phone
 */
export const createStaff = (data) => request.post('/admins/staff', data);

/**
 * 重置用户密码
 * @param {String} userType - 'staff' 或 'student'
 * @param {Number} userId - 用户ID
 * @param {Object} data - 包含 default_password (可选，默认 '123456')
 */
export const resetUserPassword = (userType, userId, data = {}) =>
  request.patch(`/admins/users/${userType}/${userId}/reset-password`, data);

/**
 * 删除用户
 * @param {String} userType - 'teacher' 或 'student'
 * @param {Number} userId - 用户ID
 */
export const deleteUser = (userType, userId) =>
  request.delete(`/admins/users/${userType}/${userId}`);

