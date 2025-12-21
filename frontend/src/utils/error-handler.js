/**
 * 统一错误处理工具
 * 提供用户友好的错误提示
 */

import { ElMessage, ElNotification } from 'element-plus';
import { useUserStore } from '@/store/user';
import router from '@/router';

/**
 * 处理API错误
 * @param {Error} error - 错误对象
 * @param {Object} options - 配置选项
 * @param {string} options.defaultMessage - 默认错误消息
 * @param {boolean} options.showNotification - 是否显示通知（默认false，使用Message）
 * @param {boolean} options.autoLogout - 401错误时是否自动登出（默认true）
 */
export const handleApiError = (error, options = {}) => {
  const {
    defaultMessage = '操作失败，请重试',
    showNotification = false,
    autoLogout = true,
  } = options;

  const status = error?.response?.status;
  const errorMessage = error?.response?.data?.error || error?.message || defaultMessage;

  // 401 未授权 - 自动登出
  if (status === 401 && autoLogout) {
    const userStore = useUserStore();
    ElMessage.error('登录已过期，请重新登录');
    userStore.logout();
    router.push({ name: 'Login' });
    return;
  }

  // 403 禁止访问
  if (status === 403) {
    const message = '您没有权限执行此操作';
    if (showNotification) {
      ElNotification({
        title: '权限不足',
        message,
        type: 'warning',
        duration: 3000,
      });
    } else {
      ElMessage.warning(message);
    }
    return;
  }

  // 404 未找到
  if (status === 404) {
    const message = '请求的资源不存在';
    if (showNotification) {
      ElNotification({
        title: '未找到',
        message,
        type: 'warning',
        duration: 3000,
      });
    } else {
      ElMessage.warning(message);
    }
    return;
  }

  // 400 错误请求
  if (status === 400) {
    if (showNotification) {
      ElNotification({
        title: '输入错误',
        message: errorMessage,
        type: 'error',
        duration: 4000,
      });
    } else {
      ElMessage.error(errorMessage);
    }
    return;
  }

  // 500 服务器错误
  if (status === 500) {
    const message = '服务器内部错误，请稍后重试';
    if (showNotification) {
      ElNotification({
        title: '服务器错误',
        message,
        type: 'error',
        duration: 5000,
      });
    } else {
      ElMessage.error(message);
    }
    return;
  }

  // 网络错误
  if (!error.response) {
    const message = '网络连接失败，请检查网络设置';
    if (showNotification) {
      ElNotification({
        title: '网络错误',
        message,
        type: 'error',
        duration: 4000,
      });
    } else {
      ElMessage.error(message);
    }
    return;
  }

  // 其他错误
  if (showNotification) {
    ElNotification({
      title: '操作失败',
      message: errorMessage,
      type: 'error',
      duration: 4000,
    });
  } else {
    ElMessage.error(errorMessage);
  }
};

/**
 * 处理表单验证错误
 * @param {Error} error - 验证错误
 * @param {string} defaultMessage - 默认消息
 */
export const handleValidationError = (error, defaultMessage = '请检查输入内容') => {
  const message = error?.message || defaultMessage;
  ElMessage.warning(message);
};

/**
 * 处理文件上传错误
 * @param {Error} error - 错误对象
 * @param {string} fileName - 文件名
 */
export const handleUploadError = (error, fileName = '') => {
  const status = error?.response?.status;
  let message = '文件上传失败';

  if (status === 413) {
    message = '文件大小超出限制';
  } else if (status === 415) {
    message = '不支持的文件类型';
  } else if (fileName) {
    message = `文件 "${fileName}" 上传失败`;
  }

  ElMessage.error(message);
};

/**
 * 处理批量操作错误
 * @param {Array} errors - 错误数组
 * @param {number} total - 总数
 * @param {number} success - 成功数
 */
export const handleBatchError = (errors, total, success) => {
  if (errors.length === 0) {
    ElMessage.success(`全部 ${total} 项操作成功`);
    return;
  }

  if (success === 0) {
    ElMessage.error(`全部 ${total} 项操作失败`);
    return;
  }

  ElMessage.warning(`成功 ${success} 项，失败 ${errors.length} 项`);
  if (errors.length <= 5) {
    errors.forEach((err, index) => {
      setTimeout(() => {
        ElMessage.error(`第 ${index + 1} 项: ${err.message || err}`);
      }, index * 500);
    });
  }
};

