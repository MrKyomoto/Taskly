/**
 * 表单验证工具
 * 提供常用的验证规则和验证函数
 */

/**
 * 验证学号/工号格式
 * @param {string} value - 学号/工号
 * @param {number} minLength - 最小长度
 * @param {number} maxLength - 最大长度
 */
export const validateStudentNo = (value, minLength = 6, maxLength = 30) => {
  if (!value) {
    return '请输入学号';
  }
  if (value.length < minLength || value.length > maxLength) {
    return `学号长度应在 ${minLength}-${maxLength} 位之间`;
  }
  if (!/^[a-zA-Z0-9]+$/.test(value)) {
    return '学号只能包含字母和数字';
  }
  return true;
};

/**
 * 验证邮箱格式
 * @param {string} value - 邮箱地址
 */
export const validateEmail = (value) => {
  if (!value) {
    return true; // 邮箱可选
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(value)) {
    return '请输入有效的邮箱地址';
  }
  return true;
};

/**
 * 验证手机号格式
 * @param {string} value - 手机号
 */
export const validatePhone = (value) => {
  if (!value) {
    return true; // 手机号可选
  }
  // 支持国际格式：+86 13800138000 或 13800138000
  const phoneRegex = /^(\+?\d{1,4}[\s-]?)?\d{7,15}$/;
  if (!phoneRegex.test(value.replace(/\s/g, ''))) {
    return '请输入有效的手机号码';
  }
  return true;
};

/**
 * 验证密码强度
 * @param {string} value - 密码
 * @param {number} minLength - 最小长度
 */
export const validatePassword = (value, minLength = 6) => {
  if (!value) {
    return '请输入密码';
  }
  if (value.length < minLength) {
    return `密码长度不能少于 ${minLength} 位`;
  }
  return true;
};

/**
 * 验证课程代码格式
 * @param {string} value - 课程代码
 */
export const validateCourseCode = (value) => {
  if (!value) {
    return '请输入课程代码';
  }
  if (value.length < 3 || value.length > 20) {
    return '课程代码长度应在 3-20 位之间';
  }
  if (!/^[A-Za-z0-9\-_]+$/.test(value)) {
    return '课程代码只能包含字母、数字、连字符和下划线';
  }
  return true;
};

/**
 * 验证分数范围
 * @param {number} value - 分数
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 */
export const validateScore = (value, min = 0, max = 100) => {
  if (value === null || value === undefined || value === '') {
    return '请输入分数';
  }
  const numValue = Number(value);
  if (isNaN(numValue)) {
    return '分数必须是数字';
  }
  if (numValue < min || numValue > max) {
    return `分数应在 ${min}-${max} 之间`;
  }
  return true;
};

/**
 * 验证必填字段
 * @param {any} value - 字段值
 * @param {string} fieldName - 字段名称
 */
export const validateRequired = (value, fieldName = '此字段') => {
  if (value === null || value === undefined || value === '') {
    return `请输入${fieldName}`;
  }
  if (typeof value === 'string' && value.trim() === '') {
    return `请输入${fieldName}`;
  }
  return true;
};

/**
 * 验证日期时间
 * @param {string|Date} value - 日期时间
 * @param {boolean} requireFuture - 是否必须是未来时间
 */
export const validateDateTime = (value, requireFuture = false) => {
  if (!value) {
    return '请选择日期时间';
  }
  const date = new Date(value);
  if (isNaN(date.getTime())) {
    return '请输入有效的日期时间';
  }
  if (requireFuture && date <= new Date()) {
    return '请选择未来的时间';
  }
  return true;
};

/**
 * 验证文件类型
 * @param {File} file - 文件对象
 * @param {Array<string>} allowedTypes - 允许的文件类型（MIME类型或扩展名）
 * @param {number} maxSize - 最大文件大小（MB）
 */
export const validateFile = (file, allowedTypes = [], maxSize = 10) => {
  if (!file) {
    return '请选择文件';
  }

  // 检查文件类型
  if (allowedTypes.length > 0) {
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    const fileType = file.type;
    const isAllowed = allowedTypes.some(type => {
      if (type.startsWith('.')) {
        return fileExtension === type.substring(1);
      }
      return fileType.includes(type);
    });

    if (!isAllowed) {
      return `不支持的文件类型，仅支持: ${allowedTypes.join(', ')}`;
    }
  }

  // 检查文件大小
  const maxSizeBytes = maxSize * 1024 * 1024;
  if (file.size > maxSizeBytes) {
    return `文件大小不能超过 ${maxSize}MB`;
  }

  return true;
};

/**
 * Element Plus 验证规则生成器
 */
export const createRules = {
  required: (message) => [{ required: true, message, trigger: 'blur' }],
  email: (message = '请输入有效的邮箱地址') => [
    { type: 'email', message, trigger: 'blur' },
  ],
  phone: (message = '请输入有效的手机号码') => [
    { validator: (rule, value, callback) => {
      if (!value) {
        callback();
        return;
      }
      const result = validatePhone(value);
      if (result === true) {
        callback();
      } else {
        callback(new Error(result));
      }
    }, trigger: 'blur' },
  ],
  studentNo: (minLength = 6, maxLength = 30) => [
    { validator: (rule, value, callback) => {
      const result = validateStudentNo(value, minLength, maxLength);
      if (result === true) {
        callback();
      } else {
        callback(new Error(result));
      }
    }, trigger: 'blur' },
  ],
  password: (minLength = 6) => [
    { validator: (rule, value, callback) => {
      const result = validatePassword(value, minLength);
      if (result === true) {
        callback();
      } else {
        callback(new Error(result));
      }
    }, trigger: 'blur' },
  ],
  score: (min = 0, max = 100) => [
    { validator: (rule, value, callback) => {
      const result = validateScore(value, min, max);
      if (result === true) {
        callback();
      } else {
        callback(new Error(result));
      }
    }, trigger: 'blur' },
  ],
};

