/**
 * 图片 URL 处理工具函数
 * 处理相对路径和绝对路径的图片 URL
 */

/**
 * 获取完整的图片 URL
 * @param {string} url - 图片 URL（可能是相对路径或绝对路径）
 * @param {boolean} includeToken - 是否在 URL 中包含 token（用于需要认证的图片）
 * @returns {string} 完整的图片 URL
 */
export const getImageUrl = (url, includeToken = false) => {
  if (!url) return '';
  // 如果是对象，尝试提取 image_url 或 url 属性
  if (typeof url === 'object' && url !== null) {
    url = url.image_url || url.url || String(url);
  }
  // 确保是字符串
  url = String(url);
  // 如果已经是完整的 URL（http/https），检查是否需要添加 token
  if (url.startsWith('http://') || url.startsWith('https://')) {
    if (includeToken) {
      const token = localStorage.getItem('token');
      if (token) {
        const separator = url.includes('?') ? '&' : '?';
        return `${url}${separator}token=${encodeURIComponent(token)}`;
      }
    }
    return url;
  }
  // 如果是相对路径，拼接后端基地址
  const baseUrl = 'http://127.0.0.1:5000';
  
  // 处理路径：去掉开头的 uploads/ 前缀（如果存在）
  // 因为路由是 /uploads/<path:filename>，filename 应该是 course/... 格式
  let path = url;
  if (path.startsWith('uploads/')) {
    path = path.substring('uploads/'.length);
  } else if (path.startsWith('/uploads/')) {
    path = path.substring('/uploads/'.length);
  }
  
  // 确保路径以 / 开头，然后加上 /uploads/ 前缀
  path = path.startsWith('/') ? path : `/${path}`;
  let fullUrl = `${baseUrl}/uploads${path}`;
  
  // 如果需要 token，添加到 URL 参数中
  if (includeToken) {
    const token = localStorage.getItem('token');
    if (token) {
      fullUrl = `${fullUrl}?token=${encodeURIComponent(token)}`;
    }
  }
  
  return fullUrl;
};

/**
 * 解析 JSON 字符串格式的图片 URL 数组
 * @param {string|Array} imageUrls - 图片 URL（可能是 JSON 字符串或数组）
 * @returns {Array} 图片 URL 数组
 */
export const parseImageUrls = (imageUrls) => {
  if (!imageUrls) return [];
  if (Array.isArray(imageUrls)) {
    return imageUrls;
  }
  try {
    const parsed = JSON.parse(imageUrls);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

