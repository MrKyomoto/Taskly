/**
 * UI优化工具函数
 * 用于统一处理字体、对齐、按钮样式等
 */

// 统一字体样式
export const fontStyles = {
  clear: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    fontSize: '14px',
    lineHeight: '1.6',
    color: '#303133',
    fontWeight: '400',
  },
  title: {
    fontSize: '20px',
    fontWeight: '600',
    color: '#303133',
    lineHeight: '1.4',
  },
  subtitle: {
    fontSize: '16px',
    fontWeight: '500',
    color: '#606266',
    lineHeight: '1.5',
  },
  body: {
    fontSize: '14px',
    fontWeight: '400',
    color: '#303133',
    lineHeight: '1.6',
  },
  caption: {
    fontSize: '12px',
    fontWeight: '400',
    color: '#909399',
    lineHeight: '1.5',
  },
};

// 对齐工具
export const alignment = {
  center: {
    textAlign: 'center',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  left: {
    textAlign: 'left',
  },
  right: {
    textAlign: 'right',
    display: 'flex',
    justifyContent: 'flex-end',
  },
};

// 按钮对齐工具
export const buttonAlignment = {
  group: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    justifyContent: 'flex-start',
  },
  groupCenter: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    justifyContent: 'center',
  },
  groupRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    justifyContent: 'flex-end',
  },
};

// 卡片样式优化
export const cardStyles = {
  default: {
    borderRadius: '8px',
    boxShadow: '0 2px 12px 0 rgba(0, 0, 0, 0.1)',
    border: '1px solid #ebeef5',
    padding: '20px',
  },
  hover: {
    transition: 'all 0.3s ease',
    cursor: 'pointer',
  },
};

// 表格样式优化
export const tableStyles = {
  header: {
    fontWeight: '600',
    fontSize: '14px',
    color: '#303133',
    textAlign: 'center',
  },
  cell: {
    fontSize: '14px',
    color: '#606266',
    textAlign: 'center',
  },
};

// 响应式断点
export const breakpoints = {
  xs: '480px',
  sm: '768px',
  md: '1024px',
  lg: '1280px',
  xl: '1920px',
};

