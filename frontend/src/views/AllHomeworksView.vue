<template>
  <div class="all-homeworks-view fade-in">
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
              <el-statistic 
                title="待提交作业" 
                :value="stats.pending"
                :value-style="{ color: '#409EFF' }"
              />
            </el-col>
            <el-col :span="6">
              <el-statistic 
                title="已提交" 
                :value="stats.submitted"
                :value-style="{ color: '#E6A23C' }"
              />
            </el-col>
            <el-col :span="6">
              <el-statistic 
                title="已完成" 
                :value="stats.completed"
                :value-style="{ color: '#67C23A' }"
              />
            </el-col>
            <el-col :span="6">
              <el-statistic 
                title="已逾期" 
                :value="stats.overdue"
                :value-style="{ color: '#F56C6C' }"
              />
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
            v-if="paginatedHomeworks.length > 0"
            :data="paginatedHomeworks"
            style="width: 100%"
            @row-click="goToHomework"
            :row-class-name="getRowClassName"
            stripe
            highlight-current-row
          >
            <el-table-column prop="course_name" label="课程" width="150" align="center" />
            <el-table-column prop="title" label="作业标题" min-width="200" align="center" />
            <el-table-column label="状态" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusTag(row).type" effect="plain">
                  {{ getStatusTag(row).label }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="截止时间" width="180" align="center">
              <template #default="{ row }">
                {{ formatDateTime(row.deadline) }}
              </template>
            </el-table-column>
            <el-table-column label="提交时间" width="180" align="center">
              <template #default="{ row }">
                <span v-if="row.submission?.submit_time">
                  {{ formatDateTime(row.submission.submit_time) }}
                </span>
                <span v-else class="text-muted">未提交</span>
              </template>
            </el-table-column>
            <el-table-column label="成绩" width="100" align="center">
              <template #default="{ row }">
                <span v-if="row.submission?.score !== undefined && row.submission?.score !== null" class="score-text">
                  {{ row.submission.score }} 分
                </span>
                <span v-else class="text-muted">未批改</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="170" fixed="right" align="center">
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
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { ArrowLeft } from '@element-plus/icons-vue';
import { fetchStudentCourses, fetchCourseHomeworks } from '@/api/student';
import { useUserStore } from '@/store/user';
import { formatDateTime as formatDateUtil } from '@/utils/date-formatter';
import { getCurrentSemester } from '@/utils/semester';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const loading = ref(false);
const courses = ref([]);
const homeworks = ref([]);
const activeFilter = ref('all');
const selectedCourseId = ref('all');
const currentPage = ref(1);
const pageSize = ref(20); // 每页显示20条

// 获取当前查看的学期（从路由参数或当前学期）
const viewingSemester = computed(() => {
  // 如果路由中有学期参数（历史学期），使用它
  if (route.params.semester) {
    return route.params.semester;
  }
  // 否则使用当前学期
  const currentSemesterInfo = getCurrentSemester();
  return currentSemesterInfo.semester;
});

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
  // 重置分页
  currentPage.value = 1;
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
    if (!deadlineDate) {
      // 没有截止日期，根据提交状态判断
      if (hw.submission) {
        if (hw.submission.is_graded) {
          stats.completed++;
        } else {
          stats.submitted++;
        }
      } else {
        stats.pending++;
      }
      return;
    }
    
    const submissionTime = hw.submission?.submit_time ? new Date(hw.submission.submit_time) : null;
    const submittedBeforeDeadline = submissionTime && submissionTime <= deadlineDate;
    const isOverdue = deadlineDate < now;
    
    if (hw.submission) {
      // 如果已提交
      if (submittedBeforeDeadline) {
        // 在ddl前提交
      if (hw.submission.is_graded || isOverdue) {
        stats.completed++;
      } else {
        stats.submitted++;
      }
      } else {
        // 在ddl后提交，算作已逾期
        stats.overdue++;
      }
    } else {
      // 未提交
      if (isOverdue) {
      stats.overdue++;
    } else {
      stats.pending++;
      }
    }
  });

  return stats;
});

// 筛选后的作业列表
const filteredHomeworks = computed(() => {
  let filtered = homeworks.value;
  const now = new Date();

  // 首先按学期筛选（只显示当前查看学期的作业）
  filtered = filtered.filter((hw) => {
    // 找到作业对应的课程
    const course = courses.value.find(c => c.id === hw.course_id);
    return course && course.semester === viewingSemester.value;
  });

  // 按课程筛选
  if (selectedCourseId.value !== 'all') {
    filtered = filtered.filter((hw) => hw.course_id === selectedCourseId.value);
  }

  // 按状态筛选
  if (activeFilter.value !== 'all') {
    filtered = filtered.filter((hw) => {
      const deadlineDate = hw.deadline ? new Date(hw.deadline) : null;
      if (!deadlineDate) {
        // 没有截止日期的作业，根据筛选条件处理
        if (activeFilter.value === 'overdue') {
          return false; // 没有截止日期不算逾期
        }
        // 其他筛选条件继续处理
      }
      
      const submissionTime = hw.submission?.submit_time ? new Date(hw.submission.submit_time) : null;
      const submittedBeforeDeadline = submissionTime && deadlineDate && submissionTime <= deadlineDate;
      
      // 已逾期：已过ddl且（未提交 或 在ddl之后才提交）
      const isOverdue = deadlineDate && deadlineDate < now && (!hw.submission || !submittedBeforeDeadline);
      
      switch (activeFilter.value) {
        case 'pending':
          // 待提交：没有逾期并且待提交的作业
          return !hw.submission && !isOverdue;
        case 'submitted':
          // 已提交：已经提交的作业且没有到达ddl，或者在ddl前提交的
          return hw.submission && !hw.submission.is_graded && deadlineDate && deadlineDate >= now && submittedBeforeDeadline;
        case 'completed':
          // 已完成：已经提交过的作业而且在ddl前提交，且已过ddl
          return hw.submission && deadlineDate && deadlineDate < now && submittedBeforeDeadline;
        case 'overdue':
          // 已逾期：已过ddl且（未提交 或 在ddl之后才提交）
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

// 分页后的作业列表
const paginatedHomeworks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return filteredHomeworks.value.slice(start, end);
});

// 处理分页变化
const handlePageChange = (page) => {
  currentPage.value = page;
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// 返回上一页
const goBack = () => {
  // 使用 router.back() 返回到上一个页面
  // 如果浏览器历史记录中没有上一个页面，则返回到主页
  if (window.history.length > 1) {
    router.back();
  } else {
  router.push({ name: 'StudentHome' });
  }
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
    const deadlineDate = row.deadline ? new Date(row.deadline) : null;
    const now = new Date();
    const isOverdue = deadlineDate && deadlineDate < now;
  
  // 检查是否在ddl前提交：如果提交时间在ddl之后或没有提交时间，视为未在ddl前提交
  const submissionTime = row.submission?.submit_time ? new Date(row.submission.submit_time) : null;
  const submittedBeforeDeadline = submissionTime && deadlineDate && submissionTime <= deadlineDate;
  
  // 如果已过ddl且没有在ddl前提交，即使有批改记录（老师批改0分），也应该显示"已逾期"
  if (isOverdue && !submittedBeforeDeadline) {
    return { type: 'danger', label: '已逾期' };
  }
  
  // 如果有提交记录（在ddl前提交的）
  if (row.submission && submittedBeforeDeadline) {
    // 如果已批改，显示为已完成
    if (row.submission.is_graded) {
      return { type: 'success', label: '已完成' };
    } else {
      return { type: 'warning', label: '已提交' };
    }
  }
  
  // 如果没有提交，再检查是否逾期
  if (isOverdue) {
    return { type: 'danger', label: '已逾期' };
  } else {
    return { type: 'info', label: '待提交' };
  }
};

// 获取行样式类
const getRowClassName = ({ row }) => {
  const deadlineDate = row.deadline ? new Date(row.deadline) : null;
  const now = new Date();
  const isOverdue = deadlineDate && deadlineDate < now;
  
  // 检查是否在ddl前提交
  const submissionTime = row.submission?.submit_time ? new Date(row.submission.submit_time) : null;
  const submittedBeforeDeadline = submissionTime && deadlineDate && submissionTime <= deadlineDate;
  
  // 如果已过ddl且没有在ddl前提交，显示逾期样式
  if (isOverdue && !submittedBeforeDeadline) {
    return 'overdue-row';
  }
  return '';
};

// 格式化日期时间
const formatDateTime = (dateString) => {
  return formatDateUtil(dateString, 'YYYY-MM-DD HH:mm');
};

// 筛选改变
// 课程改变
const handleCourseChange = () => {
  // 筛选逻辑已在 computed 中处理
  // 重置分页
  currentPage.value = 1;
};

// 处理筛选变化
const handleFilterChange = () => {
  // 重置分页
  currentPage.value = 1;
};

// 获取数据
const fetchData = async () => {
  loading.value = true;
  try {
    // 获取所有课程列表
    const coursesRes = await fetchStudentCourses();
    const allCourses = coursesRes.data?.course_list || [];

    // 只显示当前查看学期的课程
    courses.value = allCourses.filter(course => course.semester === viewingSemester.value);

    // 只获取当前查看学期的课程的作业
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
        // 静默处理单个课程获取失败，不影响其他课程
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

// 监听学期变化，重新获取数据
watch(viewingSemester, () => {
  fetchData();
}, { immediate: false });

// 监听路由变化，当从历史学期页面跳转过来时重新获取数据
watch(() => route.params.semester, () => {
  fetchData();
}, { immediate: false });
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
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stats-card,
.filter-card,
.homeworks-card {
  margin-bottom: 24px;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.stats-card:hover,
.filter-card:hover,
.homeworks-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
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
  color: #909399;
  font-style: italic;
}

.score-text {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
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

