import { defineStore } from 'pinia';

// 获取当前用户ID
const getCurrentUserId = () => {
  try {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      const user = JSON.parse(userStr);
      // 根据用户类型返回对应的ID字段
      // 所有用户对象都有 id 和 role 字段（根据后端返回的数据结构）
      if (user.id !== undefined && user.id !== null) {
        // 使用 role 和 id 组合确保唯一性
        // 例如: "student_1", "teacher_2", "admin_1"
        return user.role ? `${user.role}_${user.id}` : `user_${user.id}`;
      }
      // 兼容旧数据：如果没有 id，尝试其他字段
      if (user.student_id !== undefined && user.student_id !== null) {
        return `student_${user.student_id}`;
      }
      if (user.staff_id !== undefined && user.staff_id !== null) {
        return `staff_${user.staff_id}`;
      }
      if (user.admin_id !== undefined && user.admin_id !== null) {
        return `admin_${user.admin_id}`;
      }
      // 如果都没有，尝试使用role和可能的其他标识（如学号、工号）
      if (user.role) {
        if (user.student_no) return `${user.role}_${user.student_no}`;
        if (user.staff_no) return `${user.role}_${user.staff_no}`;
        if (user.username) return `${user.role}_${user.username}`;
        if (user.name) return `${user.role}_${user.name}`;
      }
    }
  } catch (e) {
    console.error('Failed to get user ID:', e);
  }
  return null;
};

// 获取用户个性化设置的key
const getPersonalizationKey = () => {
  const userId = getCurrentUserId();
  return userId ? `personalization_${userId}` : 'personalization_guest';
};

// 默认个性化设置
const defaultSettings = {
  backgroundColor: '#ffffff', // 页面背景颜色改为白色
  darkMode: false, // 暗夜模式开关
  modules: {
    header: {
      backgroundColor: '#ffffff', // 白色
      textColor: '#303133',
      position: 'top',
      visible: true,
    },
    sidebar: {
      backgroundColor: '#ffffff', // 白色
      textColor: '#303133',
      position: 'left',
      visible: true,
    },
    content: {
      backgroundColor: '#ffffff', // 白色
      textColor: '#303133',
      position: 'center',
      visible: true,
    },
    card: {
      backgroundColor: '#ffffff', // 白色
      textColor: '#303133',
      borderColor: '#ebeef5',
      visible: true,
    },
  },
};

// 暗夜模式配置
const darkModeSettings = {
  backgroundColor: '#1a1a1a',
  modules: {
    header: {
      backgroundColor: '#2d2d2d',
      textColor: '#e5e5e5',
    },
    sidebar: {
      backgroundColor: '#252525',
      textColor: '#e5e5e5',
    },
    content: {
      backgroundColor: '#1a1a1a',
      textColor: '#e5e5e5',
    },
    card: {
      backgroundColor: '#2d2d2d',
      textColor: '#e5e5e5',
      borderColor: '#404040',
    },
  },
};

export const usePersonalizationStore = defineStore('personalization', {
  state: () => {
    // 从localStorage加载当前用户的个性化设置
    const key = getPersonalizationKey();
    const savedSettings = localStorage.getItem(key);
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        // 合并默认设置和保存的设置
        const merged = {
          ...defaultSettings,
          ...parsed,
          modules: {
            ...defaultSettings.modules,
            ...(parsed.modules || {}),
          },
        };
        // 如果启用了暗夜模式，应用暗夜模式配置
        if (merged.darkMode) {
          merged.backgroundColor = darkModeSettings.backgroundColor;
          Object.keys(merged.modules).forEach(moduleName => {
            if (darkModeSettings.modules[moduleName]) {
              merged.modules[moduleName] = {
                ...merged.modules[moduleName],
                ...darkModeSettings.modules[moduleName],
              };
            }
          });
        }
        return merged;
      } catch (e) {
        console.error('Failed to parse personalization settings:', e);
      }
    }
    return defaultSettings;
  },
  getters: {
    getModuleStyle: (state) => (moduleName) => {
      const module = state.modules[moduleName];
      if (!module) return {};
      return {
        backgroundColor: module.backgroundColor,
        color: module.textColor,
        borderColor: module.borderColor,
      };
    },
  },
  actions: {
    updateBackgroundColor(color) {
      this.backgroundColor = color;
      this.save();
    },
    updateModule(moduleName, updates) {
      if (!this.modules[moduleName]) {
        this.modules[moduleName] = { ...defaultSettings.modules[moduleName] };
      }
      this.modules[moduleName] = {
        ...this.modules[moduleName],
        ...updates,
      };
      this.save();
    },
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
      if (this.darkMode) {
        // 启用暗夜模式
        this.backgroundColor = darkModeSettings.backgroundColor;
        Object.keys(this.modules).forEach(moduleName => {
          if (darkModeSettings.modules[moduleName]) {
            this.modules[moduleName] = {
              ...this.modules[moduleName],
              backgroundColor: darkModeSettings.modules[moduleName].backgroundColor,
              textColor: darkModeSettings.modules[moduleName].textColor,
              borderColor: darkModeSettings.modules[moduleName].borderColor || this.modules[moduleName].borderColor,
            };
          }
        });
      } else {
        // 关闭暗夜模式，恢复默认 - 强制重置所有颜色为白色
        this.backgroundColor = '#ffffff';
        Object.keys(this.modules).forEach(moduleName => {
          if (defaultSettings.modules[moduleName]) {
            // 完全替换为默认设置，确保所有属性都被重置
            this.modules[moduleName] = {
              ...defaultSettings.modules[moduleName],
            };
          }
        });
      }
      this.save();
    },
    resetToDefault() {
      this.darkMode = false;
      this.backgroundColor = defaultSettings.backgroundColor;
      this.modules = JSON.parse(JSON.stringify(defaultSettings.modules));
      this.save();
    },
    save() {
      const key = getPersonalizationKey();
      localStorage.setItem(key, JSON.stringify({
        backgroundColor: this.backgroundColor,
        darkMode: this.darkMode,
        modules: this.modules,
      }));
    },
    // 加载用户设置（在用户登录或切换时调用）
    loadUserSettings() {
      const key = getPersonalizationKey();
      const savedSettings = localStorage.getItem(key);
      if (savedSettings) {
        try {
          const parsed = JSON.parse(savedSettings);
          // 合并默认设置和保存的设置
          const merged = {
            ...defaultSettings,
            ...parsed,
            modules: {
              ...defaultSettings.modules,
              ...(parsed.modules || {}),
            },
          };
          // 如果启用了暗夜模式，应用暗夜模式配置
          if (merged.darkMode) {
            merged.backgroundColor = darkModeSettings.backgroundColor;
            Object.keys(merged.modules).forEach(moduleName => {
              if (darkModeSettings.modules[moduleName]) {
                merged.modules[moduleName] = {
                  ...merged.modules[moduleName],
                  ...darkModeSettings.modules[moduleName],
                };
              }
            });
          }
          // 更新store状态
          this.backgroundColor = merged.backgroundColor;
          this.darkMode = merged.darkMode;
          this.modules = merged.modules;
        } catch (e) {
          console.error('Failed to load user settings:', e);
          // 如果加载失败，使用默认设置
          this.backgroundColor = defaultSettings.backgroundColor;
          this.darkMode = defaultSettings.darkMode;
          this.modules = JSON.parse(JSON.stringify(defaultSettings.modules));
        }
      } else {
        // 如果没有保存的设置，使用默认设置
        this.backgroundColor = defaultSettings.backgroundColor;
        this.darkMode = defaultSettings.darkMode;
        this.modules = JSON.parse(JSON.stringify(defaultSettings.modules));
      }
    },
  },
});

