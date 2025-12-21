import { request } from './index';

/**
 * 获取教师个人信息
 */
export const fetchTeacherProfile = () => request.get('/teachers/me');

/**
 * 获取教师负责的所有课程
 */
export const fetchTeacherCourses = () => request.get('/teachers/me/courses');

/**
 * 创建新课程
 * @param {Object} data - 包含 course_name, semester 等字段
 */
export const createCourse = (data) => request.post('/teachers/me/courses', data);

/**
 * 获取课程的所有作业
 * @param {Number} courseId - 课程ID
 */
export const fetchCourseHomeworks = (courseId) =>
  request.get(`/teachers/me/courses/${courseId}/homeworks`);

/**
 * 创建作业
 * @param {Number} courseId - 课程ID
 * @param {Object} data - 作业数据
 */
export const createHomework = (courseId, data) =>
  request.post(`/teachers/me/courses/${courseId}/homeworks`, data);

/**
 * 上传作业图片
 * @param {Number} courseId - 课程ID
 * @param {Number} homeworkId - 作业ID
 * @param {FormData} formData - 包含文件的 FormData
 */
export const uploadHomeworkImage = (courseId, homeworkId, formData) =>
  request.post(`/teachers/me/courses/${courseId}/homeworks/${homeworkId}/upload-image`, formData, {
  headers: {
      'Content-Type': 'multipart/form-data',
    },
});

/**
 * 获取学生提交列表
 * @param {Number} courseId - 课程ID
 * @param {Number} homeworkId - 作业ID
 */
export const fetchStudentSubmissions = (courseId, homeworkId) =>
  request.get(`/teachers/me/courses/${courseId}/homeworks/${homeworkId}/submissions`);

/**
 * 批改作业
 * @param {Number} submissionId - 提交ID
 * @param {Object} data - 包含 score, ai_feedback, annotation_data 等字段
 */
export const gradeSubmission = (submissionId, data) =>
  request.post(`/teachers/me/submissions/${submissionId}/grade`, data);

/**
 * 更新作业
 * @param {Number} courseId - 课程ID
 * @param {Number} homeworkId - 作业ID
 * @param {Object} data - 作业数据
 */
export const updateHomework = (courseId, homeworkId, data) =>
  request.patch(`/teachers/me/courses/${courseId}/homeworks/${homeworkId}`, data);

/**
 * 删除作业（仅教师）
 * @param {Number} courseId - 课程ID
 * @param {Number} homeworkId - 作业ID
 */
export const deleteHomework = (courseId, homeworkId) =>
  request.delete(`/teachers/me/courses/${courseId}/homeworks/${homeworkId}`);

/**
 * 获取课程学生列表（教师端）
 * @param {Number} courseId - 课程ID
 */
export const fetchCourseStudents = (courseId) =>
  request.get(`/teachers/courses/${courseId}/students`);

/**
 * 添加助教到课程（仅教师）
 * @param {Number} courseId - 课程ID
 * @param {Object} data - 包含 student_no 字段（助教从学生中选择）
 */
export const addTAToCourse = (courseId, data) =>
  request.post(`/teachers/me/courses/${courseId}/add-ta`, data);

/**
 * 获取课程的助教列表
 * @param {Number} courseId - 课程ID
 */
export const fetchCourseTAs = (courseId) =>
  request.get(`/teachers/courses/${courseId}/tas`);

/**
 * 获取课程的教师列表
 * @param {Number} courseId - 课程ID
 */
export const fetchCourseTeachers = (courseId) =>
  request.get(`/teachers/courses/${courseId}/teachers`);

/**
 * 导出课程成绩为 Excel
 * @param {Number} courseId - 课程ID
 * @param {Object} filters - 可选过滤条件，如 { homework_ids: '1,2', student_ids: '11,12' }
 */
export const exportCourseGrades = (courseId, filters = {}) =>
  request.get(`/teachers/me/courses/${courseId}/export-grades`, {
    responseType: 'blob',
    params: filters,
  });

/**
 * 为未提交学生打0分
 * @param {Number} courseId - 课程ID
 * @param {Number} homeworkId - 作业ID
 * @param {Number} studentId - 学生ID
 * @param {Object} data - 包含 ai_feedback 等字段（可选）
 */
export const gradeUnsubmittedStudent = (courseId, homeworkId, studentId, data = {}) =>
  request.post(`/teachers/me/courses/${courseId}/homeworks/${homeworkId}/students/${studentId}/grade-zero`, data);

/**
 * 发布某次作业的成绩（老师全部批改完成后手动提交）
 * @param {Number} courseId - 课程ID
 * @param {Number} homeworkId - 作业ID
 */
export const publishHomeworkGrades = (courseId, homeworkId) =>
  request.post(`/teachers/me/courses/${courseId}/homeworks/${homeworkId}/publish-grades`);

/**
 * 更新教师个人资料
 * @param {Object} data - 包含要更新的字段（name, email, phone）
 */
export const updateTeacherProfile = (data) =>
  request.patch('/teachers/me', data);

/**
 * 修改教师密码
 * @param {Object} data - 包含 old_password 和 new_password
 */
export const updateTeacherPassword = (data) =>
  request.patch('/teachers/me/password', data);
