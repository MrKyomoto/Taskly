<template>
  <div class="all-homeworks-view">
    <el-header class="header">
      <div class="header-content">
        <el-button text @click="goBack" :icon="ArrowLeft">返回</el-button>
        <h1 class="header-title">{{ pageTitle }}</h1>
        <div></div>
      </div>
    </el-header>

    <div class="homeworks-container">
      <el-skeleton v-if="loading" animated :count="5" />
      <template v-else>
        <!-- 统计信息 -->
        <el-card class="stats-card" shadow="never">
          <el-row :gutter="20">
            <el-col :span="6">
              <el-statistic title="待提交作业" :value="stats.pending" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="已提交" :value="stats.submitted" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="已完成" :value="stats.completed" />
            </el-col>
            <el-col :span="6">
              <el-statistic title="已逾期" :value="stats.overdue" />
            </el-col>
          </el-row>
        </el-card>

        <!-- 筛选栏 -->
        <el-card class="filter-card" shadow="never">
          <el-space>
            <span>筛选：</span>
            <el-radio-group v-model="activeFilter" @change="handleFilterChange">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="pending">待提交</el-radio-button>
              <el-radio-button label="submitted">已提交</el-radio-button>
              <el-radio-button label="completed">已完成</el-radio-button>
              <el-radio-button label="overdue">已逾期</el-radio-button>
            </el-radio-group>
            <el-select
              v-model="selectedCourseId"
              placeholder="选择课程"
              clearable
              style="width: 200px"
              @change="handleCourseChange"
            >
              <el-option label="全部课程" value="all" />
              <el-option
                v-for="course in courses"
                :key="course.id"
                :label="course.course_name"
                :value="course.id"
              />
            </el-select>
          </el-space>
        </el-card>

        <!-- 作业列表 -->
        <el-card class="homeworks-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">作业列表</span>
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
                <el-tag :type="getStatusTag(row).type" effect="plain">
                  {{ getStatusTag(row).label }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="截止时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.deadline) }}
              </template>
            </el-table-column>
            <el-table-column label="提交时间" width="180">
              <template #default="{ row }">
                <span v-if="row.submission?.submit_time">
                  {{ formatDateTime(row.submission.submit_time) }}
                </span>
                <span v-else class="text-muted">未提交</span>
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
            <el-table-column label="操作" width="170" fixed="right">
              <template #default="{ row }">
                <div class="table-actions">
                  <el-button type="primary" link size="small" @click.stop="goToHomework(row)">
                    查看详情
                  </el-button>
                  <el-button
                    v-if="row.submission"
                    type="success"
                    link
                    size="small"
                    @click.stop="viewSubmission(row)"
                  >
                    查看提交
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无符合筛选条件的作业" :image-size="100" />
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
const activeFilter = ref('all');
const selectedCourseId = ref('all');

// 根据路由参数设置页面标题和默认筛选
const pageTitle = computed(() => {
  const filter = route.query.filter || route.params.filter || 'all';
  switch (filter) {
    case 'pending':
      return '待提交作业';
    case 'submitted':
      return '已提交作业';
    case 'completed':
      return '已完成作业';
    default:
      return '所有作业';
  }
});

// 初始化筛选模式
const initFilter = () => {
  // 从路由路径判断筛选模式
  const path = route.path;
  if (path.includes('/pending')) {
    activeFilter.value = 'pending';
  } else if (path.includes('/submitted')) {
    activeFilter.value = 'submitted';
  } else if (path.includes('/completed')) {
    activeFilter.value = 'completed';
  } else {
    const filter = route.query.filter || 'all';
    activeFilter.value = filter;
  }
};

// 统计数据
const stats = computed(() => {
  const stats = {
    pending: 0,
    submitted: 0,
    completed: 0,
    overdue: 0,
  };

  const now = new Date();
  homeworks.value.forEach((hw) => {
    const deadlineDate = hw.deadline ? new Date(hw.deadline) : null;
    const isOverdue = deadlineDate && deadlineDate < now;
    // 已逾期：ddl之前还没提交的作业
    const isOverdueAndNotSubmitted = isOverdue && !hw.submission;
    
    if (hw.submission) {
      // 如果已过ddl且已提交，算作已完成
      if (hw.submission.is_graded || isOverdue) {
        stats.completed++;
      } else {
        stats.submitted++;
      }
    } else if (isOverdueAndNotSubmitted) {
      stats.overdue++;
    } else {
      stats.pending++;
    }
  });

  return stats;
});

// 筛选后的作业列表
const filteredHomeworks = computed(() => {
  let filtered = homeworks.value;
  const now = new Date();

  // 按课程筛选
  if (selectedCourseId.value !== 'all') {
    filtered = filtered.filter((hw) => hw.course_id === selectedCourseId.value);
  }

  // 按状态筛选
  if (activeFilter.value !== 'all') {
    filtered = filtered.filter((hw) => {
      const deadlineDate = hw.deadline ? new Date(hw.deadline) : null;
      // 已逾期：ddl之前还没提交的作业
      const isOverdue = deadlineDate && deadlineDate < now && !hw.submission;
      
      switch (activeFilter.value) {
        case 'pending':
          // 待提交：没有逾期并且待提交的作业
          return !hw.submission && !isOverdue;
        case 'submitted':
          // 已提交：已经提交的作业且没有到达ddl
          return hw.submission && !hw.submission.is_graded && deadlineDate && deadlineDate >= now;
        case 'completed':
          // 已完成：已经提交过的作业而且已经过了ddl
          return hw.submission && deadlineDate && deadlineDate < now;
        case 'overdue':
          // 已逾期：ddl之前还没提交的作业
          return isOverdue;
        default:
          return true;
      }
    });
  }

  // 按截止时间排序
  return filtered.sort((a, b) => {
    if (!a.deadline && !b.deadline) return 0;
    if (!a.deadline) return 1;
    if (!b.deadline) return -1;
    return new Date(a.deadline) - new Date(b.deadline);
  });
});

// 返回上一页
const goBack = () => {
  router.push({ name: 'StudentHome' });
};

// 跳转到作业详情
const goToHomework = (homework) => {
  router.push({ name: 'HomeworkView', params: { id: homework.id } });
};

// 查看提交
const viewSubmission = (homework) => {
  router.push({ name: 'SubmissionView', params: { id: homework.id } });
};

// 获取状态标签
const getStatusTag = (row) => {
  // 优先检查提交状态：已完成的作业一定不是已逾期
  if (row.submission) {
    const deadlineDate = row.deadline ? new Date(row.deadline) : null;
    const now = new Date();
    const isOverdue = deadlineDate && deadlineDate < now;
    // 如果已过ddl且已提交，显示为已完成
    if (row.submission.is_graded || isOverdue) {
      return { type: 'success', label: '已完成' };
    } else {
      return { type: 'warning', label: '已提交' };
    }
  }
  // 如果没有提交，再检查是否逾期
  const deadlineDate = row.deadline ? new Date(row.deadline) : null;
  const now = new Date();
  const isOverdue = deadlineDate && deadlineDate < now;
  if (isOverdue) {
    return { type: 'danger', label: '已逾期' };
  } else {
    return { type: 'info', label: '待提交' };
  }
};

// 获取行样式类
const getRowClassName = ({ row }) => {
  // 只有未提交且已逾期的作业才显示逾期样式
  // 已完成的作业一定不是已逾期
  if (row.submission) {
    return '';
  }
  const deadlineDate = row.deadline ? new Date(row.deadline) : null;
  const now = new Date();
  const isOverdue = deadlineDate && deadlineDate < now;
  if (isOverdue) {
    return 'overdue-row';
  }
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

// 筛选改变
const handleFilterChange = () => {
  // 筛选逻辑已在 computed 中处理
};

// 课程改变
const handleCourseChange = () => {
  // 筛选逻辑已在 computed 中处理
};

// 获取数据
const fetchData = async () => {
  loading.value = true;
  try {
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
  initFilter();
  fetchData();
});
</script>

<style scoped>
.all-homeworks-view {
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

.stats-card,
.filter-card,
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

.text-muted {
  color: #c0c4cc;
}

.score-text {
  font-weight: 600;
  color: #409eff;
}

.table-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.table-actions .el-button {
  padding-left: 8px;
  padding-right: 8px;
}

:deep(.overdue-row) {
  background-color: #fef0f0;
}

:deep(.overdue-row:hover) {
  background-color: #fde2e2;
}
</style>

