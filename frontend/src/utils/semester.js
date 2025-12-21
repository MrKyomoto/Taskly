/**
 * 学期相关工具函数
 */

/**
 * 根据当前时间获取当前学期
 * 规则：
 * - 2-6月：春季学期（Spring）
 * - 7-8月：夏季学期（Summer）
 * - 9-1月：秋季学期（Fall）
 * @returns {Object} { year: number, term: 'Spring'|'Summer'|'Fall', semester: string }
 */
export function getCurrentSemester() {
  const now = new Date();
  const month = now.getMonth() + 1; // getMonth() 返回 0-11，所以 +1
  const year = now.getFullYear();
  
  let term;
  let semesterYear = year;
  
  if (month >= 2 && month <= 6) {
    // 2-6月：春季学期
    term = 'Spring';
    semesterYear = year; // 春季学期属于当前年份
  } else if (month >= 7 && month <= 8) {
    // 7-8月：夏季学期
    term = 'Summer';
    semesterYear = year; // 夏季学期属于当前年份
  } else {
    // 9-1月：秋季学期
    term = 'Fall';
    // 如果是9-12月，秋季学期属于当前年份
    // 如果是1月，秋季学期属于上一年（因为秋季学期从9月开始）
    if (month >= 9) {
      semesterYear = year;
    } else {
      semesterYear = year - 1;
    }
  }
  
  return {
    year: semesterYear,
    term: term,
    semester: `${semesterYear}-${term}`
  };
}

/**
 * 判断给定的学期字符串是否是当前学期
 * @param {string} semester - 学期字符串，格式：2024-Fall
 * @returns {boolean}
 */
export function isCurrentSemester(semester) {
  if (!semester) return false;
  const current = getCurrentSemester();
  return semester === current.semester;
}

