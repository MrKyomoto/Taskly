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

/**
 * 创建学生
 * @param {Object} data - 包含 student_no, name, password, email, phone
 */
export const createStudent = (data) => request.post('/admins/students', data);

/**
 * 更新学生信息
 * @param {Number} studentId - 学生ID
 * @param {Object} data - 包含 name, email, phone
 */
export const updateStudent = (studentId, data) =>
  request.patch(`/admins/students/${studentId}`, data);

/**
 * 更新教职工信息
 * @param {Number} staffId - 教职工ID
 * @param {Object} data - 包含 name, email, phone
 */
export const updateStaff = (staffId, data) =>
  request.patch(`/admins/staff/${staffId}`, data);

/**
 * 创建课程
 * @param {Object} data - 包含 course_code, course_name, semester, description
 */
export const createCourse = (data) => request.post('/admins/courses', data);

/**
 * 更新课程信息
 * @param {Number} courseId - 课程ID
 * @param {Object} data - 包含 course_name, semester, description
 */
export const updateCourse = (courseId, data) =>
  request.patch(`/admins/courses/${courseId}`, data);

/**
 * 删除课程
 * @param {Number} courseId - 课程ID
 */
export const deleteCourse = (courseId) =>
  request.delete(`/admins/courses/${courseId}`);

/**
 * 课程结课
 * @param {Number} courseId - 课程ID
 */
export const closeCourse = (courseId) =>
  request.post(`/admins/courses/${courseId}/close`);

/**
 * 审核课程
 * @param {Number} courseId - 课程ID
 * @param {Boolean} approve - true为通过，false为驳回
 */
export const approveCourse = (courseId, approve) =>
  request.post(`/admins/courses/${courseId}/approve`, { approve });

/**
 * 管理员添加教师到课程
 * @param {Number} courseId - 课程ID
 * @param {Object} data - 包含 staff_no 字段
 */
export const addTeacherToCourse = (courseId, data) =>
  request.post(`/admins/courses/${courseId}/add-teacher`, data);

/**
 * 管理员添加助教到课程
 * @param {Number} courseId - 课程ID
 * @param {Object} data - 包含 student_no 字段（助教从学生中选择）
 */
export const addTAToCourse = (courseId, data) =>
  request.post(`/admins/courses/${courseId}/add-ta`, data);

/**
 * 管理员添加学生到课程
 * @param {Number} courseId - 课程ID
 * @param {Object} data - 包含 student_no 字段
 */
export const addStudentToCourse = (courseId, data) =>
  request.post(`/admins/courses/${courseId}/add-student`, data);

