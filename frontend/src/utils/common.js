/**
 * 通用工具函数
 */

import { ElMessage } from 'element-plus';

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @param {string} successMessage - 成功消息
 */
export const copyToClipboard = async (text, successMessage = '已复制到剪贴板') => {
  try {
    await navigator.clipboard.writeText(text);
    ElMessage.success(successMessage);
    return true;
  } catch (error) {
    // 降级方案：使用传统方法
    try {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.opacity = '0';
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      ElMessage.success(successMessage);
      return true;
    } catch (err) {
      ElMessage.error('复制失败，请手动复制');
      return false;
    }
  }
};

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

/**
 * 高亮文本中的关键词
 * @param {string} text - 原文本
 * @param {string} keyword - 关键词
 */
export const highlightText = (text, keyword) => {
  if (!text || !keyword) return text;
  const regex = new RegExp(`(${keyword})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
};

/**
 * 生成唯一ID
 */
export const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

/**
 * 深度克隆对象
 * @param {any} obj - 要克隆的对象
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (typeof obj === 'object') {
    const cloned = {};
    Object.keys(obj).forEach(key => {
      cloned[key] = deepClone(obj[key]);
    });
    return cloned;
  }
};

/**
 * 防抖函数（Vue 3 Composition API 版本）
 * @param {Function} fn - 要防抖的函数
 * @param {number} delay - 延迟时间（毫秒）
 */
export const useDebounce = (fn, delay = 300) => {
  let timeoutId = null;
  return function debounced(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn.apply(this, args), delay);
  };
};

/**
 * 节流函数（Vue 3 Composition API 版本）
 * @param {Function} fn - 要节流的函数
 * @param {number} limit - 时间限制（毫秒）
 */
export const useThrottle = (fn, limit = 300) => {
  let inThrottle = false;
  return function throttled(...args) {
    if (!inThrottle) {
      fn.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * 检查对象是否为空
 * @param {any} obj - 要检查的对象
 */
export const isEmpty = (obj) => {
  if (obj === null || obj === undefined) return true;
  if (typeof obj === 'string') return obj.trim() === '';
  if (Array.isArray(obj)) return obj.length === 0;
  if (typeof obj === 'object') return Object.keys(obj).length === 0;
  return false;
};

/**
 * 安全的JSON解析
 * @param {string} str - JSON字符串
 * @param {any} defaultValue - 默认值
 */
export const safeJsonParse = (str, defaultValue = null) => {
  try {
    return JSON.parse(str);
  } catch (e) {
    return defaultValue;
  }
};

/**
 * 安全的JSON字符串化
 * @param {any} obj - 要序列化的对象
 * @param {string} defaultValue - 默认值
 */
export const safeJsonStringify = (obj, defaultValue = '') => {
  try {
    return JSON.stringify(obj);
  } catch (e) {
    return defaultValue;
  }
};

/**
 * 获取URL参数
 * @param {string} name - 参数名
 * @param {string} url - URL（可选，默认使用当前URL）
 */
export const getUrlParam = (name, url = window.location.href) => {
  const params = new URLSearchParams(new URL(url).search);
  return params.get(name);
};

/**
 * 设置URL参数
 * @param {string} name - 参数名
 * @param {string} value - 参数值
 */
export const setUrlParam = (name, value) => {
  const url = new URL(window.location.href);
  url.searchParams.set(name, value);
  window.history.pushState({}, '', url);
};

/**
 * 移除URL参数
 * @param {string} name - 参数名
 */
export const removeUrlParam = (name) => {
  const url = new URL(window.location.href);
  url.searchParams.delete(name);
  window.history.pushState({}, '', url);
};

/**
 * 下载文件
 * @param {string} url - 文件URL
 * @param {string} filename - 文件名
 */
export const downloadFile = (url, filename) => {
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * 滚动到元素
 * @param {string|HTMLElement} element - 元素选择器或元素对象
 * @param {Object} options - 滚动选项
 */
export const scrollToElement = (element, options = {}) => {
  const el = typeof element === 'string' 
    ? document.querySelector(element) 
    : element;
  if (el) {
    el.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
      ...options,
    });
  }
};

/**
 * 检查是否在视口中
 * @param {HTMLElement} element - 元素
 */
export const isInViewport = (element) => {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
};

