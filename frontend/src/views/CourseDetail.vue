<template>
  <div class="course-detail">
    <el-header class="header">
      <div class="header-content">
        <el-button text @click="goBack" :icon="ArrowLeft">返回</el-button>
        <h1 class="header-title">{{ courseInfo?.course_name || '课程详情' }}</h1>
        <div></div>
      </div>
    </el-header>

    <div class="course-detail-container">
      <el-skeleton v-if="loading" animated :count="5" />
      <template v-else>
        <!-- 课程信息展示 -->
        <el-card v-if="courseInfo" class="course-info-card" shadow="never">
          <div class="course-info">
            <h2>{{ courseInfo.course_name }}</h2>
            <p class="course-code">课程代码：{{ courseInfo.course_code }}</p>
            <p v-if="courseInfo.description" class="course-announcement">
              <strong>公告：</strong>{{ courseInfo.description }}
            </p>
          </div>
        </el-card>

        <!-- 作业列表 -->
        <el-card class="homework-list-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">任务清单</span>
            </div>
          </template>

          <div v-if="homeworks.length > 0" class="homework-list">
            <div
              v-for="hw in homeworks"
              :key="hw.id"
              class="homework-item"
              @click="goToHomework(hw)"
            >
              <div class="homework-item-left">
                <span
                  class="status-icon"
                  :class="`status-${getStatusTag(hw).type}`"
                ></span>
              </div>
              <div class="homework-item-middle">
                <div class="homework-title-row">
                  <span class="homework-title">{{ hw.title }}</span>
                </div>
                <div class="homework-meta-row">
                  <span class="homework-deadline">
                    截止：{{ formatDateTime(hw.deadline) }}
                  </span>
                  <span
                    v-if="hw.submission?.submit_time"
                    class="homework-submission-time"
                  >
                    最近提交：{{ formatDateTime(hw.submission.submit_time) }}
                  </span>
                </div>
              </div>
              <div class="homework-item-right" @click.stop>
                <el-tag :type="getStatusTag(hw).type" effect="plain" class="homework-status-tag">
                  {{ getStatusTag(hw).label }}
                </el-tag>
                <div class="homework-actions">
                  <el-button type="primary" text size="small" @click="goToHomework(hw)">
                    查看详情
                  </el-button>
                  <el-button
                    v-if="hw.submission"
                    type="success"
                    text
                    size="small"
                    @click="viewSubmission(hw)"
                  >
                    查看提交
                  </el-button>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无作业，享受没有作业的宁静吧～" :image-size="100" />
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { ArrowLeft } from '@element-plus/icons-vue';
import { fetchCourseHomeworks, fetchStudentCourses, fetchHomeworkSubmission } from '@/api/student';
import { useUserStore } from '@/store/user';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const loading = ref(false);
const courseInfo = ref(null);
const homeworks = ref([]);

// 获取课程ID
const courseId = computed(() => parseInt(route.params.id));

// 返回上一页
const goBack = () => {
  router.push({ name: 'StudentHome' });
};

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '未设置';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// 获取作业状态标签（配合统一的状态色彩规范）
const getStatusTag = (homework) => {
  const now = new Date();
  const deadline = homework.deadline ? new Date(homework.deadline) : null;
  const submission = homework.submission;

  if (submission) {
    if (submission.is_graded) {
      return { type: 'success', label: '已批改' };
    } else {
      // 已提交但未批改，视为进行中，使用 success/primary 色系
      return { type: 'success', label: '已提交' };
    }
  }

  // 如果未提交，根据截止时间判断
  if (deadline) {
    if (now > deadline) {
      // 已截止但未提交，使用 info（灰色）
      return { type: 'info', label: '待提交（已截止）' };
    } else {
      // 未提交且未截止，使用 warning（橙色）
      return { type: 'warning', label: '待提交' };
    }
  }

  return { type: 'warning', label: '待提交' };
};

// 跳转到作业详情
const goToHomework = (homework) => {
  router.push({ name: 'HomeworkView', params: { id: homework.id } });
};

// 查看提交（跳转到提交查看页面，只读模式）
const viewSubmission = (homework) => {
  router.push({ name: 'SubmissionView', params: { id: homework.id } });
};

// 获取数据
const fetchData = async () => {
  loading.value = true;
  try {
    // 获取课程信息
    const coursesRes = await fetchStudentCourses();
    const courseList = coursesRes.data?.course_list || [];
    courseInfo.value = courseList.find(c => c.id === courseId.value);

    if (!courseInfo.value) {
      ElMessage.error('课程不存在或无权访问');
      router.push({ name: 'StudentHome' });
      return;
    }

    // 获取作业列表（后端已包含提交状态）
    const homeworksRes = await fetchCourseHomeworks(courseId.value);
    const homeworkList = homeworksRes.data?.homework_list || [];

    // 直接使用后端返回的数据，不再主动获取提交记录
    homeworks.value = homeworkList;
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else if (status === 403) {
      ElMessage.error('无权访问该课程');
      router.push({ name: 'StudentHome' });
    } else {
      ElMessage.error(error?.response?.data?.error || '获取课程信息失败');
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchData();
});
</script>

<script>
export default {
  name: 'CourseDetail',
};
</script>

<style scoped>
.course-detail {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px;
  height: 60px;
  line-height: 60px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  flex: 1;
  text-align: center;
}

.course-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.course-info-card {
  margin-bottom: 24px;
}

.course-info h2 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.course-code {
  font-size: 14px;
  color: #909399;
  margin: 8px 0;
}

.course-announcement {
  font-size: 14px;
  color: #606266;
  margin: 12px 0 0 0;
  line-height: 1.6;
}

.homework-list-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* 列表卡片样式 */
.homework-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.homework-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 10px;
  transition: background-color 0.2s ease, transform 0.1s ease;
  cursor: pointer;
}

.homework-item:hover {
  background-color: #f9fafb;
  transform: translateY(-1px);
}

.homework-item-left {
  margin-right: 12px;
}

.status-icon {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background-color: #dcdfe6;
}

.status-icon.status-success {
  background-color: #67c23a;
}

.status-icon.status-warning {
  background-color: #e6a23c;
}

.status-icon.status-info {
  background-color: #909399;
}

.homework-item-middle {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.homework-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.homework-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.homework-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  color: #909399;
}

.homework-deadline {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.homework-submission-time {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.homework-item-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  margin-left: 16px;
}

.homework-status-tag {
  font-size: 12px;
}

.homework-actions {
  display: flex;
  gap: 4px;
}

@media (max-width: 768px) {
  .course-detail-container {
    padding: 16px;
  }

  .header-title {
    font-size: 18px;
  }
}
</style>
