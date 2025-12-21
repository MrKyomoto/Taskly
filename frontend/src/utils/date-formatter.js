/**
 * 日期时间格式化工具
 */

/**
 * 格式化日期时间
 * @param {string|Date} date - 日期时间
 * @param {string} format - 格式模板，默认 'YYYY-MM-DD HH:mm:ss'
 */
export const formatDateTime = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  if (!date) return '未设置';
  
  const d = date instanceof Date ? date : new Date(date);
  if (isNaN(d.getTime())) return '无效日期';
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
};

/**
 * 格式化日期（不包含时间）
 * @param {string|Date} date - 日期
 */
export const formatDate = (date) => {
  return formatDateTime(date, 'YYYY-MM-DD');
};

/**
 * 格式化时间（不包含日期）
 * @param {string|Date} date - 日期时间
 */
export const formatTime = (date) => {
  return formatDateTime(date, 'HH:mm:ss');
};

/**
 * 相对时间格式化（如：3分钟前、2小时前、昨天）
 * @param {string|Date} date - 日期时间
 */
export const formatRelativeTime = (date) => {
  if (!date) return '未知时间';
  
  const d = date instanceof Date ? date : new Date(date);
  if (isNaN(d.getTime())) return '无效日期';
  
  const now = new Date();
  const diff = now - d;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (seconds < 60) {
    return '刚刚';
  } else if (minutes < 60) {
    return `${minutes}分钟前`;
  } else if (hours < 24) {
    return `${hours}小时前`;
  } else if (days === 1) {
    return '昨天';
  } else if (days < 7) {
    return `${days}天前`;
  } else if (days < 30) {
    const weeks = Math.floor(days / 7);
    return `${weeks}周前`;
  } else if (days < 365) {
    const months = Math.floor(days / 30);
    return `${months}个月前`;
  } else {
    const years = Math.floor(days / 365);
    return `${years}年前`;
  }
};

/**
 * 计算倒计时
 * @param {string|Date} deadline - 截止时间
 * @returns {Object} 包含天、时、分、秒的对象
 */
export const calculateCountdown = (deadline) => {
  if (!deadline) return null;
  
  const d = deadline instanceof Date ? deadline : new Date(deadline);
  if (isNaN(d.getTime())) return null;
  
  const now = new Date();
  const diff = d - now;
  
  if (diff <= 0) {
    return { days: 0, hours: 0, minutes: 0, seconds: 0, expired: true };
  }
  
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);
  
  return { days, hours, minutes, seconds, expired: false };
};

/**
 * 格式化倒计时文本
 * @param {string|Date} deadline - 截止时间
 * @param {boolean} showSeconds - 是否显示秒数
 */
export const formatCountdown = (deadline, showSeconds = false) => {
  const countdown = calculateCountdown(deadline);
  if (!countdown) return '无效时间';
  
  if (countdown.expired) {
    return '已过期';
  }
  
  const parts = [];
  if (countdown.days > 0) {
    parts.push(`${countdown.days}天`);
  }
  if (countdown.hours > 0 || countdown.days > 0) {
    parts.push(`${countdown.hours}小时`);
  }
  if (countdown.minutes > 0 || countdown.hours > 0 || countdown.days > 0) {
    parts.push(`${countdown.minutes}分钟`);
  }
  if (showSeconds) {
    parts.push(`${countdown.seconds}秒`);
  }
  
  return parts.length > 0 ? parts.join(' ') : '即将到期';
};

/**
 * 判断是否在今天
 * @param {string|Date} date - 日期
 */
export const isToday = (date) => {
  if (!date) return false;
  const d = date instanceof Date ? date : new Date(date);
  const today = new Date();
  return d.toDateString() === today.toDateString();
};

/**
 * 判断是否在本周
 * @param {string|Date} date - 日期
 */
export const isThisWeek = (date) => {
  if (!date) return false;
  const d = date instanceof Date ? date : new Date(date);
  const today = new Date();
  const weekStart = new Date(today.setDate(today.getDate() - today.getDay()));
  weekStart.setHours(0, 0, 0, 0);
  const weekEnd = new Date(weekStart);
  weekEnd.setDate(weekEnd.getDate() + 6);
  weekEnd.setHours(23, 59, 59, 999);
  return d >= weekStart && d <= weekEnd;
};

/**
 * 判断是否在本月
 * @param {string|Date} date - 日期
 */
export const isThisMonth = (date) => {
  if (!date) return false;
  const d = date instanceof Date ? date : new Date(date);
  const today = new Date();
  return d.getMonth() === today.getMonth() && d.getFullYear() === today.getFullYear();
};

