/**
 * 前端表单验证工具函数
 */

/**
 * 验证邮箱格式
 * 匹配常见邮箱格式，如：user@example.com, test.email@domain.co.uk
 * @param {string} email - 待验证的邮箱地址
 * @returns {boolean} 验证通过返回 true，否则返回 false
 */
export const validateEmail = (email) => {
  if (!email || typeof email !== 'string') {
    return false;
  }
  // 邮箱正则：允许字母、数字、点、下划线、连字符，@符号前后都有内容，域名部分允许点分隔
  const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email.trim());
};

/**
 * 验证电话号码格式
 * 匹配 +86 开头的 11 位数字格式，如：+8613812345678
 * @param {string} phone - 待验证的电话号码
 * @returns {boolean} 验证通过返回 true，否则返回 false
 */
export const validatePhone = (phone) => {
  if (!phone || typeof phone !== 'string') {
    return false;
  }
  // 电话正则：+86 开头，后面跟 11 位数字
  const phoneRegex = /^\+86\d{11}$/;
  return phoneRegex.test(phone.trim());
};

/**
 * 验证密码强度
 * 密码长度 >= 6，且包含字母/数字/特殊字符中的两类
 * @param {string} password - 待验证的密码
 * @returns {Object} 返回 { isValid: boolean, message: string }
 */
export const validatePassword = (password) => {
  if (!password || typeof password !== 'string') {
    return {
      isValid: false,
      message: '密码不能为空'
    };
  }

  // 检查长度
  if (password.length < 6) {
    return {
      isValid: false,
      message: '密码长度不能少于6位'
    };
  }

  // 检查是否包含字母、数字、特殊字符
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasDigit = /\d/.test(password);
  const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?]/.test(password);

  // 统计包含的字符类型数量
  const typeCount = [hasLetter, hasDigit, hasSpecial].filter(Boolean).length;

  if (typeCount < 2) {
    return {
      isValid: false,
      message: '密码必须包含字母、数字、特殊字符这三类中的至少两类'
    };
  }

  return {
    isValid: true,
    message: '密码格式正确'
  };
};

