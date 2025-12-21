/**
 * 性能优化工具函数
 */

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间（毫秒）
 * @param {boolean} immediate - 是否立即执行
 */
export const debounce = (func, wait = 300, immediate = false) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) func(...args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func(...args);
  };
};

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 时间限制（毫秒）
 */
export const throttle = (func, limit = 300) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * 延迟执行
 * @param {number} ms - 延迟时间（毫秒）
 */
export const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * 批量处理数据，避免一次性处理大量数据导致UI阻塞
 * @param {Array} items - 要处理的数据数组
 * @param {Function} processor - 处理函数
 * @param {number} batchSize - 每批处理的数量
 * @param {number} delayMs - 每批之间的延迟（毫秒）
 */
export const batchProcess = async (items, processor, batchSize = 10, delayMs = 0) => {
  const results = [];
  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(batch.map(processor));
    results.push(...batchResults);
    if (delayMs > 0 && i + batchSize < items.length) {
      await delay(delayMs);
    }
  }
  return results;
};

/**
 * 虚拟滚动优化 - 计算可见范围
 * @param {number} scrollTop - 滚动位置
 * @param {number} itemHeight - 每项高度
 * @param {number} containerHeight - 容器高度
 * @param {number} totalItems - 总项数
 * @param {number} buffer - 缓冲区大小
 */
export const calculateVisibleRange = (scrollTop, itemHeight, containerHeight, totalItems, buffer = 5) => {
  const start = Math.max(0, Math.floor(scrollTop / itemHeight) - buffer);
  const end = Math.min(totalItems, Math.ceil((scrollTop + containerHeight) / itemHeight) + buffer);
  return { start, end, visibleCount: end - start };
};

/**
 * 图片懒加载优化
 * @param {string} src - 图片源
 * @param {Function} onLoad - 加载完成回调
 * @param {Function} onError - 加载失败回调
 */
export const lazyLoadImage = (src, onLoad, onError) => {
  const img = new Image();
  img.onload = () => onLoad && onLoad(img);
  img.onerror = () => onError && onError();
  img.src = src;
};

/**
 * 内存优化 - 清理未使用的数据
 * @param {Object} data - 数据对象
 * @param {Array} keysToKeep - 要保留的键
 */
export const cleanupData = (data, keysToKeep = []) => {
  if (Array.isArray(data)) {
    return data.map(item => cleanupData(item, keysToKeep));
  }
  if (typeof data === 'object' && data !== null) {
    const cleaned = {};
    keysToKeep.forEach(key => {
      if (key in data) {
        cleaned[key] = data[key];
      }
    });
    return cleaned;
  }
  return data;
};

/**
 * 缓存函数结果
 * @param {Function} fn - 要缓存的函数
 * @param {number} ttl - 缓存时间（毫秒），0表示永久缓存
 */
export const memoize = (fn, ttl = 0) => {
  const cache = new Map();
  return function memoizedFunction(...args) {
    const key = JSON.stringify(args);
    const cached = cache.get(key);
    
    if (cached) {
      if (ttl === 0 || Date.now() - cached.timestamp < ttl) {
        return cached.value;
      }
      cache.delete(key);
    }
    
    const value = fn.apply(this, args);
    cache.set(key, { value, timestamp: Date.now() });
    return value;
  };
};

/**
 * 请求去重 - 防止重复请求
 */
export const requestDeduplicator = () => {
  const pendingRequests = new Map();
  
  return async (key, requestFn) => {
    if (pendingRequests.has(key)) {
      return pendingRequests.get(key);
    }
    
    const promise = requestFn().finally(() => {
      pendingRequests.delete(key);
    });
    
    pendingRequests.set(key, promise);
    return promise;
  };
};

/**
 * 分页加载优化
 * @param {Function} loadFn - 加载函数
 * @param {number} pageSize - 每页大小
 * @param {Object} options - 配置选项
 */
export const createPaginatedLoader = (loadFn, pageSize = 20, options = {}) => {
  const { initialLoad = true, onLoad, onError } = options;
  let currentPage = 0;
  let hasMore = true;
  let loading = false;
  const allData = [];
  
  const loadPage = async () => {
    if (loading || !hasMore) return;
    
    loading = true;
    try {
      const result = await loadFn(currentPage, pageSize);
      const { data, total } = result;
      
      allData.push(...data);
      hasMore = allData.length < total;
      currentPage++;
      
      onLoad && onLoad(allData, hasMore);
    } catch (error) {
      onError && onError(error);
    } finally {
      loading = false;
    }
  };
  
  if (initialLoad) {
    loadPage();
  }
  
  return {
    loadMore: loadPage,
    getData: () => allData,
    reset: () => {
      currentPage = 0;
      hasMore = true;
      allData.length = 0;
      if (initialLoad) loadPage();
    },
    hasMore: () => hasMore,
    isLoading: () => loading,
  };
};

