<template>
  <div class="course-detail fade-in">
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

        <!-- 教师信息卡片 -->
        <section class="teacher-section" v-if="teacherList.length > 0">
          <div class="teacher-section-header">
            <h3 class="teacher-section-title">教师信息</h3>
            <el-tag type="primary" size="small">{{ teacherList.length }} 位教师</el-tag>
          </div>
          <div class="teacher-cards-grid">
            <el-card
              v-for="teacher in teacherList"
              :key="teacher.id"
              shadow="hover"
              class="teacher-card-item"
            >
              <div class="teacher-card-content">
                <div class="teacher-card-header-info">
                  <div class="teacher-avatar">
                    <el-icon :size="32"><UserFilled /></el-icon>
                  </div>
                  <div class="teacher-header-text">
                    <div class="teacher-name-row">
                      <span class="teacher-name">{{ teacher.name }}</span>
                      <el-tag type="primary" size="small" effect="plain">{{ teacher.role || '主讲教师' }}</el-tag>
                    </div>
                    <div class="teacher-staff-no">工号：{{ teacher.staff_no }}</div>
                  </div>
                </div>
                <div class="teacher-card-details">
                  <div class="teacher-detail-row" v-if="teacher.email">
                    <el-icon class="teacher-detail-icon"><Message /></el-icon>
                    <span class="teacher-detail-text">{{ teacher.email }}</span>
                  </div>
                  <div class="teacher-detail-row" v-if="teacher.phone">
                    <el-icon class="teacher-detail-icon"><Phone /></el-icon>
                    <span class="teacher-detail-text">{{ teacher.phone }}</span>
                  </div>
                  <div class="teacher-detail-row" v-if="!teacher.email && !teacher.phone">
                    <span class="teacher-detail-text teacher-no-contact">暂无联系方式</span>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </section>

        <!-- 助教信息卡片 -->
        <section class="teacher-section" v-if="taList.length > 0 || loadingTAs">
          <div v-if="loadingTAs" class="loading-placeholder">正在加载助教信息...</div>
          <template v-else-if="taList.length > 0">
          <div class="teacher-section-header">
            <h3 class="teacher-section-title">助教信息</h3>
            <el-tag type="info" size="small">{{ taList.length }} 位助教</el-tag>
          </div>
          <div class="teacher-cards-grid">
            <el-card
              v-for="ta in taList"
              :key="ta.id"
              shadow="hover"
              class="teacher-card-item"
            >
              <div class="teacher-card-content">
                <div class="teacher-card-header-info">
                  <div class="teacher-avatar ta-avatar">
                    <el-icon :size="32"><UserFilled /></el-icon>
                  </div>
                  <div class="teacher-header-text">
                    <div class="teacher-name-row">
                      <span class="teacher-name">{{ ta.name }}</span>
                      <el-tag type="success" size="small" effect="plain">助教</el-tag>
                    </div>
                    <div class="teacher-staff-no">学号：{{ ta.student_no }}</div>
                  </div>
                </div>
                <div class="teacher-card-details">
                  <div class="teacher-detail-row" v-if="ta.email">
                    <el-icon class="teacher-detail-icon"><Message /></el-icon>
                    <span class="teacher-detail-text">{{ ta.email }}</span>
                  </div>
                  <div class="teacher-detail-row" v-if="ta.phone">
                    <el-icon class="teacher-detail-icon"><Phone /></el-icon>
                    <span class="teacher-detail-text">{{ ta.phone }}</span>
                  </div>
                  <div class="teacher-detail-row" v-if="!ta.email && !ta.phone">
                    <span class="teacher-detail-text teacher-no-contact">暂无联系方式</span>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
          </template>
          <div v-else class="empty-placeholder" style="padding: 20px; text-align: center; color: #909399;">
            暂无助教信息
          </div>
        </section>

        <!-- 作业列表 -->
        <el-card class="homework-list-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">任务清单</span>
            </div>
          </template>

          <div v-if="displayedHomeworks.length > 0" class="homework-list">
            <div
              v-for="hw in displayedHomeworks"
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
          
          <!-- 显示更多/收起按钮 -->
          <div v-if="homeworks.length > pageSize" class="homework-list-footer">
            <el-button 
              type="primary" 
              text 
              @click="showAllHomeworks = !showAllHomeworks"
            >
              {{ showAllHomeworks ? '收起' : `查看更多 (共 ${homeworks.length} 项)` }}
            </el-button>
          </div>
        </el-card>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { ArrowLeft, UserFilled, Message, Phone } from '@element-plus/icons-vue';
import { fetchCourseHomeworks, fetchStudentCourses, fetchHomeworkSubmission, fetchCourseTeachers, fetchCourseTAs } from '@/api/student';
import { useUserStore } from '@/store/user';
import { formatDateTime as formatDateUtil } from '@/utils/date-formatter';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const loading = ref(false);
const courseInfo = ref(null);
const homeworks = ref([]);
const currentPage = ref(1);
const pageSize = ref(20); // 每页显示20条作业
const showAllHomeworks = ref(false); // 是否显示所有作业
const teacherList = ref([]);
const taList = ref([]);
const loadingTeachers = ref(false);
const loadingTAs = ref(false);

// 获取课程ID
const courseId = computed(() => parseInt(route.params.id));

// 显示的作业列表（根据是否展开）
const displayedHomeworks = computed(() => {
  if (showAllHomeworks.value || homeworks.value.length <= pageSize.value) {
    return homeworks.value;
  }
  return homeworks.value.slice(0, pageSize.value);
});

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

// 格式化日期时间
const formatDateTime = (dateString) => {
  return formatDateUtil(dateString, 'YYYY-MM-DD HH:mm');
};

// 获取作业状态标签（配合统一的状态色彩规范，与所有作业页面逻辑一致）
const getStatusTag = (homework) => {
  const deadlineDate = homework.deadline ? new Date(homework.deadline) : null;
  const now = new Date();
  const isOverdue = deadlineDate && deadlineDate < now;

  // 检查是否在ddl前提交：如果提交时间在ddl之后或没有提交时间，视为未在ddl前提交
  const submissionTime = homework.submission?.submit_time ? new Date(homework.submission.submit_time) : null;
  const submittedBeforeDeadline = submissionTime && deadlineDate && submissionTime <= deadlineDate;

  // 如果已过ddl且没有在ddl前提交，即使有批改记录（老师批改0分），也应该显示"已逾期"
  if (isOverdue && !submittedBeforeDeadline) {
    return { type: 'danger', label: '已逾期' };
  }

  // 如果有提交记录（在ddl前提交的）
  if (homework.submission && submittedBeforeDeadline) {
    // 如果已批改，显示为已完成
    if (homework.submission.is_graded) {
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

    // 获取教师列表
    await fetchTeachers();

    // 获取助教列表
    await fetchTAs();
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

// 获取教师列表
const fetchTeachers = async () => {
  loadingTeachers.value = true;
  try {
    console.log('学生端：开始获取教师列表，courseId:', courseId.value);
    const res = await fetchCourseTeachers(courseId.value);
    console.log('学生端：获取教师列表响应:', res);
    console.log('学生端：教师数据:', res.data);
    teacherList.value = res.data?.teacher_list || [];
    console.log('学生端：最终教师列表:', teacherList.value);
  } catch (error) {
    console.error('学生端：获取教师列表失败:', error);
    console.error('学生端：错误详情:', error?.response?.data);
    console.error('学生端：错误状态码:', error?.response?.status);
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else if (status === 403) {
      // 无权查看教师列表，静默失败
      console.warn('学生端：无权查看教师列表');
      teacherList.value = [];
    } else {
      // 其他错误也静默失败，不影响主流程
      console.warn('学生端：获取教师列表失败，状态码:', status);
      teacherList.value = [];
    }
  } finally {
    loadingTeachers.value = false;
  }
};

// 获取助教列表
const fetchTAs = async () => {
  loadingTAs.value = true;
  try {
    console.log('学生端：开始获取助教列表，courseId:', courseId.value);
    const res = await fetchCourseTAs(courseId.value);
    console.log('学生端：获取助教列表响应:', res);
    console.log('学生端：助教数据:', res.data);
    taList.value = res.data?.ta_list || [];
    console.log('学生端：最终助教列表:', taList.value);
  } catch (error) {
    console.error('学生端：获取助教列表失败:', error);
    console.error('学生端：错误详情:', error?.response?.data);
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else if (status === 403) {
      // 无权查看助教列表，静默失败
      console.warn('学生端：无权查看助教列表');
      taList.value = [];
    } else {
      // 其他错误也静默失败，不影响主流程
      console.warn('学生端：获取助教列表失败，状态码:', status);
      taList.value = [];
    }
  } finally {
    loadingTAs.value = false;
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
  transition: background-color 0.2s ease, transform 0.1s ease, box-shadow 0.2s ease;
  cursor: pointer;
  border: 1px solid transparent;
}

.homework-item:hover {
  background-color: #f9fafb;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-color: #e4e7ed;
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

/* 教师和助教信息卡片样式 */
.teacher-section {
  margin-bottom: 24px;
}

.teacher-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.teacher-section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.teacher-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.teacher-card-item {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.teacher-card-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.teacher-card-content {
  padding: 4px;
}

.teacher-card-header-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.teacher-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
}

.ta-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.teacher-header-text {
  flex: 1;
  min-width: 0;
}

.teacher-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.teacher-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.teacher-staff-no {
  font-size: 13px;
  color: #909399;
}

.teacher-card-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.teacher-detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.teacher-detail-icon {
  color: #909399;
  font-size: 16px;
  flex-shrink: 0;
}

.teacher-detail-text {
  flex: 1;
  min-width: 0;
  word-break: break-all;
}

.teacher-no-contact {
  color: #c0c4cc;
  font-style: italic;
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
