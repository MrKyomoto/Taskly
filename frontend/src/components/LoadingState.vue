<template>
  <div class="loading-state" :class="{ 'loading-state-full': fullscreen }">
    <el-skeleton v-if="type === 'skeleton'" :animated="true" :count="count" />
    <div v-else class="loading-spinner">
      <el-icon class="is-loading" :size="size">
        <Loading />
      </el-icon>
      <p v-if="text" class="loading-text">{{ text }}</p>
    </div>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue';

defineProps({
  type: {
    type: String,
    default: 'spinner', // 'spinner' | 'skeleton'
  },
  fullscreen: {
    type: Boolean,
    default: false,
  },
  count: {
    type: Number,
    default: 4,
  },
  size: {
    type: Number,
    default: 40,
  },
  text: {
    type: String,
    default: '',
  },
});
</script>

<style scoped>
.loading-state {
  padding: 40px 20px;
  text-align: center;
}

.loading-state-full {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 9999;
}

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.loading-text {
  color: #909399;
  font-size: 14px;
  margin: 0;
}
</style>

