import api from './index';

export const fetchStudentProfile = () => api.get('/students/me');

export const fetchStudentCourses = () => api.get('/students/me/courses');

export const fetchCourseHomeworks = (courseId) =>
  api.get(`/students/me/courses/${courseId}/homeworks`);

export const fetchHomeworkSubmission = (courseId, homeworkId) =>
  api.get(`/students/me/courses/${courseId}/homeworks/${homeworkId}/submission`);
