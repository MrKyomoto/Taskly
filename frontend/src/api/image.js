// 获取完整的图片 URL
export function getImageUrl(path) {
    if (!path) return '';
    
    // 如果已经是完整的 http 开头，直接返回
    if (path.startsWith('http://') || path.startsWith('https://')) {
      return path;
    }
    
    // 这里的基地址要改成你后端的实际地址
    // 开发环境通常是 localhost:5000，生产环境可能是服务器 IP
    const BASE_URL = 'http://127.0.0.1:5000/'; 
    
    // 确保路径不以 / 开头（避免双斜杠）
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    
    return `${BASE_URL}${cleanPath}`;
  }