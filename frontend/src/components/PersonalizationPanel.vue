<template>
  <el-drawer
    v-model="visible"
    title="个性化设置"
    size="400px"
    direction="rtl"
  >
    <div class="personalization-panel">
      <!-- 暗夜模式开关 -->
      <el-card shadow="never" class="setting-card dark-mode-card">
        <template #header>
          <div class="card-header">
            <span>暗夜模式</span>
            <el-switch
              v-model="localSettings.darkMode"
              @change="handleDarkModeToggle"
              active-text="开启"
              inactive-text="关闭"
            />
          </div>
        </template>
        <div class="dark-mode-description">
          <p>开启暗夜模式后，页面将使用适合夜晚工作的深色主题，减少眼部疲劳。</p>
        </div>
      </el-card>

      <!-- 背景颜色设置 -->
      <el-card shadow="never" class="setting-card">
        <template #header>
          <div class="card-header">
            <span>页面背景颜色</span>
          </div>
        </template>
        <div class="color-picker-group">
          <el-color-picker
            v-model="localSettings.backgroundColor"
            @change="handleBackgroundColorChange"
            show-alpha
          />
          <el-input
            v-model="localSettings.backgroundColor"
            @change="handleBackgroundColorChange"
            placeholder="#f5f7fa"
            style="width: 200px; margin-left: 12px;"
          />
        </div>
        <div class="preset-colors">
          <div
            v-for="color in presetColors"
            :key="color"
            class="preset-color-item"
            :style="{ backgroundColor: color }"
            @click="setBackgroundColor(color)"
          />
        </div>
      </el-card>

      <!-- 模块设置 -->
      <el-card
        v-for="(module, moduleName) in localSettings.modules"
        :key="moduleName"
        shadow="never"
        class="setting-card"
      >
        <template #header>
          <div class="card-header">
            <span>{{ getModuleLabel(moduleName) }}</span>
            <el-switch
              v-model="module.visible"
              @change="handleModuleVisibilityChange(moduleName, module.visible)"
            />
          </div>
        </template>
        <div class="module-settings">
          <!-- 背景颜色 -->
          <div class="setting-item">
            <label>背景颜色</label>
            <div class="color-picker-group">
              <el-color-picker
                v-model="module.backgroundColor"
                @change="handleModuleChange(moduleName)"
                show-alpha
              />
              <el-input
                v-model="module.backgroundColor"
                @change="handleModuleChange(moduleName)"
                placeholder="#ffffff"
                style="width: 150px; margin-left: 12px;"
              />
            </div>
          </div>
          <!-- 文字颜色 -->
          <div class="setting-item">
            <label>文字颜色</label>
            <div class="color-picker-group">
              <el-color-picker
                v-model="module.textColor"
                @change="handleModuleChange(moduleName)"
                show-alpha
              />
              <el-input
                v-model="module.textColor"
                @change="handleModuleChange(moduleName)"
                placeholder="#303133"
                style="width: 150px; margin-left: 12px;"
              />
            </div>
          </div>
          <!-- 边框颜色（仅卡片） -->
          <div v-if="moduleName === 'card'" class="setting-item">
            <label>边框颜色</label>
            <div class="color-picker-group">
              <el-color-picker
                v-model="module.borderColor"
                @change="handleModuleChange(moduleName)"
                show-alpha
              />
              <el-input
                v-model="module.borderColor"
                @change="handleModuleChange(moduleName)"
                placeholder="#ebeef5"
                style="width: 150px; margin-left: 12px;"
              />
            </div>
          </div>
          <!-- 位置设置（仅header和sidebar） -->
          <div v-if="['header', 'sidebar'].includes(moduleName)" class="setting-item">
            <label>位置</label>
            <el-radio-group
              v-model="module.position"
              @change="handleModuleChange(moduleName)"
            >
              <el-radio
                v-if="moduleName === 'header'"
                label="top"
              >顶部</el-radio>
              <el-radio
                v-if="moduleName === 'header'"
                label="bottom"
              >底部</el-radio>
              <el-radio
                v-if="moduleName === 'sidebar'"
                label="left"
              >左侧</el-radio>
              <el-radio
                v-if="moduleName === 'sidebar'"
                label="right"
              >右侧</el-radio>
            </el-radio-group>
          </div>
        </div>
      </el-card>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button @click="handleReset">恢复默认</el-button>
        <el-button type="primary" @click="handleSave">保存设置</el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { usePersonalizationStore } from '@/store/personalization';
import { ElMessage } from 'element-plus';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:modelValue']);

const personalizationStore = usePersonalizationStore();

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

// 本地设置副本 - 安全初始化
const initLocalSettings = () => {
  try {
    return JSON.parse(JSON.stringify(personalizationStore.$state));
  } catch (e) {
    console.error('Failed to initialize local settings:', e);
    // 返回默认设置的深拷贝
    return {
      backgroundColor: personalizationStore.backgroundColor || '#f5f7fa',
      darkMode: personalizationStore.darkMode || false,
      modules: {
        header: { ...personalizationStore.modules.header },
        sidebar: { ...personalizationStore.modules.sidebar },
        content: { ...personalizationStore.modules.content },
        card: { ...personalizationStore.modules.card },
      },
    };
  }
};

const localSettings = ref(initLocalSettings());

// 预设颜色
const presetColors = [
  '#f5f7fa',
  '#ffffff',
  '#f0f2f5',
  '#e8f4f8',
  '#fef0f0',
  '#f0f9ff',
  '#f5f0ff',
];

// 模块标签映射
const getModuleLabel = (moduleName) => {
  const labels = {
    header: '顶部导航栏',
    sidebar: '侧边栏',
    content: '内容区域',
    card: '卡片',
  };
  return labels[moduleName] || moduleName;
};

// 设置背景颜色
const setBackgroundColor = (color) => {
  localSettings.value.backgroundColor = color;
  handleBackgroundColorChange();
};

// 背景颜色改变
const handleBackgroundColorChange = () => {
  personalizationStore.updateBackgroundColor(localSettings.value.backgroundColor);
};

// 模块设置改变
const handleModuleChange = (moduleName) => {
  personalizationStore.updateModule(moduleName, localSettings.value.modules[moduleName]);
};

// 模块可见性改变
const handleModuleVisibilityChange = (moduleName, visible) => {
  personalizationStore.updateModule(moduleName, { visible });
};

// 暗夜模式切换
const handleDarkModeToggle = () => {
  personalizationStore.toggleDarkMode();
  // 同步本地设置
  localSettings.value = initLocalSettings();
  ElMessage.success(localSettings.value.darkMode ? '暗夜模式已开启' : '暗夜模式已关闭');
};

// 保存设置
const handleSave = () => {
  // 同步所有模块设置
  Object.keys(localSettings.value.modules).forEach((moduleName) => {
    personalizationStore.updateModule(moduleName, localSettings.value.modules[moduleName]);
  });
  ElMessage.success('个性化设置已保存');
  visible.value = false;
};

// 恢复默认
const handleReset = () => {
  personalizationStore.resetToDefault();
  localSettings.value = initLocalSettings();
  ElMessage.success('已恢复默认设置');
};

// 当面板打开时，重新同步本地设置
watch(
  () => props.modelValue,
  (isVisible) => {
    if (isVisible) {
      // 面板打开时，重新初始化本地设置
      localSettings.value = initLocalSettings();
    }
  }
);

// 监听store变化，同步到本地设置
watch(
  () => personalizationStore.$state,
  (newState) => {
    try {
      localSettings.value = JSON.parse(JSON.stringify(newState));
    } catch (e) {
      console.error('Failed to sync local settings:', e);
      localSettings.value = initLocalSettings();
    }
  },
  { deep: true }
);
</script>

<style scoped>
.personalization-panel {
  padding: 20px;
}

.setting-card {
  margin-bottom: 20px;
}

.dark-mode-card {
  border: 2px solid #409EFF;
}

.dark-mode-description {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  margin-top: 12px;
}

.dark-mode-description p {
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.color-picker-group {
  display: flex;
  align-items: center;
}

.preset-colors {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.preset-color-item {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  cursor: pointer;
  border: 2px solid #ebeef5;
  transition: transform 0.2s;
}

.preset-color-item:hover {
  transform: scale(1.1);
  border-color: #409eff;
}

.module-settings {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-item label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}
</style>

