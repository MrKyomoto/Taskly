import { request } from './index';

export const fetchStudentProfile = () => request.get('/students/me');

export const fetchStudentCourses = () => request.get('/students/me/courses');

export const fetchCourseHomeworks = (courseId) =>
  request.get(`/students/me/courses/${courseId}/homeworks`);

export const fetchHomeworkSubmission = (courseId, homeworkId) =>
  request.get(`/students/me/courses/${courseId}/homeworks/${homeworkId}/submission`);

/**
 * 修改学生个人资料（姓名、邮箱、电话）
 * @param {Object} data - 包含要更新的字段（name, email, phone）
 * @returns {Promise} API响应
 */
export const updateStudentProfile = (data) =>
  request.patch('/students/me', data);

/**
 * 修改学生密码
 * @param {Object} data - 包含 old_password 和 new_password 的对象
 * @returns {Promise} API响应
 */
export const updatePassword = (data) =>
  request.patch('/students/me/password', data);

/**
 * 加入课程（选课）
 * @param {Object} data - 包含 course_code 的对象
 * @returns {Promise} API响应
 */
export const enrollCourse = (data) =>
  request.post('/students/me/courses', data);

/**
 * 提交作业
 * @param {Number} homeworkId - 作业ID
 * @param {Object} data - 包含 text_content 和 image_urls 的对象
 * @returns {Promise} API响应
 */
export const submitHomework = (homeworkId, data) =>
  request.post(`/students/me/homeworks/${homeworkId}/submission`, data);

/**
 * 上传作业图片
 * @param {Number} homeworkId - 作业ID
 * @param {FormData} formData - 包含文件的 FormData
 * @returns {Promise} API响应
 */
export const uploadHomeworkImage = (homeworkId, formData) =>
  request.post(`/students/me/homeworks/${homeworkId}/upload-image`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

/**
 * 获取课程的教师列表
 * @param {Number} courseId - 课程ID
 * @returns {Promise} API响应
 */
export const fetchCourseTeachers = (courseId) =>
  request.get(`/students/me/courses/${courseId}/teachers`);

/**
 * 获取课程的助教列表
 * @param {Number} courseId - 课程ID
 * @returns {Promise} API响应
 */
export const fetchCourseTAs = (courseId) =>
  request.get(`/students/me/courses/${courseId}/tas`);
