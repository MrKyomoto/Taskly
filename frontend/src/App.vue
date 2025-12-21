<template>
  <div id="app" :class="{ 'dark-mode': isDarkMode }">
    <router-view />
  </div>
</template>

<script setup>
import { computed, watch, nextTick } from 'vue';
import { usePersonalizationStore } from '@/store/personalization';

const personalizationStore = usePersonalizationStore();

const isDarkMode = computed(() => personalizationStore.darkMode);

// 监听暗夜模式变化，确保样式正确应用
watch(isDarkMode, (newValue) => {
  // 当暗夜模式关闭时，确保页面样式正确还原
  if (!newValue) {
    // 强制触发样式更新
    document.documentElement.classList.remove('dark-mode');
    const appElement = document.getElementById('app');
    if (appElement) {
      appElement.classList.remove('dark-mode');
    }
    // 强制更新个性化设置，确保所有颜色都恢复为白色
    // 使用 nextTick 确保 DOM 更新后再触发
    nextTick(() => {
      // 确保 store 中的值被正确重置
      if (personalizationStore.backgroundColor !== '#ffffff') {
        personalizationStore.backgroundColor = '#ffffff';
      }
      // 确保所有模块的颜色都被重置
      Object.keys(personalizationStore.modules).forEach(moduleName => {
        const module = personalizationStore.modules[moduleName];
        if (module.backgroundColor !== '#ffffff') {
          personalizationStore.updateModule(moduleName, {
            backgroundColor: '#ffffff',
            textColor: '#303133',
            borderColor: moduleName === 'card' ? '#ebeef5' : undefined,
          });
        }
      });
    });
  } else {
    // 启用暗夜模式时，确保 dark-mode 类被添加
    document.documentElement.classList.add('dark-mode');
    const appElement = document.getElementById('app');
    if (appElement) {
      appElement.classList.add('dark-mode');
    }
  }
}, { immediate: true });
</script>

<style>
/* 默认亮色模式样式 - 所有区域都是白色 */
#app {
  color: #303133;
  background-color: #ffffff;
}

/* 确保当没有 dark-mode 类时，所有元素都是白色 */
#app:not(.dark-mode) {
  color: #303133 !important;
  background-color: #ffffff !important;
}

/* 全局暗夜模式样式 */
#app.dark-mode {
  /* 基础颜色变量 */
  --dark-bg-primary: #1a1a1a;
  --dark-bg-secondary: #2d2d2d;
  --dark-bg-tertiary: #252525;
  --dark-text-primary: #e5e5e5;
  --dark-text-secondary: #b0b0b0;
  --dark-text-tertiary: #909399;
  --dark-border: #404040;
  --dark-border-light: #505050;
  --dark-hover: #3a3a3a;
  --dark-active: #4a4a4a;
}

/* 暗夜模式下的全局样式 */
#app.dark-mode {
  color: var(--dark-text-primary);
  background-color: var(--dark-bg-primary);
}

/* Element Plus 组件暗夜模式样式 */
#app.dark-mode .el-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-card__header {
  border-bottom-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-input__wrapper {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

/* 确保 el-select 的样式优先级高于通用 el-input__wrapper - 使用 background 和 border 属性 */
#app.dark-mode .el-select .el-input__wrapper,
#app.dark-mode .el-select--small .el-input__wrapper,
#app.dark-mode .el-select.is-small .el-input__wrapper,
#app.dark-mode .gantt-controls .el-select .el-input__wrapper,
#app.dark-mode .gantt-header .gantt-controls .el-select .el-input__wrapper {
  background-color: #252525 !important;
  background: #252525 !important;
  border-color: #404040 !important;
  border: 1px solid #404040 !important;
  box-shadow: none !important;
}

#app.dark-mode .el-input__inner {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-input__inner::placeholder {
  color: var(--dark-text-tertiary) !important;
}

#app.dark-mode .el-textarea__inner {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* ========== 下拉选择框暗夜模式 - 全面覆盖（使用具体颜色值） ========== */
#app.dark-mode .el-select {
  background-color: transparent !important;
}


#app.dark-mode .el-select .el-input__wrapper .el-input__inner,
#app.dark-mode .el-select--small .el-input__wrapper .el-input__inner,
#app.dark-mode .el-select.is-small .el-input__wrapper .el-input__inner {
  background-color: transparent !important;
}

#app.dark-mode .el-select .el-input__inner {
  background-color: transparent !important;
  color: #e5e5e5 !important;
}

#app.dark-mode .el-select .el-input__inner::placeholder {
  color: #909399 !important;
}

#app.dark-mode .el-select .el-input__suffix {
  color: #e5e5e5 !important;
}

#app.dark-mode .el-select .el-input__suffix-inner .el-icon {
  color: #e5e5e5 !important;
}

#app.dark-mode .el-select:hover .el-input__wrapper {
  background-color: #3a3a3a !important;
  border-color: #409EFF !important;
}

#app.dark-mode .el-select.is-focus .el-input__wrapper {
  background-color: #3a3a3a !important;
  border-color: #409EFF !important;
}

#app.dark-mode .el-select.is-disabled .el-input__wrapper {
  background-color: var(--dark-bg-tertiary) !important;
  opacity: 0.6;
}

#app.dark-mode .el-select.is-disabled .el-input__inner {
  color: var(--dark-text-tertiary) !important;
}

/* 下拉菜单容器（使用具体颜色值） */
#app.dark-mode .el-select-dropdown {
  background-color: #2d2d2d !important;
  border-color: #404040 !important;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.5) !important;
}

/* 下拉菜单选项（使用具体颜色值） */
#app.dark-mode .el-select-dropdown__item {
  background-color: #2d2d2d !important;
  color: #e5e5e5 !important;
}

#app.dark-mode .el-select-dropdown__item:hover {
  background-color: #3a3a3a !important;
  color: #e5e5e5 !important;
}

#app.dark-mode .el-select-dropdown__item.selected {
  background-color: rgba(64, 158, 255, 0.2) !important;
  color: #409EFF !important;
  font-weight: 500;
}

#app.dark-mode .el-select-dropdown__item.is-disabled {
  color: var(--dark-text-tertiary) !important;
  cursor: not-allowed;
}

#app.dark-mode .el-select-dropdown__item.is-disabled:hover {
  background-color: var(--dark-bg-secondary) !important;
}

/* 下拉菜单空状态 */
#app.dark-mode .el-select-dropdown__empty {
  color: var(--dark-text-secondary) !important;
}

/* 下拉菜单分组标题 */
#app.dark-mode .el-select-group__title {
  color: var(--dark-text-secondary) !important;
  background-color: var(--dark-bg-tertiary) !important;
}

/* 下拉菜单分隔线 */
#app.dark-mode .el-select-dropdown__item.is-disabled {
  border-top-color: var(--dark-border) !important;
}

#app.dark-mode .el-table {
  background-color: var(--dark-bg-secondary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-table th.el-table__cell {
  background-color: var(--dark-bg-tertiary) !important;
  color: var(--dark-text-primary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-table td.el-table__cell {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* 确保所有表格行（包括普通行和stripe行）都是深色背景 */
#app.dark-mode .el-table__body tr td {
  background-color: var(--dark-bg-secondary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-table--striped .el-table__body tr.el-table__row--striped td {
  background-color: var(--dark-bg-tertiary) !important;
}

/* 覆盖stripe效果，让所有行都是深色 */
#app.dark-mode .el-table--striped .el-table__body tr:not(.el-table__row--striped) td {
  background-color: var(--dark-bg-secondary) !important;
}

#app.dark-mode .el-table__body tr:hover > td {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .el-menu {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-menu-item {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-menu-item:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .el-menu-item.is-active {
  color: #409EFF !important;
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .el-sub-menu__title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-sub-menu__title:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .el-tabs__item {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .el-tabs__item.is-active {
  color: #409EFF !important;
}

#app.dark-mode .el-tabs__nav-wrap::after {
  background-color: var(--dark-border) !important;
}

#app.dark-mode .el-tabs__active-bar {
  background-color: #409EFF !important;
}

#app.dark-mode .el-button {
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-button:not(.el-button--primary):not(.el-button--success):not(.el-button--warning):not(.el-button--danger):not(.el-button--info) {
  background-color: var(--dark-bg-tertiary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-button.is-plain {
  background-color: transparent !important;
}

#app.dark-mode .el-button--text {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-button--text:hover {
  color: #409EFF !important;
}

#app.dark-mode .el-dialog {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-dialog__header {
  border-bottom-color: var(--dark-border) !important;
}

#app.dark-mode .el-dialog__title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-drawer {
  background-color: var(--dark-bg-secondary) !important;
}

#app.dark-mode .el-drawer__header {
  border-bottom-color: var(--dark-border) !important;
}

#app.dark-mode .el-drawer__title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-form-item__label {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-empty__description {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .el-statistic__number {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-statistic__head {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .el-skeleton {
  background-color: var(--dark-bg-tertiary) !important;
}

#app.dark-mode .el-skeleton__item {
  background: linear-gradient(90deg, var(--dark-bg-tertiary) 25%, var(--dark-hover) 37%, var(--dark-bg-tertiary) 63%) !important;
}

#app.dark-mode .el-dropdown-menu {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-dropdown-menu__item {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-dropdown-menu__item:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .el-timeline {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-timeline-item__timestamp {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .el-calendar {
  background-color: var(--dark-bg-secondary) !important;
}

#app.dark-mode .el-calendar__header {
  border-bottom-color: var(--dark-border) !important;
}

#app.dark-mode .el-calendar-table thead th {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .el-calendar-table td {
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-calendar-day {
  background-color: var(--dark-bg-tertiary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-calendar-day:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .el-image-viewer__wrapper {
  background-color: rgba(0, 0, 0, 0.9) !important;
}

/* 自定义组件暗夜模式样式 */
#app.dark-mode .course-card,
#app.dark-mode .homework-item,
#app.dark-mode .search-result-item {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-card:hover,
#app.dark-mode .homework-item:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .section-title,
#app.dark-mode .card-title,
#app.dark-mode h1,
#app.dark-mode h2,
#app.dark-mode h3,
#app.dark-mode h4 {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .welcome-name,
#app.dark-mode .welcome-semester,
#app.dark-mode .student-name {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .stat-label,
#app.dark-mode .stat-value {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .stat-block {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .course-count,
#app.dark-mode .homework-count {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .dropdown-trigger {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .dropdown-trigger:hover {
  background-color: var(--dark-hover) !important;
}

/* 链接和文本颜色 */
#app.dark-mode a {
  color: #409EFF !important;
}

#app.dark-mode a:hover {
  color: #66b1ff !important;
}

/* 滚动条样式 */
#app.dark-mode ::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

#app.dark-mode ::-webkit-scrollbar-track {
  background: var(--dark-bg-primary);
}

#app.dark-mode ::-webkit-scrollbar-thumb {
  background: var(--dark-border);
  border-radius: 4px;
}

#app.dark-mode ::-webkit-scrollbar-thumb:hover {
  background: var(--dark-border-light);
}

/* 更多组件暗夜模式样式 */
#app.dark-mode .el-radio__label,
#app.dark-mode .el-checkbox__label {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-radio__input.is-checked .el-radio__inner,
#app.dark-mode .el-checkbox__input.is-checked .el-checkbox__inner {
  background-color: #409EFF !important;
  border-color: #409EFF !important;
}

#app.dark-mode .el-switch__label {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-switch__core {
  background-color: var(--dark-border) !important;
}

#app.dark-mode .el-switch.is-checked .el-switch__core {
  background-color: #409EFF !important;
}

#app.dark-mode .el-pagination {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-pagination button {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-pagination button:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .el-pagination .el-pager li {
  background-color: var(--dark-bg-tertiary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-pagination .el-pager li:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .el-pagination .el-pager li.is-active {
  background-color: #409EFF !important;
  color: #fff !important;
}

#app.dark-mode .el-tag {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-tag.el-tag--info {
  background-color: rgba(64, 158, 255, 0.15) !important;
  border-color: rgba(64, 158, 255, 0.3) !important;
  color: #66B1FF !important;
}

#app.dark-mode .el-tag.el-tag--success {
  background-color: rgba(103, 194, 58, 0.15) !important;
  border-color: rgba(103, 194, 58, 0.3) !important;
  color: #85CE61 !important;
}

#app.dark-mode .el-tag.el-tag--warning {
  background-color: rgba(230, 162, 60, 0.15) !important;
  border-color: rgba(230, 162, 60, 0.3) !important;
  color: #FFB84D !important;
}

#app.dark-mode .el-tag.el-tag--danger {
  background-color: rgba(245, 108, 108, 0.15) !important;
  border-color: rgba(245, 108, 108, 0.3) !important;
  color: #F78989 !important;
}

#app.dark-mode .el-divider {
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-divider__text {
  background-color: var(--dark-bg-secondary) !important;
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .el-badge__content {
  background-color: #F56C6C !important;
  border-color: #F56C6C !important;
}

#app.dark-mode .el-progress-bar__outer {
  background-color: var(--dark-bg-tertiary) !important;
}

#app.dark-mode .el-progress__text {
  color: var(--dark-text-primary) !important;
}

/* 自定义元素暗夜模式 */
#app.dark-mode .course-cover {
  background: linear-gradient(135deg, var(--dark-bg-tertiary), var(--dark-hover)) !important;
}

#app.dark-mode .gantt-card,
#app.dark-mode .insights-card,
#app.dark-mode .history-card,
#app.dark-mode .calendar-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .gantt-timeline-header {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .gantt-bar {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .gantt-label {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .gantt-label-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .gantt-label-course,
#app.dark-mode .gantt-label-deadline {
  color: var(--dark-text-secondary) !important;
}

/* 甘特图暗夜模式 - 小字体和提示 */
#app.dark-mode .gantt-help-icon {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .gantt-help-icon:hover {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .gantt-intro {
  background: linear-gradient(135deg, var(--dark-bg-tertiary) 0%, var(--dark-hover) 100%) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .intro-text {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .gantt-legend {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .legend-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .legend-text {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .legend-item {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .timeline-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .tick-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .tick-line {
  background-color: var(--dark-border) !important;
}

#app.dark-mode .today-label {
  color: var(--dark-text-primary) !important;
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .today-line {
  background-color: #f56c6c !important;
}

#app.dark-mode .gantt-today-line {
  background-color: #f56c6c !important;
}

#app.dark-mode .gantt-bar-content {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .gantt-bar-deadline {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .gantt-footer {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .gantt-stats {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .filter-hint {
  color: var(--dark-text-tertiary) !important;
}

#app.dark-mode .gantt-controls .el-select,
#app.dark-mode .gantt-controls .el-button-group {
  color: var(--dark-text-primary) !important;
}

/* 甘特图按钮组暗夜模式优化 */
#app.dark-mode .gantt-controls .el-button-group .el-button {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .gantt-controls .el-button-group .el-button:hover {
  background-color: var(--dark-hover) !important;
  border-color: #409EFF !important;
  color: #409EFF !important;
}

#app.dark-mode .gantt-controls .el-button-group .el-button.is-active,
#app.dark-mode .gantt-controls .el-button-group .el-button[type="primary"] {
  background-color: #409EFF !important;
  border-color: #409EFF !important;
  color: #ffffff !important;
}

#app.dark-mode .gantt-controls .el-button-group .el-button[type="primary"]:hover {
  background-color: #66b1ff !important;
  border-color: #66b1ff !important;
  color: #ffffff !important;
}

/* 甘特图选择框暗夜模式优化 - 确保深色背景和亮色文字（使用完整路径和具体颜色值） */
#app.dark-mode .gantt-controls .el-select,
#app.dark-mode .gantt-header .gantt-controls .el-select,
#app.dark-mode .insights-content .gantt-controls .el-select,
#app.dark-mode .gantt-card .gantt-controls .el-select,
#app.dark-mode .gantt-card .gantt-header .gantt-controls .el-select,
#app.dark-mode .insights-card .insights-content .gantt-card .gantt-header .gantt-controls .el-select,
#app.dark-mode .insights-card .gantt-card .gantt-header .gantt-controls .el-select {
  background-color: transparent !important;
}

#app.dark-mode .gantt-controls .el-select .el-input__wrapper,
#app.dark-mode .gantt-header .gantt-controls .el-select .el-input__wrapper,
#app.dark-mode .insights-content .gantt-controls .el-select .el-input__wrapper,
#app.dark-mode .gantt-card .gantt-controls .el-select .el-input__wrapper,
#app.dark-mode .gantt-card .gantt-header .gantt-controls .el-select .el-input__wrapper,
#app.dark-mode .insights-card .insights-content .gantt-card .gantt-header .gantt-controls .el-select .el-input__wrapper,
#app.dark-mode .insights-card .gantt-card .gantt-header .gantt-controls .el-select .el-input__wrapper {
  background-color: #252525 !important;
  border-color: #404040 !important;
  box-shadow: none !important;
}

#app.dark-mode .gantt-controls .el-select .el-input,
#app.dark-mode .gantt-header .gantt-controls .el-select .el-input,
#app.dark-mode .insights-content .gantt-controls .el-select .el-input,
#app.dark-mode .gantt-card .gantt-controls .el-select .el-input,
#app.dark-mode .gantt-card .gantt-header .gantt-controls .el-select .el-input {
  background-color: transparent !important;
}

#app.dark-mode .gantt-controls .el-select .el-input__inner,
#app.dark-mode .gantt-header .gantt-controls .el-select .el-input__inner,
#app.dark-mode .insights-content .gantt-controls .el-select .el-input__inner,
#app.dark-mode .gantt-card .gantt-controls .el-select .el-input__inner,
#app.dark-mode .gantt-card .gantt-header .gantt-controls .el-select .el-input__inner,
#app.dark-mode .insights-card .insights-content .gantt-card .gantt-header .gantt-controls .el-select .el-input__inner,
#app.dark-mode .insights-card .gantt-card .gantt-header .gantt-controls .el-select .el-input__inner {
  background-color: transparent !important;
  color: #e5e5e5 !important;
}

#app.dark-mode .gantt-controls .el-select .el-input__inner::placeholder,
#app.dark-mode .gantt-header .gantt-controls .el-select .el-input__inner::placeholder,
#app.dark-mode .insights-content .gantt-controls .el-select .el-input__inner::placeholder,
#app.dark-mode .gantt-card .gantt-controls .el-select .el-input__inner::placeholder,
#app.dark-mode .gantt-card .gantt-header .gantt-controls .el-select .el-input__inner::placeholder {
  color: #909399 !important;
}

#app.dark-mode .gantt-controls .el-select .el-input__suffix,
#app.dark-mode .gantt-header .gantt-controls .el-select .el-input__suffix,
#app.dark-mode .insights-content .gantt-controls .el-select .el-input__suffix,
#app.dark-mode .gantt-card .gantt-controls .el-select .el-input__suffix,
#app.dark-mode .gantt-card .gantt-header .gantt-controls .el-select .el-input__suffix {
  color: #e5e5e5 !important;
}

#app.dark-mode .gantt-controls .el-select .el-input__suffix-inner,
#app.dark-mode .gantt-header .gantt-controls .el-select .el-input__suffix-inner,
#app.dark-mode .insights-content .gantt-controls .el-select .el-input__suffix-inner,
#app.dark-mode .gantt-card .gantt-controls .el-select .el-input__suffix-inner,
#app.dark-mode .gantt-card .gantt-header .gantt-controls .el-select .el-input__suffix-inner {
  color: #e5e5e5 !important;
}

#app.dark-mode .gantt-controls .el-select .el-input__suffix-inner .el-icon,
#app.dark-mode .gantt-header .gantt-controls .el-select .el-input__suffix-inner .el-icon,
#app.dark-mode .insights-content .gantt-controls .el-select .el-input__suffix-inner .el-icon,
#app.dark-mode .gantt-card .gantt-controls .el-select .el-input__suffix-inner .el-icon,
#app.dark-mode .gantt-card .gantt-header .gantt-controls .el-select .el-input__suffix-inner .el-icon {
  color: #e5e5e5 !important;
}

#app.dark-mode .gantt-controls .el-select:hover .el-input__wrapper,
#app.dark-mode .gantt-header .gantt-controls .el-select:hover .el-input__wrapper,
#app.dark-mode .insights-content .gantt-controls .el-select:hover .el-input__wrapper,
#app.dark-mode .gantt-card .gantt-controls .el-select:hover .el-input__wrapper,
#app.dark-mode .gantt-card .gantt-header .gantt-controls .el-select:hover .el-input__wrapper {
  background-color: #3a3a3a !important;
  border-color: #409EFF !important;
}

#app.dark-mode .gantt-controls .el-select.is-focus .el-input__wrapper,
#app.dark-mode .gantt-header .gantt-controls .el-select.is-focus .el-input__wrapper,
#app.dark-mode .insights-content .gantt-controls .el-select.is-focus .el-input__wrapper,
#app.dark-mode .gantt-card .gantt-controls .el-select.is-focus .el-input__wrapper,
#app.dark-mode .gantt-card .gantt-header .gantt-controls .el-select.is-focus .el-input__wrapper {
  background-color: #3a3a3a !important;
  border-color: #409EFF !important;
}

#app.dark-mode .gantt-controls .el-select.is-disabled .el-input__wrapper,
#app.dark-mode .gantt-header .gantt-controls .el-select.is-disabled .el-input__wrapper,
#app.dark-mode .insights-content .gantt-controls .el-select.is-disabled .el-input__wrapper,
#app.dark-mode .gantt-card .gantt-controls .el-select.is-disabled .el-input__wrapper,
#app.dark-mode .gantt-card .gantt-header .gantt-controls .el-select.is-disabled .el-input__wrapper {
  background-color: #252525 !important;
  opacity: 0.6;
}

/* 甘特图选择框下拉菜单暗夜模式 - 确保深色背景（使用更高优先级和具体颜色值） */
#app.dark-mode .gantt-controls .el-select-dropdown,
#app.dark-mode .gantt-header .gantt-controls .el-select-dropdown,
#app.dark-mode .insights-content .gantt-controls .el-select-dropdown,
#app.dark-mode .el-select-dropdown[data-popper-placement] {
  background-color: #2d2d2d !important;
  border-color: #404040 !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4) !important;
}

#app.dark-mode .gantt-controls .el-select-dropdown__item,
#app.dark-mode .gantt-header .gantt-controls .el-select-dropdown__item,
#app.dark-mode .insights-content .gantt-controls .el-select-dropdown__item,
#app.dark-mode .el-select-dropdown__item {
  background-color: #2d2d2d !important;
  color: #e5e5e5 !important;
}

#app.dark-mode .gantt-controls .el-select-dropdown__item:hover,
#app.dark-mode .gantt-header .gantt-controls .el-select-dropdown__item:hover,
#app.dark-mode .insights-content .gantt-controls .el-select-dropdown__item:hover,
#app.dark-mode .el-select-dropdown__item:hover {
  background-color: #3a3a3a !important;
  color: #e5e5e5 !important;
}

#app.dark-mode .gantt-controls .el-select-dropdown__item.selected,
#app.dark-mode .gantt-header .gantt-controls .el-select-dropdown__item.selected,
#app.dark-mode .insights-content .gantt-controls .el-select-dropdown__item.selected,
#app.dark-mode .el-select-dropdown__item.selected {
  background-color: rgba(64, 158, 255, 0.2) !important;
  color: #409EFF !important;
  font-weight: 500;
}

#app.dark-mode .gantt-controls .el-select-dropdown__item.is-disabled,
#app.dark-mode .gantt-header .gantt-controls .el-select-dropdown__item.is-disabled,
#app.dark-mode .insights-content .gantt-controls .el-select-dropdown__item.is-disabled,
#app.dark-mode .el-select-dropdown__item.is-disabled {
  color: #909399 !important;
  opacity: 0.5;
}

#app.dark-mode .gantt-row:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .gantt-bar-container {
  background-color: var(--dark-bg-tertiary) !important;
}

#app.dark-mode .gantt-chart {
  background-color: transparent !important;
}

#app.dark-mode .gantt-wrapper {
  color: var(--dark-text-primary) !important;
}

/* 甘特图状态条暗夜模式 */
#app.dark-mode .gantt-bar.status-pending {
  background-color: #409EFF !important;
  opacity: 0.8;
}

#app.dark-mode .gantt-bar.status-due-soon {
  background-color: #E6A23C !important;
  opacity: 0.8;
}

#app.dark-mode .gantt-bar.status-overdue {
  background-color: #F56C6C !important;
  opacity: 0.8;
}

#app.dark-mode .gantt-bar.status-submitted {
  background-color: #67C23A !important;
  opacity: 0.8;
}

#app.dark-mode .gantt-bar.status-completed {
  background-color: #909399 !important;
  opacity: 0.8;
}

#app.dark-mode .calendar-cell {
  background-color: var(--dark-bg-tertiary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .calendar-cell:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .calendar-assignment-item {
  background-color: var(--dark-bg-secondary) !important;
  color: var(--dark-text-primary) !important;
}

/* 老师端课程号暗夜模式样式 */
#app.dark-mode .hero-code-pill {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid var(--dark-border) !important;
}

#app.dark-mode .hero-code-pill:hover {
  background: rgba(255, 255, 255, 0.25) !important;
}

#app.dark-mode .code-label {
  color: var(--dark-text-secondary) !important;
  opacity: 1 !important;
}

#app.dark-mode .code-value {
  color: var(--dark-text-primary) !important;
  font-weight: 700 !important;
}

#app.dark-mode .hero-text {
  color: var(--dark-text-secondary) !important;
  opacity: 1 !important;
}

#app.dark-mode .course-code-section {
  background: linear-gradient(135deg, var(--dark-bg-tertiary) 0%, var(--dark-hover) 100%) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .course-code-section:hover {
  background: linear-gradient(135deg, var(--dark-hover) 0%, var(--dark-active) 100%) !important;
  border-color: var(--dark-border-light) !important;
}

#app.dark-mode .course-code-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .course-code-value {
  color: #409EFF !important;
}

/* 老师端课程详情页暗夜模式样式 */
#app.dark-mode .teacher-course-detail {
  background-color: var(--dark-bg-primary) !important;
}

#app.dark-mode .teacher-course-detail .header {
  background-color: var(--dark-bg-secondary) !important;
  border-bottom-color: var(--dark-border) !important;
}

#app.dark-mode .teacher-course-detail .header-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .teacher-course-detail .course-detail-container {
  background-color: transparent !important;
}

#app.dark-mode .teacher-course-detail .course-hero {
  background: linear-gradient(135deg, var(--dark-bg-secondary) 0%, #2d4a7c 100%) !important;
  border: 1px solid var(--dark-border) !important;
}

#app.dark-mode .teacher-course-detail .hero-breadcrumb {
  color: var(--dark-text-secondary) !important;
  opacity: 1 !important;
}

#app.dark-mode .teacher-course-detail .hero-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .teacher-course-detail .course-hero-right .el-statistic .el-statistic__title {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .teacher-course-detail .course-hero-right .el-statistic .el-statistic__content {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .teacher-course-detail .task-item {
  background-color: var(--dark-bg-secondary) !important;
  border: 1px solid var(--dark-border) !important;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2) !important;
}

#app.dark-mode .teacher-course-detail .task-item:hover {
  background-color: var(--dark-hover) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}

#app.dark-mode .teacher-course-detail .task-icon {
  color: #409EFF !important;
}

#app.dark-mode .teacher-course-detail .task-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .teacher-course-detail .task-title:hover {
  color: #409EFF !important;
}

#app.dark-mode .teacher-course-detail .task-meta-row {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .teacher-course-detail .task-deadline {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .teacher-course-detail .task-sub-info {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .teacher-course-detail .toolbar-search .el-input__inner {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .teacher-course-detail .toolbar-search .el-input__inner::placeholder {
  color: var(--dark-text-tertiary) !important;
}

#app.dark-mode .teacher-course-detail .el-empty {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .teacher-course-detail .el-empty__description {
  color: var(--dark-text-secondary) !important;
}

/* 助教信息卡片暗夜模式 */
#app.dark-mode .teacher-course-detail .ta-section-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .teacher-course-detail .ta-card-item {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .teacher-course-detail .ta-card-item:hover {
  background-color: var(--dark-hover) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .teacher-course-detail .ta-card-header-info {
  border-bottom-color: var(--dark-border) !important;
}

#app.dark-mode .teacher-course-detail .ta-name {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .teacher-course-detail .ta-student-no {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .teacher-course-detail .ta-detail-icon {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .teacher-course-detail .ta-detail-text {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .teacher-course-detail .ta-no-contact {
  color: var(--dark-text-tertiary) !important;
}

/* 学生端课程详情页暗夜模式 */
#app.dark-mode .course-detail {
  background-color: var(--dark-bg-primary) !important;
}

#app.dark-mode .course-detail .header {
  background-color: var(--dark-bg-secondary) !important;
  border-bottom-color: var(--dark-border) !important;
}

#app.dark-mode .course-detail .header-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-detail .course-info-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .course-detail .course-info h2 {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-detail .course-code {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .course-detail .course-announcement {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-detail .homework-list-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .course-detail .card-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-detail .homework-item {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .course-detail .homework-item:hover {
  background-color: var(--dark-hover) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .course-detail .homework-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-detail .homework-meta-row {
  color: var(--dark-text-secondary) !important;
}

/* 学生端教师和助教信息卡片暗夜模式 */
#app.dark-mode .course-detail .teacher-section-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-detail .teacher-card-item {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .course-detail .teacher-card-item:hover {
  background-color: var(--dark-hover) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .course-detail .teacher-card-header-info {
  border-bottom-color: var(--dark-border) !important;
}

#app.dark-mode .course-detail .teacher-name {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-detail .teacher-staff-no {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .course-detail .teacher-detail-icon {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .course-detail .teacher-detail-text {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-detail .teacher-no-contact {
  color: var(--dark-text-tertiary) !important;
}

#app.dark-mode .search-results-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .search-result-item {
  background-color: var(--dark-bg-tertiary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .search-result-item:hover {
  background-color: var(--dark-hover) !important;
}

/* 批改中心暗夜模式样式 */
#app.dark-mode .grading-view {
  background-color: var(--dark-bg-primary) !important;
}

#app.dark-mode .grading-header {
  background-color: var(--dark-bg-secondary) !important;
  border-bottom-color: var(--dark-border) !important;
}

#app.dark-mode .header-back-btn {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .header-back-btn:hover {
  color: #409EFF !important;
}

#app.dark-mode .header-current-student {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .header-right {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .grading-container {
  background-color: var(--dark-bg-primary) !important;
}

#app.dark-mode .student-list-panel {
  background-color: var(--dark-bg-secondary) !important;
  border-right-color: var(--dark-border) !important;
}

#app.dark-mode .filter-section {
  border-bottom-color: var(--dark-border) !important;
}

#app.dark-mode .student-item {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .student-item:hover {
  background-color: var(--dark-hover) !important;
  border-color: #409EFF !important;
}

#app.dark-mode .student-item.active {
  background: linear-gradient(135deg, var(--dark-bg-tertiary) 0%, var(--dark-hover) 100%) !important;
  border-color: #409EFF !important;
}

#app.dark-mode .student-name {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .student-no {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .content-panel {
  background-color: var(--dark-bg-primary) !important;
}

#app.dark-mode .card-header {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .text-content {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .text-reference-content {
  background-color: var(--dark-bg-tertiary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .grading-panel {
  background-color: var(--dark-bg-secondary) !important;
  border-left-color: var(--dark-border) !important;
}

#app.dark-mode .student-name-large {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .student-no-small {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .grader-info {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .form-label {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .form-hint {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .image-stage {
  background-color: var(--dark-bg-tertiary) !important;
}

#app.dark-mode .image-stage-item {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

/* 输入框组暗夜模式 */
#app.dark-mode .el-input-group__prepend,
#app.dark-mode .el-input-group__append {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* 日期选择器暗夜模式 */
#app.dark-mode .el-date-editor {
  background-color: var(--dark-bg-tertiary) !important;
}

#app.dark-mode .el-picker-panel {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-picker-panel__content {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-date-table td.available:hover {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-date-table td.current:not(.disabled) span {
  background-color: #409EFF !important;
  color: #fff !important;
}

/* 消息提示暗夜模式 */
#app.dark-mode .el-message {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-message-box {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-message-box__title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-message-box__message {
  color: var(--dark-text-secondary) !important;
}

/* 对话框暗夜模式 */
#app.dark-mode .el-dialog {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-dialog__header {
  border-bottom-color: var(--dark-border) !important;
}

#app.dark-mode .el-dialog__title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-dialog__body {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-dialog__footer {
  border-top-color: var(--dark-border) !important;
}

/* 表单暗夜模式 */
#app.dark-mode .el-form-item__label {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-form-item__error {
  color: #f56c6c !important;
}

/* 数字输入框暗夜模式 */
#app.dark-mode .el-input-number {
  background-color: var(--dark-bg-tertiary) !important;
}

#app.dark-mode .el-input-number .el-input__wrapper {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-input-number .el-input__inner {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-input-number__increase,
#app.dark-mode .el-input-number__decrease {
  background-color: var(--dark-bg-tertiary) !important;
  color: var(--dark-text-primary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-input-number__increase:hover,
#app.dark-mode .el-input-number__decrease:hover {
  color: #409EFF !important;
}

#app.dark-mode .el-input-number.is-disabled .el-input__wrapper {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

/* 学期选择组暗夜模式 */
#app.dark-mode .semester-select-group {
  color: var(--dark-text-primary) !important;
}

/* 加载状态暗夜模式 */
#app.dark-mode .el-loading-mask {
  background-color: rgba(26, 26, 26, 0.8) !important;
}

/* 工具提示暗夜模式 */
#app.dark-mode .el-tooltip__popper {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* 图片预览暗夜模式 */
#app.dark-mode .el-image-viewer__close {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-image-viewer__actions {
  background-color: rgba(45, 45, 45, 0.8) !important;
}

/* 骨架屏暗夜模式 */
#app.dark-mode .el-skeleton__text,
#app.dark-mode .el-skeleton__h1,
#app.dark-mode .el-skeleton__h3 {
  background: linear-gradient(90deg, var(--dark-bg-tertiary) 25%, var(--dark-hover) 37%, var(--dark-bg-tertiary) 63%) !important;
}

/* 确保所有文本在暗夜模式下可见 */
#app.dark-mode * {
  color: inherit;
}

/* 特殊处理：确保某些元素在暗夜模式下有正确的颜色 */
#app.dark-mode .text-muted,
#app.dark-mode .el-text--secondary {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .el-text--primary {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-text--regular {
  color: var(--dark-text-primary) !important;
}

/* ========== 页面头部暗夜模式 ========== */
/* 所有页面的header样式 */
#app.dark-mode .page-header,
#app.dark-mode .view-header,
#app.dark-mode .header-container,
#app.dark-mode .header,
#app.dark-mode .el-header.header {
  background-color: var(--dark-bg-secondary) !important;
  border-bottom-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .header-content {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .header-title {
  color: var(--dark-text-primary) !important;
}

/* ========== 选择器、单选框、复选框、开关暗夜模式 ========== */
#app.dark-mode .el-select {
  background-color: var(--dark-bg-tertiary) !important;
}

#app.dark-mode .el-select .el-input__wrapper {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-select-dropdown {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-select-dropdown__item {
  color: var(--dark-text-primary) !important;
  background-color: var(--dark-bg-secondary) !important;
}

#app.dark-mode .el-select-dropdown__item:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .el-select-dropdown__item.selected {
  color: #409EFF !important;
  background-color: rgba(64, 158, 255, 0.1) !important;
}

#app.dark-mode .el-radio {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-radio__input.is-checked .el-radio__inner {
  background-color: #409EFF !important;
  border-color: #409EFF !important;
}

#app.dark-mode .el-radio__label {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-checkbox {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-checkbox__input.is-checked .el-checkbox__inner {
  background-color: #409EFF !important;
  border-color: #409EFF !important;
}

#app.dark-mode .el-checkbox__label {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-switch {
  --el-switch-on-color: #409EFF !important;
  --el-switch-off-color: var(--dark-border) !important;
}

#app.dark-mode .el-switch__label {
  color: var(--dark-text-primary) !important;
}

/* ========== 上传组件暗夜模式 ========== */
#app.dark-mode .el-upload {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-upload-dragger {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-upload-dragger:hover {
  border-color: #409EFF !important;
}

#app.dark-mode .el-upload-list__item {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-upload-list__item-name {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-upload-list__item-status-label {
  color: var(--dark-text-secondary) !important;
}

/* ========== 文本域暗夜模式 ========== */
#app.dark-mode .el-textarea__inner {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-textarea__inner::placeholder {
  color: var(--dark-text-tertiary) !important;
}

/* ========== 步骤条暗夜模式 ========== */
#app.dark-mode .el-steps {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-step__title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-step__description {
  color: var(--dark-text-secondary) !important;
}

/* ========== 评分暗夜模式 ========== */
#app.dark-mode .el-rate {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-rate__text {
  color: var(--dark-text-secondary) !important;
}

/* ========== 滑块暗夜模式 ========== */
#app.dark-mode .el-slider {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-slider__runway {
  background-color: var(--dark-border) !important;
}

#app.dark-mode .el-slider__bar {
  background-color: #409EFF !important;
}

#app.dark-mode .el-slider__button {
  background-color: #409EFF !important;
  border-color: #409EFF !important;
}

/* ========== 折叠面板暗夜模式 ========== */
#app.dark-mode .el-collapse {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-collapse-item__header {
  background-color: var(--dark-bg-tertiary) !important;
  color: var(--dark-text-primary) !important;
  border-bottom-color: var(--dark-border) !important;
}

#app.dark-mode .el-collapse-item__content {
  background-color: var(--dark-bg-secondary) !important;
  color: var(--dark-text-primary) !important;
  border-bottom-color: var(--dark-border) !important;
}

/* ========== 树形控件暗夜模式 ========== */
#app.dark-mode .el-tree {
  background-color: var(--dark-bg-secondary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-tree-node__content {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-tree-node__content:hover {
  background-color: var(--dark-hover) !important;
}

/* ========== 级联选择器暗夜模式 ========== */
#app.dark-mode .el-cascader {
  background-color: var(--dark-bg-tertiary) !important;
}

#app.dark-mode .el-cascader-menu {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-cascader-node {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-cascader-node:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .el-cascader-node.is-active {
  color: #409EFF !important;
}

/* ========== 颜色选择器暗夜模式 ========== */
#app.dark-mode .el-color-picker {
  background-color: var(--dark-bg-tertiary) !important;
}

#app.dark-mode .el-color-picker__trigger {
  border-color: var(--dark-border) !important;
}

/* ========== 时间选择器暗夜模式 ========== */
#app.dark-mode .el-time-picker {
  background-color: var(--dark-bg-tertiary) !important;
}

#app.dark-mode .el-time-panel {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-time-spinner__item {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-time-spinner__item:hover {
  background-color: var(--dark-hover) !important;
}

#app.dark-mode .el-time-spinner__item.active {
  color: #409EFF !important;
}

/* ========== 穿梭框暗夜模式 ========== */
#app.dark-mode .el-transfer {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-transfer-panel {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-transfer-panel__header {
  background-color: var(--dark-bg-tertiary) !important;
  border-bottom-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-transfer-panel__body {
  background-color: var(--dark-bg-secondary) !important;
}

#app.dark-mode .el-transfer-panel__list {
  background-color: var(--dark-bg-secondary) !important;
}

#app.dark-mode .el-transfer-panel__item {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-transfer-panel__item:hover {
  background-color: var(--dark-hover) !important;
}

/* ========== 通知暗夜模式 ========== */
#app.dark-mode .el-notification {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-notification__title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-notification__content {
  color: var(--dark-text-secondary) !important;
}

/* ========== 警告提示暗夜模式 ========== */
#app.dark-mode .el-alert {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-alert__title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-alert__description {
  color: var(--dark-text-secondary) !important;
}

/* 不同类型的alert暗夜模式 */
#app.dark-mode .el-alert--success {
  background-color: rgba(103, 194, 58, 0.15) !important;
  border-color: rgba(103, 194, 58, 0.3) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-alert--success .el-alert__title {
  color: #85CE61 !important;
}

#app.dark-mode .el-alert--warning {
  background-color: rgba(230, 162, 60, 0.15) !important;
  border-color: rgba(230, 162, 60, 0.3) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-alert--warning .el-alert__title {
  color: #FFB84D !important;
}

#app.dark-mode .el-alert--info {
  background-color: rgba(64, 158, 255, 0.15) !important;
  border-color: rgba(64, 158, 255, 0.3) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-alert--info .el-alert__title {
  color: #66B1FF !important;
}

#app.dark-mode .el-alert--error {
  background-color: rgba(245, 108, 108, 0.15) !important;
  border-color: rgba(245, 108, 108, 0.3) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-alert--error .el-alert__title {
  color: #F78989 !important;
}

/* ========== 面包屑暗夜模式 ========== */
#app.dark-mode .el-breadcrumb {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-breadcrumb__inner {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .el-breadcrumb__inner.is-link {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-breadcrumb__inner.is-link:hover {
  color: #409EFF !important;
}

/* ========== 页面容器暗夜模式 ========== */
/* 修复所有页面的白色背景容器 */
#app.dark-mode .page-container,
#app.dark-mode .view-container,
#app.dark-mode .content-container,
#app.dark-mode .main-container {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

/* 修复白色背景的卡片 */
#app.dark-mode .white-card,
#app.dark-mode .content-card,
#app.dark-mode .info-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* ========== 作业视图特定样式 ========== */
#app.dark-mode .homework-header,
#app.dark-mode .submission-header {
  background-color: var(--dark-bg-secondary) !important;
  border-bottom-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-content,
#app.dark-mode .submission-content {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .attachment-card,
#app.dark-mode .reference-files-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* ========== 图片预览器暗夜模式 ========== */
#app.dark-mode .image-viewer-overlay,
#app.dark-mode .pdf-viewer-overlay {
  background-color: rgba(0, 0, 0, 0.9) !important;
}

#app.dark-mode .image-viewer-close,
#app.dark-mode .pdf-viewer-close {
  color: var(--dark-text-primary) !important;
  background-color: rgba(45, 45, 45, 0.8) !important;
}

/* ========== 表格操作按钮暗夜模式 ========== */
#app.dark-mode .el-table__fixed-right-patch {
  background-color: var(--dark-bg-secondary) !important;
}

#app.dark-mode .el-table__fixed {
  background-color: var(--dark-bg-secondary) !important;
}

/* ========== 分页器暗夜模式增强 ========== */
#app.dark-mode .el-pagination .el-select .el-input__wrapper {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-pagination .el-input__inner {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-pagination .el-pagination__total {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .el-pagination .el-pagination__jump {
  color: var(--dark-text-secondary) !important;
}

/* ========== 弹出层暗夜模式 ========== */
#app.dark-mode .el-popover {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-popover__title {
  color: var(--dark-text-primary) !important;
}

/* ========== 描述列表暗夜模式 ========== */
#app.dark-mode .el-descriptions {
  background-color: var(--dark-bg-secondary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-descriptions__header {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-descriptions__label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .el-descriptions__content {
  color: var(--dark-text-primary) !important;
}

/* ========== 结果页暗夜模式 ========== */
#app.dark-mode .el-result {
  background-color: var(--dark-bg-secondary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-result__title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-result__subtitle {
  color: var(--dark-text-secondary) !important;
}

/* ========== 骨架屏暗夜模式增强 ========== */
#app.dark-mode .el-skeleton__avatar {
  background: linear-gradient(90deg, var(--dark-bg-tertiary) 25%, var(--dark-hover) 37%, var(--dark-bg-tertiary) 63%) !important;
}

#app.dark-mode .el-skeleton__button {
  background: linear-gradient(90deg, var(--dark-bg-tertiary) 25%, var(--dark-hover) 37%, var(--dark-bg-tertiary) 63%) !important;
}

#app.dark-mode .el-skeleton__image {
  background: linear-gradient(90deg, var(--dark-bg-tertiary) 25%, var(--dark-hover) 37%, var(--dark-bg-tertiary) 63%) !important;
}

/* ========== 管理员仪表板特定样式 ========== */
#app.dark-mode .admin-tabs,
#app.dark-mode .admin-dashboard-container {
  background-color: var(--dark-bg-secondary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .admin-tabs .el-tabs__content {
  background-color: var(--dark-bg-secondary) !important;
}

/* ========== 作业视图特定样式增强 ========== */
#app.dark-mode .homework-view-container,
#app.dark-mode .submission-view-container {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-info-card,
#app.dark-mode .submission-info-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* ========== 课程详情特定样式 ========== */
/* ========== 学生端课程详情页暗夜模式 ========== */
#app.dark-mode .course-detail {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-detail .header {
  background-color: var(--dark-bg-secondary) !important;
  border-bottom-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-detail .header-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-detail-container {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-info-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-info h2 {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-code {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .course-announcement {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-announcement strong {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-list-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-list-card .card-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-item {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-item:hover {
  background-color: var(--dark-hover) !important;
  border-color: #409EFF !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
}

#app.dark-mode .homework-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-deadline {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .homework-submission-time {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .homework-actions .el-button {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-actions .el-button:hover {
  color: #409EFF !important;
}

#app.dark-mode .homework-list-footer {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-list-footer .el-button {
  color: #409EFF !important;
}

/* ========== 日期作业视图特定样式 ========== */
#app.dark-mode .date-homeworks-container {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

/* ========== 所有作业页面暗夜模式 ========== */
#app.dark-mode .all-homeworks-view {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .all-homeworks-view .homeworks-container {
  background-color: var(--dark-bg-primary) !important;
}

#app.dark-mode .all-homeworks-view .stats-card,
#app.dark-mode .all-homeworks-view .filter-card,
#app.dark-mode .all-homeworks-view .homeworks-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .all-homeworks-view .card-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .all-homeworks-view .card-count {
  color: var(--dark-text-secondary) !important;
}

/* 所有作业页面筛选按钮暗夜模式 */
#app.dark-mode .all-homeworks-view .el-radio-group {
  background-color: transparent !important;
}

#app.dark-mode .all-homeworks-view .el-radio-button__inner {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .all-homeworks-view .el-radio-button__inner:hover {
  background-color: var(--dark-hover) !important;
  border-color: #409EFF !important;
  color: #409EFF !important;
}

#app.dark-mode .all-homeworks-view .el-radio-button__original-radio:checked + .el-radio-button__inner {
  background-color: #409EFF !important;
  border-color: #409EFF !important;
  color: #ffffff !important;
  box-shadow: none !important;
}

#app.dark-mode .all-homeworks-view .el-radio-button:first-child .el-radio-button__inner {
  border-left-color: var(--dark-border) !important;
}

#app.dark-mode .all-homeworks-view .el-radio-button:last-child .el-radio-button__inner {
  border-right-color: var(--dark-border) !important;
}

/* 所有作业页面选择器暗夜模式 */
#app.dark-mode .all-homeworks-view .el-select .el-input__wrapper {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .all-homeworks-view .el-select .el-input__inner {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .all-homeworks-view .el-select .el-input__inner::placeholder {
  color: var(--dark-text-tertiary) !important;
}

/* 所有作业页面标签暗夜模式 - 使用深色但能区分的颜色 */
#app.dark-mode .all-homeworks-view .el-tag.el-tag--warning {
  background-color: rgba(230, 162, 60, 0.15) !important;
  border-color: rgba(230, 162, 60, 0.35) !important;
  color: #FFB84D !important;
}

#app.dark-mode .all-homeworks-view .el-tag.el-tag--danger {
  background-color: rgba(245, 108, 108, 0.15) !important;
  border-color: rgba(245, 108, 108, 0.35) !important;
  color: #F78989 !important;
}

#app.dark-mode .all-homeworks-view .el-tag.el-tag--success {
  background-color: rgba(103, 194, 58, 0.15) !important;
  border-color: rgba(103, 194, 58, 0.35) !important;
  color: #85CE61 !important;
}

#app.dark-mode .all-homeworks-view .el-tag.el-tag--info {
  background-color: rgba(64, 158, 255, 0.15) !important;
  border-color: rgba(64, 158, 255, 0.35) !important;
  color: #66B1FF !important;
}

/* 所有作业页面表格行暗夜模式 */
#app.dark-mode .all-homeworks-view .overdue-row {
  background-color: rgba(245, 108, 108, 0.1) !important;
}

#app.dark-mode .all-homeworks-view .overdue-row:hover {
  background-color: rgba(245, 108, 108, 0.15) !important;
}

/* ========== 作业详情页面暗夜模式 ========== */
#app.dark-mode .homework-view {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-view-container {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-requirement-card,
#app.dark-mode .homework-submission-card,
#app.dark-mode .grading-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* 批改反馈内容区域暗夜模式 */
#app.dark-mode .grading-content {
  background-color: transparent !important;
  color: var(--dark-text-primary) !important;
}

/* 得分区域暗夜模式 */
#app.dark-mode .score-section {
  background: linear-gradient(135deg, var(--dark-bg-tertiary) 0%, var(--dark-hover) 100%) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .score-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .score-unit {
  color: var(--dark-text-primary) !important;
}

/* 批改人信息暗夜模式 */
#app.dark-mode .grader-info {
  color: var(--dark-text-primary) !important;
}

/* 反馈区域暗夜模式 */
#app.dark-mode .feedback-section {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .feedback-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .feedback-text {
  background-color: var(--dark-bg-secondary) !important;
  border-left-color: #409EFF !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-content,
#app.dark-mode .submission-content {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .text-content {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* 作业详情页面上传提示暗夜模式 */
#app.dark-mode .upload-tip {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .upload-tip::before {
  color: var(--dark-text-secondary) !important;
}

/* ========== 查看提交页面暗夜模式 ========== */
#app.dark-mode .submission-view {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .submission-view-container {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-info-card,
#app.dark-mode .submission-display-card,
#app.dark-mode .grading-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* 批改反馈内容区域暗夜模式 */
#app.dark-mode .grading-content {
  background-color: transparent !important;
  color: var(--dark-text-primary) !important;
}

/* 得分区域暗夜模式 */
#app.dark-mode .score-section {
  background: linear-gradient(135deg, var(--dark-bg-tertiary) 0%, var(--dark-hover) 100%) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .score-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .score-unit {
  color: var(--dark-text-primary) !important;
}

/* 批改人信息暗夜模式 */
#app.dark-mode .grader-info {
  color: var(--dark-text-primary) !important;
}

/* 反馈区域暗夜模式 */
#app.dark-mode .feedback-section {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .feedback-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .feedback-text {
  background-color: var(--dark-bg-secondary) !important;
  border-left-color: #409EFF !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-basic-info h2 {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-basic-info .deadline {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .submission-content .text-content {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .submit-time {
  color: var(--dark-text-secondary) !important;
}

/* ========== 教师主页特定样式 ========== */
#app.dark-mode .teacher-home-container {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

/* ========== 确保所有白色背景被覆盖 ========== */
#app.dark-mode [style*="background: #fff"],
#app.dark-mode [style*="background: #ffffff"],
#app.dark-mode [style*="background-color: #fff"],
#app.dark-mode [style*="background-color: #ffffff"] {
  background-color: var(--dark-bg-secondary) !important;
}

/* ========== 确保所有白色文字被覆盖 ========== */
#app.dark-mode [style*="color: #fff"],
#app.dark-mode [style*="color: #ffffff"] {
  color: var(--dark-text-primary) !important;
}

/* ========== 修复页面容器的白色背景 ========== */
#app.dark-mode .container,
#app.dark-mode .main-content,
#app.dark-mode .content-wrapper {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

/* ========== 默认亮色模式 - 布局元素样式 ========== */
/* 使用 :not(.dark-mode) 确保暗夜模式关闭时所有元素都是白色 */
#app:not(.dark-mode) .el-header,
#app .el-header {
  background-color: #ffffff !important;
  border-bottom-color: #e4e7ed !important;
  color: #303133 !important;
}

#app:not(.dark-mode) .el-main,
#app .el-main {
  background-color: #ffffff !important;
  color: #303133 !important;
}

#app:not(.dark-mode) .el-aside,
#app .el-aside {
  background-color: #ffffff !important;
  border-right-color: #e4e7ed !important;
  color: #303133 !important;
}

#app:not(.dark-mode) .el-footer,
#app .el-footer {
  background-color: #ffffff !important;
  border-top-color: #e4e7ed !important;
  color: #303133 !important;
}

/* 确保所有卡片在默认模式下是白色 */
#app:not(.dark-mode) .el-card {
  background-color: #ffffff !important;
  border-color: #ebeef5 !important;
  color: #303133 !important;
}

/* 确保所有输入框在默认模式下是白色 */
#app:not(.dark-mode) .el-input__wrapper {
  background-color: #ffffff !important;
  border-color: #dcdfe6 !important;
}

#app:not(.dark-mode) .el-input__inner {
  background-color: transparent !important;
  color: #606266 !important;
}

/* 确保所有下拉选择框在默认模式下是白色 */
#app:not(.dark-mode) .el-select .el-input__wrapper {
  background-color: #ffffff !important;
  border-color: #dcdfe6 !important;
}

#app:not(.dark-mode) .el-select .el-input__inner {
  background-color: transparent !important;
  color: #606266 !important;
}

/* 确保所有表格在默认模式下是白色 */
#app:not(.dark-mode) .el-table {
  background-color: #ffffff !important;
  color: #606266 !important;
}

#app:not(.dark-mode) .el-table th.el-table__cell {
  background-color: #fafafa !important;
  color: #606266 !important;
  border-color: #ebeef5 !important;
}

#app:not(.dark-mode) .el-table td.el-table__cell {
  background-color: #ffffff !important;
  border-color: #ebeef5 !important;
  color: #606266 !important;
}

/* 确保所有文本区域在默认模式下是白色 */
#app:not(.dark-mode) .el-textarea__inner {
  background-color: #ffffff !important;
  border-color: #dcdfe6 !important;
  color: #606266 !important;
}

/* 确保所有下拉菜单在默认模式下是白色 */
#app:not(.dark-mode) .el-select-dropdown {
  background-color: #ffffff !important;
  border-color: #e4e7ed !important;
}

#app:not(.dark-mode) .el-select-dropdown__item {
  background-color: #ffffff !important;
  color: #606266 !important;
}

#app:not(.dark-mode) .el-select-dropdown__item:hover {
  background-color: #f5f7fa !important;
}

/* 确保所有页面容器在默认模式下是白色 */
#app:not(.dark-mode) .page-container,
#app:not(.dark-mode) .view-container,
#app:not(.dark-mode) .content-container,
#app:not(.dark-mode) .main-container,
#app:not(.dark-mode) .container,
#app:not(.dark-mode) .main-content,
#app:not(.dark-mode) .content-wrapper {
  background-color: #ffffff !important;
  color: #303133 !important;
}

/* ========== 默认模式下按钮文字颜色调整 ========== */
/* 老师端课程号复制按钮文字颜色调亮 - 使用更亮的主色调 */
#app:not(.dark-mode) .copy-btn,
#app:not(.dark-mode) .copy-btn span,
#app:not(.dark-mode) .copy-btn .el-button__text,
#app:not(.dark-mode) .el-button.copy-btn,
#app:not(.dark-mode) .el-button.copy-btn span,
#app:not(.dark-mode) .el-button.copy-btn .el-button__text {
  color: #409EFF !important;
}

#app:not(.dark-mode) .copy-btn:hover,
#app:not(.dark-mode) .copy-btn:hover span,
#app:not(.dark-mode) .copy-btn:hover .el-button__text,
#app:not(.dark-mode) .el-button.copy-btn:hover,
#app:not(.dark-mode) .el-button.copy-btn:hover span,
#app:not(.dark-mode) .el-button.copy-btn:hover .el-button__text {
  color: #66b1ff !important;
}

/* 老师端"去查看"和"去批改"按钮文字颜色调亮 */
#app:not(.dark-mode) .el-button--primary.is-text,
#app:not(.dark-mode) .el-button--primary.is-text span,
#app:not(.dark-mode) .el-button--primary.is-text .el-button__text,
#app:not(.dark-mode) .el-button--primary.el-button--text,
#app:not(.dark-mode) .el-button--primary.el-button--text span,
#app:not(.dark-mode) .el-button--primary.el-button--text .el-button__text {
  color: #409EFF !important;
}

#app:not(.dark-mode) .el-button--primary.is-text:hover,
#app:not(.dark-mode) .el-button--primary.is-text:hover span,
#app:not(.dark-mode) .el-button--primary.is-text:hover .el-button__text,
#app:not(.dark-mode) .el-button--primary.el-button--text:hover,
#app:not(.dark-mode) .el-button--primary.el-button--text:hover span,
#app:not(.dark-mode) .el-button--primary.el-button--text:hover .el-button__text {
  color: #66b1ff !important;
}

/* 确保所有 primary text 按钮的文字在默认模式下清晰可见 */
#app:not(.dark-mode) button.el-button--primary.is-text,
#app:not(.dark-mode) button.el-button--primary.el-button--text {
  color: #409EFF !important;
}

#app:not(.dark-mode) button.el-button--primary.is-text:hover,
#app:not(.dark-mode) button.el-button--primary.el-button--text:hover {
  color: #66b1ff !important;
}

/* ========== 暗夜模式 - 布局元素样式 ========== */
#app.dark-mode .el-header {
  background-color: var(--dark-bg-secondary) !important;
  border-bottom-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-main {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-aside {
  background-color: var(--dark-bg-secondary) !important;
  border-right-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-footer {
  background-color: var(--dark-bg-secondary) !important;
  border-top-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* ========== 所有作业页面暗夜模式 ========== */
#app.dark-mode .all-homeworks-view {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .all-homeworks-view .homeworks-container {
  background-color: var(--dark-bg-primary) !important;
}

#app.dark-mode .all-homeworks-view .stats-card,
#app.dark-mode .all-homeworks-view .filter-card,
#app.dark-mode .all-homeworks-view .homeworks-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .all-homeworks-view .card-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .all-homeworks-view .card-count {
  color: var(--dark-text-secondary) !important;
}

/* 所有作业页面筛选按钮暗夜模式 */
#app.dark-mode .all-homeworks-view .el-radio-group {
  background-color: transparent !important;
}

#app.dark-mode .all-homeworks-view .el-radio-button__inner {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .all-homeworks-view .el-radio-button__inner:hover {
  background-color: var(--dark-hover) !important;
  border-color: #409EFF !important;
  color: #409EFF !important;
}

#app.dark-mode .all-homeworks-view .el-radio-button__original-radio:checked + .el-radio-button__inner {
  background-color: #409EFF !important;
  border-color: #409EFF !important;
  color: #ffffff !important;
  box-shadow: none !important;
}

#app.dark-mode .all-homeworks-view .el-radio-button:first-child .el-radio-button__inner {
  border-left-color: var(--dark-border) !important;
}

#app.dark-mode .all-homeworks-view .el-radio-button:last-child .el-radio-button__inner {
  border-right-color: var(--dark-border) !important;
}

/* 所有作业页面选择器暗夜模式 */
#app.dark-mode .all-homeworks-view .el-select .el-input__wrapper {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .all-homeworks-view .el-select .el-input__inner {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .all-homeworks-view .el-select .el-input__inner::placeholder {
  color: var(--dark-text-tertiary) !important;
}

/* 所有作业页面标签暗夜模式 - 使用深色但能区分的颜色 */
#app.dark-mode .all-homeworks-view .el-tag.el-tag--warning {
  background-color: rgba(230, 162, 60, 0.15) !important;
  border-color: rgba(230, 162, 60, 0.35) !important;
  color: #FFB84D !important;
}

#app.dark-mode .all-homeworks-view .el-tag.el-tag--danger {
  background-color: rgba(245, 108, 108, 0.15) !important;
  border-color: rgba(245, 108, 108, 0.35) !important;
  color: #F78989 !important;
}

#app.dark-mode .all-homeworks-view .el-tag.el-tag--success {
  background-color: rgba(103, 194, 58, 0.15) !important;
  border-color: rgba(103, 194, 58, 0.35) !important;
  color: #85CE61 !important;
}

#app.dark-mode .all-homeworks-view .el-tag.el-tag--info {
  background-color: rgba(64, 158, 255, 0.15) !important;
  border-color: rgba(64, 158, 255, 0.35) !important;
  color: #66B1FF !important;
}

/* 所有作业页面表格行暗夜模式 */
#app.dark-mode .all-homeworks-view .overdue-row {
  background-color: rgba(245, 108, 108, 0.1) !important;
}

#app.dark-mode .all-homeworks-view .overdue-row:hover {
  background-color: rgba(245, 108, 108, 0.15) !important;
}

/* ========== 作业详情页面暗夜模式 ========== */
#app.dark-mode .homework-view {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-view-container {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-requirement-card,
#app.dark-mode .homework-submission-card,
#app.dark-mode .grading-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* 批改反馈内容区域暗夜模式 */
#app.dark-mode .grading-content {
  background-color: transparent !important;
  color: var(--dark-text-primary) !important;
}

/* 得分区域暗夜模式 */
#app.dark-mode .score-section {
  background: linear-gradient(135deg, var(--dark-bg-tertiary) 0%, var(--dark-hover) 100%) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .score-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .score-unit {
  color: var(--dark-text-primary) !important;
}

/* 批改人信息暗夜模式 */
#app.dark-mode .grader-info {
  color: var(--dark-text-primary) !important;
}

/* 反馈区域暗夜模式 */
#app.dark-mode .feedback-section {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .feedback-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .feedback-text {
  background-color: var(--dark-bg-secondary) !important;
  border-left-color: #409EFF !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-content,
#app.dark-mode .submission-content {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .text-content {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* 作业详情页面上传提示暗夜模式 */
#app.dark-mode .upload-tip {
  background: linear-gradient(135deg, rgba(45, 45, 45, 0.8) 0%, rgba(37, 37, 37, 0.8) 100%) !important;
  border-left-color: #409EFF !important;
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .upload-tip::before {
  color: var(--dark-text-secondary) !important;
}

/* ========== 查看提交页面暗夜模式 ========== */
#app.dark-mode .submission-view {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .submission-view-container {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-info-card,
#app.dark-mode .submission-display-card,
#app.dark-mode .grading-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* 批改反馈内容区域暗夜模式 */
#app.dark-mode .grading-content {
  background-color: transparent !important;
  color: var(--dark-text-primary) !important;
}

/* 得分区域暗夜模式 */
#app.dark-mode .score-section {
  background: linear-gradient(135deg, var(--dark-bg-tertiary) 0%, var(--dark-hover) 100%) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .score-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .score-unit {
  color: var(--dark-text-primary) !important;
}

/* 批改人信息暗夜模式 */
#app.dark-mode .grader-info {
  color: var(--dark-text-primary) !important;
}

/* 反馈区域暗夜模式 */
#app.dark-mode .feedback-section {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .feedback-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .feedback-text {
  background-color: var(--dark-bg-secondary) !important;
  border-left-color: #409EFF !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-basic-info h2 {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .homework-basic-info .deadline {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .submission-content .text-content {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .submit-time {
  color: var(--dark-text-secondary) !important;
}

/* ========== 老师端页面暗夜模式 ========== */
/* 教师主页暗夜模式 */
#app.dark-mode .teacher-home-container {
  background-color: var(--dark-bg-primary) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-center {
  background-color: var(--dark-bg-primary) !important;
}

#app.dark-mode .section-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-card {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .course-card:hover {
  background-color: var(--dark-hover) !important;
  border-color: #409EFF !important;
}

#app.dark-mode .course-name {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-semester {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .course-code-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .course-code-value {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .stat-label {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .stat-value {
  color: var(--dark-text-primary) !important;
}

/* 教师课程详情页暗夜模式 */
#app.dark-mode .course-detail-container {
  background-color: var(--dark-bg-primary) !important;
}

#app.dark-mode .course-toolbar {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .task-item {
  background-color: var(--dark-bg-secondary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .task-item:hover {
  background-color: var(--dark-hover) !important;
  border-color: #409EFF !important;
}

#app.dark-mode .task-title {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .task-deadline {
  color: var(--dark-text-secondary) !important;
}

#app.dark-mode .task-sub-info {
  color: var(--dark-text-secondary) !important;
}

/* 教师课程详情页工具栏按钮暗夜模式 */
#app.dark-mode .course-toolbar .el-button:not(.el-button--primary):not(.el-button--success) {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-toolbar .el-button:hover {
  background-color: var(--dark-hover) !important;
  border-color: #409EFF !important;
  color: #409EFF !important;
}

/* 教师课程详情页搜索框暗夜模式 */
#app.dark-mode .toolbar-search .el-input__wrapper {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .toolbar-search .el-input__inner {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .toolbar-search .el-input__inner::placeholder {
  color: var(--dark-text-tertiary) !important;
}

/* 教师课程详情页对话框暗夜模式 */
#app.dark-mode .el-dialog .el-form-item__label {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-dialog .el-input__wrapper {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-dialog .el-input__inner {
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .el-dialog .el-textarea__inner {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

/* 教师课程详情页上传组件暗夜模式 */
#app.dark-mode .el-upload {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .el-upload-dragger {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .upload-file-item {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
}

#app.dark-mode .upload-file-name {
  color: var(--dark-text-primary) !important;
}

/* 教师课程详情页表单提示暗夜模式 */
#app.dark-mode .form-tip {
  color: var(--dark-text-secondary) !important;
}

/* 教师主页课程卡片暗夜模式 */
#app.dark-mode .course-card-body {
  background-color: var(--dark-bg-secondary) !important;
}

#app.dark-mode .course-tags .el-tag {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-card-actions .el-button {
  background-color: var(--dark-bg-tertiary) !important;
  border-color: var(--dark-border) !important;
  color: var(--dark-text-primary) !important;
}

#app.dark-mode .course-card-actions .el-button:hover {
  background-color: var(--dark-hover) !important;
  border-color: #409EFF !important;
  color: #409EFF !important;
}

#app.dark-mode .course-card-actions .el-button[type="primary"] {
  background-color: #409EFF !important;
  border-color: #409EFF !important;
  color: #ffffff !important;
}

#app.dark-mode .course-card-actions .el-button[type="success"] {
  background-color: #67C23A !important;
  border-color: #67C23A !important;
  color: #ffffff !important;
}

#app.dark-mode .course-card-actions .el-button[type="info"] {
  background-color: #909399 !important;
  border-color: #909399 !important;
  color: #ffffff !important;
}
</style>
