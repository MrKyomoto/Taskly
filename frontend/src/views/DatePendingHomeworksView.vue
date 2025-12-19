<template>
  <div class="date-pending-homeworks-view">
    <el-header class="header">
      <div class="header-content">
        <el-button text @click="goBack" :icon="ArrowLeft">返回</el-button>
        <h1 class="header-title">{{ selectedDate }} 待提交作业</h1>
        <div></div>
      </div>
    </el-header>

    <div class="homeworks-container">
      <el-skeleton v-if="loading" animated :count="5" />
      <template v-else>
        <!-- 作业列表 -->
        <el-card class="homeworks-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">{{ selectedDate }} 待提交作业</span>
              <span class="card-count">共 {{ filteredHomeworks.length }} 项</span>
            </div>
          </template>

          <el-table
            v-if="filteredHomeworks.length > 0"
            :data="filteredHomeworks"
            style="width: 100%"
            @row-click="goToHomework"
            :row-class-name="getRowClassName"
          >
            <el-table-column prop="course_name" label="课程" width="150" />
            <el-table-column prop="title" label="作业标题" min-width="200" />
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag type="info" effect="plain">待提交</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="截止时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.deadline) }}
              </template>
            </el-table-column>
            <el-table-column label="成绩" width="100">
              <template #default="{ row }">
                <span v-if="row.submission?.score !== undefined && row.submission?.score !== null" class="score-text">
                  {{ row.submission.score }} 分
                </span>
                <span v-else class="text-muted">未批改</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <div class="table-actions">
                  <el-button type="primary" link size="small" @click.stop="goToHomework(row)">
                    查看详情
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="该日期暂无待提交的作业" :image-size="100" />
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { ArrowLeft } from '@element-plus/icons-vue';
import { fetchStudentCourses, fetchCourseHomeworks } from '@/api/student';
import { useUserStore } from '@/store/user';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const loading = ref(false);
const courses = ref([]);
const homeworks = ref([]);
const selectedDate = ref('');

// 筛选后的作业列表（只显示未提交且截止日期为选中日期的作业）
const filteredHomeworks = computed(() => {
  const now = new Date();
  return homeworks.value.filter((hw) => {
    // 只显示未提交的作业
    if (hw.submission) return false;
    
    // 检查截止日期是否匹配
    if (!hw.deadline) return false;
    const deadlineDate = new Date(hw.deadline);
    const deadlineDateStr = formatDateKey(deadlineDate);
    
    return deadlineDateStr === selectedDate.value;
  }).sort((a, b) => {
    // 按截止时间排序
    if (!a.deadline && !b.deadline) return 0;
    if (!a.deadline) return 1;
    if (!b.deadline) return -1;
    return new Date(a.deadline) - new Date(b.deadline);
  });
});

// 格式化日期为 YYYY-MM-DD
const formatDateKey = (date) => {
  if (!date) return '';
  const d = new Date(date);
  const year = d.getFullYear();
  const month = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// 返回上一页
const goBack = () => {
  router.push({ name: 'StudentHome' });
};

// 跳转到作业详情
const goToHomework = (homework) => {
  router.push({ name: 'HomeworkView', params: { id: homework.id } });
};

// 获取行样式类
const getRowClassName = ({ row }) => {
  return '';
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

// 获取数据
const fetchData = async () => {
  loading.value = true;
  try {
    // 从路由参数获取日期
    const dateParam = route.params.date;
    if (!dateParam) {
      ElMessage.error('缺少日期参数');
      router.push({ name: 'StudentHome' });
      return;
    }
    selectedDate.value = dateParam;

    // 获取课程列表
    const coursesRes = await fetchStudentCourses();
    courses.value = coursesRes.data?.course_list || [];

    // 获取所有课程的作业
    const homeworkPromises = courses.value.map(async (course) => {
      try {
        const hwRes = await fetchCourseHomeworks(course.id);
        const homeworkList = hwRes.data?.homework_list || [];
        return homeworkList.map((hw) => ({
          ...hw,
          course_id: course.id,
          course_name: course.course_name,
        }));
      } catch (error) {
        console.error(`获取课程 ${course.id} 的作业失败:`, error);
        return [];
      }
    });

    const homeworkArrays = await Promise.all(homeworkPromises);
    homeworks.value = homeworkArrays.flat();
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else {
      ElMessage.error(error?.response?.data?.error || '获取作业列表失败');
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.date-pending-homeworks-view {
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

.homeworks-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.homeworks-card {
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

.card-count {
  font-size: 14px;
  color: #909399;
}

.score-text {
  font-weight: 600;
  color: #409eff;
}

.table-actions {
  display: flex;
  align-items: center;
  justify-content: center;
}

.text-muted {
  color: #909399;
}
</style>

