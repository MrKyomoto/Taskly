<template>
  <div class="empty-state" :class="{ 'empty-state-compact': compact }">
    <el-empty
      :description="description"
      :image-size="imageSize"
    >
      <template v-if="actionText" #default>
        <el-button
          v-if="actionText"
          :type="actionType"
          @click="$emit('action')"
        >
          {{ actionText }}
        </el-button>
      </template>
    </el-empty>
  </div>
</template>

<script setup>
defineProps({
  description: {
    type: String,
    default: '暂无数据',
  },
  imageSize: {
    type: Number,
    default: 100,
  },
  actionText: {
    type: String,
    default: '',
  },
  actionType: {
    type: String,
    default: 'primary',
  },
  compact: {
    type: Boolean,
    default: false,
  },
});

defineEmits(['action']);
</script>

<style scoped>
.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.empty-state-compact {
  padding: 20px;
}
</style>

