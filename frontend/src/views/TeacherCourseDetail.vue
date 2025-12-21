<template>
  <div class="teacher-course-detail">
    <el-header class="header">
      <div class="header-content">
        <el-button text @click="goBack" :icon="ArrowLeft">返回</el-button>
        <h1 class="header-title">{{ courseInfo?.course_name || '课程详情' }}</h1>
        <div></div>
      </div>
    </el-header>

    <div class="course-detail-container">
      <el-skeleton v-if="loading" animated :count="5" />
      <template v-else-if="courseInfo">
        <!-- 顶部横幅 -->
        <section class="course-hero">
          <div class="course-hero-left">
            <p class="hero-breadcrumb">课程详情</p>
            <h2 class="hero-title">{{ courseInfo.course_name }}</h2>
            <div class="hero-meta">
              <div
                class="hero-code-pill"
                @click="copyCourseCode(courseInfo.course_code)"
              >
                <span class="code-label">课程号</span>
                <span class="code-value">{{ courseInfo.course_code }}</span>
              </div>
              <span class="hero-text">学期：{{ courseInfo.semester || '未设置' }}</span>
              <span class="hero-text">已选人数：{{ courseInfo.student_count || 0 }} 人</span>
            </div>
          </div>
          <div class="course-hero-right">
            <el-statistic
              title="作业总数"
              :value="homeworks.length"
              value-style="color: #ffffff; font-weight: 600; font-size: 24px;"
            />
            <el-statistic
              title="已发布成绩作业"
              :value="publishedHomeworkCount"
              value-style="color: #ffffff; font-weight: 600; font-size: 24px;"
            />
          </div>
        </section>

        <!-- 教师信息卡片（助教登录时显示） -->
        <section class="ta-section" v-if="userStore.user?.role === 'ta' && teacherList.length > 0">
          <div class="ta-section-header">
            <h3 class="ta-section-title">教师信息</h3>
            <el-tag type="primary" size="small">{{ teacherList.length }} 位教师</el-tag>
          </div>
          <div class="ta-cards-grid">
            <el-card
              v-for="teacher in teacherList"
              :key="teacher.id"
              shadow="hover"
              class="ta-card-item"
            >
              <div class="ta-card-content">
                <div class="ta-card-header-info">
                  <div class="ta-avatar teacher-avatar">
                    <el-icon :size="32"><UserFilled /></el-icon>
                  </div>
                  <div class="ta-header-text">
                    <div class="ta-name-row">
                      <span class="ta-name">{{ teacher.name }}</span>
                      <el-tag type="primary" size="small" effect="plain">{{ teacher.role || '主讲教师' }}</el-tag>
                    </div>
                    <div class="ta-student-no">工号：{{ teacher.staff_no }}</div>
                  </div>
                </div>
                <div class="ta-card-details">
                  <div class="ta-detail-row" v-if="teacher.email">
                    <el-icon class="ta-detail-icon"><Message /></el-icon>
                    <span class="ta-detail-text">{{ teacher.email }}</span>
                  </div>
                  <div class="ta-detail-row" v-if="teacher.phone">
                    <el-icon class="ta-detail-icon"><Phone /></el-icon>
                    <span class="ta-detail-text">{{ teacher.phone }}</span>
                  </div>
                  <div class="ta-detail-row" v-if="!teacher.email && !teacher.phone">
                    <span class="ta-detail-text ta-no-contact">暂无联系方式</span>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </section>

        <!-- 助教信息卡片 -->
        <section class="ta-section" v-if="taList.length > 0">
          <div class="ta-section-header">
            <h3 class="ta-section-title">助教信息</h3>
            <el-tag type="info" size="small">{{ taList.length }} 位助教</el-tag>
          </div>
          <div class="ta-cards-grid">
            <el-card
              v-for="ta in taList"
              :key="ta.id"
              shadow="hover"
              class="ta-card-item"
            >
              <div class="ta-card-content">
                <div class="ta-card-header-info">
                  <div class="ta-avatar">
                    <el-icon :size="32"><UserFilled /></el-icon>
                  </div>
                  <div class="ta-header-text">
                    <div class="ta-name-row">
                      <span class="ta-name">{{ ta.name }}</span>
                      <el-tag type="success" size="small" effect="plain">助教</el-tag>
                    </div>
                    <div class="ta-student-no">学号：{{ ta.student_no }}</div>
                  </div>
                </div>
                <div class="ta-card-details">
                  <div class="ta-detail-row" v-if="ta.email">
                    <el-icon class="ta-detail-icon"><Message /></el-icon>
                    <span class="ta-detail-text">{{ ta.email }}</span>
                  </div>
                  <div class="ta-detail-row" v-if="ta.phone">
                    <el-icon class="ta-detail-icon"><Phone /></el-icon>
                    <span class="ta-detail-text">{{ ta.phone }}</span>
                  </div>
                  <div class="ta-detail-row" v-if="!ta.email && !ta.phone">
                    <span class="ta-detail-text ta-no-contact">暂无联系方式</span>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </section>

        <!-- 操作栏 -->
        <section class="course-toolbar">
          <div class="toolbar-left">
            <el-input
              v-model="homeworkSearch"
              placeholder="搜索作业标题..."
              clearable
              class="toolbar-search"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          <div class="toolbar-right">
            <el-button 
              v-if="userStore.user?.role === 'teacher'" 
              type="info" 
              @click="showAddTADialog = true"
            >
              <el-icon><UserFilled /></el-icon>
              添加助教
            </el-button>
            <el-button 
              type="success" 
              @click="handleExportGrades" 
              :loading="exporting"
            >
              <el-icon><Download /></el-icon>
              导出成绩
            </el-button>
            <el-button type="primary" @click="showCreateHomeworkDialog = true" :icon="Plus">
              发布新作业
            </el-button>
          </div>
        </section>

        <!-- 作业任务清单 -->
        <section class="homework-task-section">
          <div v-if="filteredHomeworks.length > 0" class="task-list">
            <transition-group name="fade-slide" tag="div">
              <div
                v-for="hw in filteredHomeworks"
                :key="hw.id"
                class="task-item"
                @click="goToGrading(hw)"
              >
                <div class="task-icon">
                  <el-icon v-if="hw.is_overdue && !hw.grades_published">
                    <CircleCheck />
                  </el-icon>
                  <el-icon v-else-if="hw.grades_published">
                    <Trophy />
                  </el-icon>
                  <el-icon v-else>
                    <Timer />
                  </el-icon>
                </div>
                <div class="task-main">
                  <div class="task-title-row">
                    <span class="task-title">{{ hw.title }}</span>
                  </div>
                  <div class="task-meta-row">
                    <span class="task-deadline">
                      截止：{{ formatDateTime(hw.deadline) }}
                    </span>
                    <span class="task-sub-info">
                      提交 {{ hw.submission_count || 0 }} / {{ hw.total_students || 0 }}
                    </span>
                  </div>
                </div>
                <div class="task-side" @click.stop>
                  <div class="task-tags">
                    <el-tag
                      type="success"
                      effect="plain"
                      size="small"
                    >
                      批改 {{ hw.graded_count || 0 }} / {{ hw.total_students || 0 }}
                    </el-tag>
                    <el-tag
                      :type="hw.grades_published ? 'success' : 'info'"
                      effect="plain"
                      size="small"
                    >
                      {{ hw.grades_published ? '成绩已发布' : '成绩未发布' }}
                    </el-tag>
                  </div>
                  <div class="task-actions">
                    <el-button
                      type="primary" 
                      text 
                      size="small" 
                      @click="goToGrading(hw)"
                    >
                      {{ hw.grades_published ? '去查看' : '去批改' }}
                    </el-button>
                    <el-tooltip
                      v-if="userStore.user?.role === 'teacher'"
                      :content="getPublishGradesTooltip(hw)"
                      placement="top"
                      :disabled="canPublishGrades(hw)"
                    >
                      <el-button
                      type="success"
                      text
                      size="small"
                      :disabled="!canPublishGrades(hw)"
                      @click="handlePublishGrades(hw)"
                    >
                      发布成绩
                    </el-button>
                    </el-tooltip>
                    <el-button
                      v-if="userStore.user?.role === 'teacher'"
                      type="warning"
                      text
                      size="small"
                      @click="handleEditHomework(hw)"
                    >
                      编辑
                    </el-button>
                    <el-button
                      v-if="userStore.user?.role === 'teacher'"
                      type="danger"
                      text
                      size="small"
                      @click="handleDeleteHomework(hw)"
                    >
                      删除
                    </el-button>
                  </div>
                </div>
              </div>
            </transition-group>
          </div>
          <el-empty v-else description="暂无作业，点击右上角发布新作业" :image-size="100" />
        </section>
      </template>
    </div>

  <!-- 导出成绩单设置对话框 -->
  <el-dialog
    v-model="exportDialogVisible"
    title="导出成绩单设置"
    width="600px"
  >
    <el-form label-width="80px">
      <!-- 作业选择 -->
      <el-form-item label="作业范围">
        <div class="export-section">
          <el-checkbox
            v-model="exportHomeworkCheckAll"
            :indeterminate="exportHomeworkIndeterminate"
            @change="handleExportHomeworkCheckAll"
          >
            全选作业
          </el-checkbox>
          <el-checkbox-group
            v-model="exportSelectedHomeworkIds"
            @change="handleExportHomeworkChange"
            class="export-checkbox-group"
          >
            <el-checkbox
              v-for="hw in homeworks"
              :key="hw.id"
              :label="hw.id"
            >
              作业{{ hw.course_hw_no }}：{{ hw.title }}
            </el-checkbox>
          </el-checkbox-group>
        </div>
      </el-form-item>

      <!-- 学生选择 -->
      <el-form-item label="学生范围">
        <div class="export-section">
          <el-input
            v-model="exportStudentSearchQuery"
            placeholder="搜索学号或姓名..."
            clearable
            size="small"
            class="export-student-search"
          />
          <el-checkbox
            v-model="exportStudentCheckAll"
            :indeterminate="exportStudentIndeterminate"
            @change="handleExportStudentCheckAll"
          >
            全选当前结果
          </el-checkbox>
          <el-scrollbar
            max-height="240px"
            class="export-student-list"
            ref="exportStudentListRef"
          >
            <div
              class="export-student-list-inner"
              @mousedown.left.prevent="onStudentListMouseDown"
              @mousemove.prevent="onStudentListMouseMove"
              @mouseup="onStudentListMouseUp"
              @mouseleave="onStudentListMouseUp"
            >
              <el-checkbox-group
                v-model="exportSelectedStudentIds"
                @change="handleExportStudentChange"
                class="export-checkbox-group"
              >
                <el-checkbox
                  v-for="stu in filteredCourseStudents"
                  :key="stu.id"
                  :label="stu.id"
                  :data-student-id="stu.id"
                >
                  {{ stu.student_no }} {{ stu.name }}
                </el-checkbox>
              </el-checkbox-group>
              <!-- 框选矩形 -->
              <div
                v-if="isDragSelectingStudents"
                class="export-selection-rect"
                :style="studentSelectionRectStyle"
              />
            </div>
          </el-scrollbar>
          <div v-if="loadingStudents" class="export-loading-tip">
            正在加载学生列表...
          </div>
        </div>
      </el-form-item>

      <el-form-item>
        <el-alert
          type="info"
          :closable="false"
          show-icon
          title="导出说明"
        >
          <template #default>
            <p>1. 可以勾选需要导出的作业（第几次或某几次作业）。</p>
            <p>2. 可以勾选需要导出的学生（如某几个人）。</p>
            <p>3. 对于未提交或未批改的作业，成绩栏将显示 “--”。</p>
          </template>
        </el-alert>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="exportDialogVisible = false">取 消</el-button>
      <el-button type="primary" :loading="exporting" @click="confirmExportGrades">
        确认导出
      </el-button>
    </template>
  </el-dialog>

    <!-- 添加助教对话框 -->
    <el-dialog v-model="showAddTADialog" title="添加助教" width="400px">
      <el-form :model="addTAForm" :rules="addTARules" ref="addTAFormRef" label-width="100px">
        <el-form-item label="学生学号" prop="student_no">
          <el-input
            v-model="addTAForm.student_no"
            placeholder="请输入学生学号（助教从学生中选择）"
            @keyup.enter="handleAddTA"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddTADialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddTA" :loading="addingTA">添加</el-button>
      </template>
    </el-dialog>

    <!-- 发布/编辑作业对话框 -->
    <el-dialog 
      v-model="showCreateHomeworkDialog" 
      :title="editingHomework ? '编辑作业' : '发布新作业'" 
      width="600px"
      @close="handleDialogClose"
    >
      <el-form :model="homeworkForm" :rules="homeworkRules" ref="homeworkFormRef" label-width="100px">
        <el-form-item label="作业标题" prop="title">
          <el-input
            v-model="homeworkForm.title"
            placeholder="请输入作业标题"
            @keyup.enter="handleCreateHomework"
          />
        </el-form-item>
        <el-form-item label="作业描述" prop="content">
          <el-input
            v-model="homeworkForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入作业详细说明..."
            @keydown.enter.ctrl="handleCreateHomework"
          />
        </el-form-item>
        <el-form-item label="参考文件">
          <el-upload
            v-model:file-list="homeworkImageList"
            :auto-upload="false"
            :before-upload="beforeUpload"
            :on-remove="handleImageRemove"
            :on-preview="handlePreview"
            list-type="picture-card"
            :limit="5"
            accept="image/*,application/pdf"
          >
            <el-icon><Plus /></el-icon>
            <template #file="{ file }">
              <div class="upload-file-item" :class="{ 'is-pdf': isPDF(file) }">
                <img
                  v-if="!isPDF(file) && file.url"
                  :src="file.url"
                  class="upload-file-thumbnail"
                  @click="handlePreview(file)"
                />
                <div v-else-if="isPDF(file)" class="upload-file-pdf-icon" @click="handlePreview(file)">
                  <el-icon :size="40"><Document /></el-icon>
                  <span class="upload-file-pdf-text">PDF</span>
                </div>
                <div v-else class="upload-file-placeholder">
                  <el-icon :size="40"><Picture /></el-icon>
                </div>
                <div class="upload-file-actions">
                  <el-icon class="upload-file-preview" @click="handlePreview(file)"><ZoomIn /></el-icon>
                  <el-icon class="upload-file-delete" @click="handleImageRemove(file)"><Delete /></el-icon>
                </div>
                <div class="upload-file-name">{{ file.name }}</div>
              </div>
            </template>
          </el-upload>
          <div class="upload-tip">支持上传参考图片和PDF文件，最多5个（将在创建作业时一并上传）</div>
        </el-form-item>
        <el-form-item label="截止时间" prop="deadline">
          <el-date-picker
            v-model="homeworkForm.deadline"
            type="datetime"
            placeholder="选择截止时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 100%"
            @keyup.enter="handleCreateHomework"
          />
        </el-form-item>
        <el-form-item label="分数上限" prop="max_score">
          <el-input-number
            v-model="homeworkForm.max_score"
            :min="1"
            :max="1000"
            :precision="0"
            placeholder="请输入分数上限（默认100分）"
            style="width: 100%"
            @keyup.enter="handleCreateHomework"
          />
          <div class="form-tip">本次作业的最高分数，批改时不能超过此上限</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="handleCancelHomeworkDialog">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleSubmitHomework" 
          :loading="creatingHomework"
        >
          {{ editingHomework ? '保存' : '发布' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 图片预览器 -->
    <el-image-viewer
      v-if="showImageViewer"
      :url-list="imageViewerUrlList"
      :initial-index="imageViewerInitialIndex"
      @close="showImageViewer = false"
      teleported
      z-index="3000"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { ElImageViewer } from 'element-plus';
import { ArrowLeft, Plus, DocumentCopy, UserFilled, Download, Search, Timer, CircleCheck, Trophy, Document, Picture, ZoomIn, Delete } from '@element-plus/icons-vue';
import { useUserStore } from '@/store/user';
import { 
  fetchCourseHomeworks, 
  createHomework,
  updateHomework,
  uploadHomeworkImage,
  fetchTeacherCourses,
  deleteHomework,
  addTAToCourse,
  exportCourseGrades,
  fetchCourseStudents,
  publishHomeworkGrades,
  fetchCourseTAs,
  fetchCourseTeachers,
} from '@/api/teacher';
import { getImageUrl, parseImageUrls } from '@/utils/image';
import { formatDateTime as formatDateUtil } from '@/utils/date-formatter';
import { logger } from '@/utils/logger';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const loading = ref(false);
const courseInfo = ref(null);
const homeworks = ref([]);
const showCreateHomeworkDialog = ref(false);
const creatingHomework = ref(false);
const exporting = ref(false);
const homeworkImageList = ref([]);
const homeworkImageUrls = ref([]);
const editingHomework = ref(null); // 当前正在编辑的作业ID
const originalDeadline = ref(null); // 保存编辑时的原始截止时间
const showAddTADialog = ref(false);
const addingTA = ref(false);
const addTAForm = ref({
  student_no: '',
});
const addTAFormRef = ref(null);
const addTARules = {
  student_no: [{ required: true, message: '请输入学生学号', trigger: 'blur' }],
};

// 成绩导出相关
const exportDialogVisible = ref(false);
const courseStudents = ref([]);
const loadingStudents = ref(false);
const exportStudentSearchQuery = ref('');
const exportStudentListRef = ref(null);
const exportSelectedHomeworkIds = ref([]);
const exportSelectedStudentIds = ref([]);
const exportHomeworkCheckAll = ref(true);
const exportHomeworkIndeterminate = ref(false);
const exportStudentCheckAll = ref(true);
const exportStudentIndeterminate = ref(false);
const isDragSelectingStudents = ref(false);
const dragStartPoint = ref({ x: 0, y: 0 });
const dragCurrentPoint = ref({ x: 0, y: 0 });

const courseId = computed(() => parseInt(route.params.id));
const homeworkSearch = ref('');
const taList = ref([]);
const loadingTAs = ref(false);
const teacherList = ref([]);
const loadingTeachers = ref(false);

const filteredHomeworks = computed(() => {
  if (!homeworkSearch.value.trim()) return homeworks.value;
  const q = homeworkSearch.value.trim().toLowerCase();
  return homeworks.value.filter(hw => hw.title?.toLowerCase().includes(q));
});

const publishedHomeworkCount = computed(() => {
  return homeworks.value.filter(hw => hw.grades_published).length;
});

// 导出对话框中，按搜索过滤后的学生列表
const filteredCourseStudents = computed(() => {
  if (!exportStudentSearchQuery.value.trim()) {
    return courseStudents.value;
  }
  const q = exportStudentSearchQuery.value.trim().toLowerCase();
  return courseStudents.value.filter(stu => {
    return (
      stu.student_no?.toLowerCase().includes(q) ||
      stu.name?.toLowerCase().includes(q)
    );
  });
});

// 学生框选选中区域样式
const studentSelectionRectStyle = computed(() => {
  if (!isDragSelectingStudents.value) return {};
  const x1 = Math.min(dragStartPoint.value.x, dragCurrentPoint.value.x);
  const y1 = Math.min(dragStartPoint.value.y, dragCurrentPoint.value.y);
  const width = Math.abs(dragCurrentPoint.value.x - dragStartPoint.value.x);
  const height = Math.abs(dragCurrentPoint.value.y - dragStartPoint.value.y);
  return {
    left: `${x1}px`,
    top: `${y1}px`,
    width: `${width}px`,
    height: `${height}px`,
  };
});

// 上传接口
const uploadAction = computed(() => {
  const hwId = editingHomework.value || 0;
  return `/api/teachers/me/courses/${courseId.value}/homeworks/${hwId}/upload-image`;
});

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token');
  return {
    Authorization: `Bearer ${token}`,
  };
});

const homeworkForm = ref({
  title: '',
  content: '',
  deadline: '',
  max_score: 100,  // 默认100分
});

const homeworkFormRef = ref(null);

// 动态生成验证规则：编辑模式下不验证时间约束
const homeworkRules = computed(() => {
  const baseRules = {
    title: [{ required: true, message: '请输入作业标题', trigger: 'blur' }],
    content: [{ required: true, message: '请输入作业描述', trigger: 'blur' }],
    deadline: [
      { required: true, message: '请选择截止时间', trigger: 'change' },
    ],
  };
  
  // 只有在创建模式下才验证时间约束（不能早于当前时间+30分钟）
  if (!editingHomework.value) {
    baseRules.deadline.push({
      validator: (_rule, value, callback) => {
        if (!value) {
          callback();
          return;
        }
        const selectedTime = new Date(value);
        const now = new Date();
        const minTime = new Date(now.getTime() + 30 * 60 * 1000); // 当前时间+30分钟
        
        if (selectedTime.getTime() < minTime.getTime()) {
          callback(new Error('截止时间不能早于当前时间+30分钟'));
        } else {
          callback();
        }
      },
      trigger: 'change',
    });
  }
  
  return baseRules;
});

// 加载课程学生列表（用于导出成绩单筛选）
const loadCourseStudents = async () => {
  if (courseStudents.value.length > 0) return;
  loadingStudents.value = true;
  try {
    const res = await fetchCourseStudents(courseId.value);
    courseStudents.value = res.data?.student_list || [];
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else if (status === 403) {
      ElMessage.error('无权查看该课程学生列表');
    } else {
      ElMessage.error(error?.response?.data?.error || '获取学生列表失败');
    }
  } finally {
    loadingStudents.value = false;
  }
};

// 返回上一页
const goBack = () => {
  // 使用 router.back() 返回到上一个页面
  // 如果浏览器历史记录中没有上一个页面，则返回到主页
  if (window.history.length > 1) {
    router.back();
  } else {
  router.push({ name: 'TeacherHome' });
  }
};

// 格式化日期时间
const formatDateTime = (dateString) => {
  return formatDateUtil(dateString, 'YYYY-MM-DD HH:mm');
};

// 发布某次作业的成绩（老师全部批改完成后手动提交）
const handlePublishGrades = async (homework) => {
  // 如果已发布，提示已发布
  if (homework.grades_published) {
    ElMessage.info('本次作业成绩已发布，学生可以查看自己的得分和批改情况');
    return;
  }

  // 检查是否可以发布
  const total = homework.total_students || 0;
  const graded = homework.graded_count || 0;
  
  if (total === 0) {
    ElMessage.warning('该课程暂无学生，无法发布成绩');
    return;
  }

  if (graded < total) {
    const ungraded = total - graded;
    ElMessage.warning(`还有 ${ungraded} 名学生未批改（已批改 ${graded} / 共 ${total}），请完成所有学生的批改后再发布成绩`);
    return;
  }

  // 检查是否已过ddl
  const deadline = homework.deadline ? new Date(homework.deadline) : null;
  const now = new Date();
  if (deadline && now < deadline) {
    ElMessage.warning('作业截止时间未到，建议在截止时间后再发布成绩');
    // 仍然允许发布，只是提示
  }

  try {
    await ElMessageBox.confirm(
      '确认发布本次作业的所有成绩吗？发布后学生将可以查看自己的得分和批改情况，且无法一键撤回。',
      '发布成绩',
      {
        type: 'warning',
        confirmButtonText: '确认发布',
        cancelButtonText: '取消',
      },
    );
  } catch {
    return;
  }

  try {
    await publishHomeworkGrades(courseId.value, homework.id);
    // 先刷新页面数据，再给出成功提示，避免前后信息不一致
    await fetchData();
    ElMessage.success('成绩发布成功，学生现在可以查看本次作业成绩');
  } catch (error) {
    logger.error('发布成绩失败:', error);
    const errorMsg = error.response?.data?.error || '发布成绩失败，请稍后重试';
    // 如果后端返回了详细错误信息，显示详细错误信息
    ElMessage.error(errorMsg);
  }
};

// 计算提交百分比
const getSubmissionPercentage = (homework) => {
  if (!homework.total_students || homework.total_students === 0) return 0;
  return Math.round((homework.submission_count || 0) / homework.total_students * 100);
};

// 获取进度条颜色
const getProgressColor = (homework) => {
  const percentage = getSubmissionPercentage(homework);
  if (percentage >= 80) return '#67c23a';
  if (percentage >= 50) return '#e6a23c';
  return '#f56c6c';
};

// 批改进度百分比
const getGradingPercentage = (homework) => {
  if (!homework.total_students || homework.total_students === 0) return 0;
  return Math.round((homework.graded_count || 0) / homework.total_students * 100);
};

// 批改进度条颜色
const getGradingProgressColor = (homework) => {
  const percentage = getGradingPercentage(homework);
  if (percentage >= 80) return '#67c23a';
  if (percentage >= 50) return '#e6a23c';
  return '#909399'; // 批改使用略微不同的颜色
};

// 是否可以发布成绩：所有学生都已批改且当前未发布
const canPublishGrades = (homework) => {
  const total = homework.total_students || 0;
  const graded = homework.graded_count || 0;
  return total > 0 && graded >= total && !homework.grades_published;
};

// 获取发布成绩按钮的提示文字
const getPublishGradesTooltip = (homework) => {
  // 如果已发布，提示已发布
  if (homework.grades_published) {
    return '成绩已发布，无法更改';
  }
  
  const total = homework.total_students || 0;
  const graded = homework.graded_count || 0;
  
  // 如果没有学生
  if (total === 0) {
    return '该课程暂无学生，无法发布成绩';
  }
  
  // 如果还有学生未批改
  if (graded < total) {
    const ungraded = total - graded;
    return `还有 ${ungraded} 名学生未批改（已批改 ${graded} / 共 ${total}），请完成所有学生的批改后再发布成绩`;
  }
  
  // 其他情况（理论上不应该到这里，因为canPublishGrades已经检查过了）
  return '可以发布成绩';
};

// 跳转到批改中心
const goToGrading = (homework) => {
  router.push({ 
    name: 'GradingView', 
    params: { 
      courseId: courseId.value,
      homeworkId: homework.id 
    } 
  });
};

// 复制课程号
const copyCourseCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code);
    ElMessage.success(`课程号 ${code} 已复制到剪贴板`);
  } catch (error) {
    // 降级方案
    const textArea = document.createElement('textarea');
    textArea.value = code;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      ElMessage.success(`课程号 ${code} 已复制到剪贴板`);
    } catch (err) {
      ElMessage.error('复制失败，请手动复制');
    }
    document.body.removeChild(textArea);
  }
};

// 编辑作业
const handleEditHomework = (homework) => {
  editingHomework.value = homework.id;
  
  // 处理截止时间格式（与创建时保持一致：YYYY-MM-DDTHH:mm:ss）
  let deadlineStr = '';
  if (homework.deadline) {
    const deadline = new Date(homework.deadline);
    // 格式化为 YYYY-MM-DDTHH:mm:ss 格式（与 value-format 一致）
    const year = deadline.getFullYear();
    const month = String(deadline.getMonth() + 1).padStart(2, '0');
    const day = String(deadline.getDate()).padStart(2, '0');
    const hours = String(deadline.getHours()).padStart(2, '0');
    const minutes = String(deadline.getMinutes()).padStart(2, '0');
    const seconds = String(deadline.getSeconds()).padStart(2, '0');
    deadlineStr = `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
    
    // 保存原始截止时间（用于后续比较，判断是否修改了截止时间）
    originalDeadline.value = deadlineStr;
  } else {
    originalDeadline.value = null;
  }
  
  homeworkForm.value = {
    title: homework.title,
    content: homework.content || '',
    deadline: deadlineStr,
    max_score: homework.max_score || 100,
  };
  
  // 处理图片URLs
  let imageUrls = homework.image_urls;
  if (typeof imageUrls === 'string') {
    try {
      imageUrls = JSON.parse(imageUrls);
    } catch (e) {
      imageUrls = parseImageUrls(imageUrls);
    }
  }
  if (!Array.isArray(imageUrls)) {
    imageUrls = [];
  }
  
  homeworkImageUrls.value = imageUrls.map(img => {
    if (typeof img === 'string') return img;
    if (typeof img === 'object' && img !== null) {
      return img.image_url || img.url || String(img);
    }
    return String(img);
  });
  
  // 设置图片列表用于显示
  homeworkImageList.value = homeworkImageUrls.value.map((url, index) => {
    // 使用带 token 的完整 URL，因为图片可能需要认证
    const fullUrl = getImageUrl(url, true);
    const urlStr = String(url);
    
    // 从URL中提取文件名，如果没有则使用默认名称
    let fileName = `file-${index}`;
    if (urlStr.includes('/')) {
      const parts = urlStr.split('/');
      const lastPart = parts[parts.length - 1];
      // 提取文件名（去掉可能的查询参数）
      if (lastPart && lastPart.includes('.')) {
        fileName = lastPart.split('?')[0]; // 去掉查询参数
      }
    }
    // 判断文件类型
    const isPDFFile = fileName.toLowerCase().endsWith('.pdf') || urlStr.toLowerCase().includes('.pdf');
    // 使用唯一标识符作为 uid（使用时间戳 + 索引 + URL 哈希）
    const uniqueId = `existing-${Date.now()}-${index}-${urlStr.substring(0, 20).replace(/[^a-zA-Z0-9]/g, '')}`;
    
    return {
      uid: uniqueId,
      name: fileName,
      url: fullUrl, // 使用完整URL，包含token，用于显示
    status: 'success',
      // 添加文件类型信息，用于预览
      type: isPDFFile ? 'application/pdf' : 'image',
      // 保存原始URL，用于后续更新和删除
      originalUrl: url,
    };
  });
  
  showCreateHomeworkDialog.value = true;
};

// 对话框关闭时的处理（无论是通过取消按钮、ESC键还是点击外部关闭）
const handleDialogClose = () => {
  // 如果正在保存中（creatingHomework为true），不重置状态，等待保存完成
  // 这样可以避免在保存过程中意外重置 editingHomework，导致调用错误的函数
  if (creatingHomework.value) {
    return;
  }
  
  editingHomework.value = null;
  originalDeadline.value = null; // 重置原始截止时间
  homeworkForm.value = {
    title: '',
    content: '',
    deadline: '',
    max_score: 100,  // 重置为默认值
  };
  homeworkImageList.value = [];
  homeworkImageUrls.value = [];
  // 重置表单验证状态
  if (homeworkFormRef.value) {
    homeworkFormRef.value.resetFields();
  }
  creatingHomework.value = false; // 确保加载状态也重置
};

// 取消作业对话框
const handleCancelHomeworkDialog = () => {
  showCreateHomeworkDialog.value = false;
  // 重置状态会在 handleDialogClose 中处理（通过 @close 事件）
};

// 统一处理提交（创建或更新）
const handleSubmitHomework = () => {
  // 根据 editingHomework 的值决定是创建还是更新
  // 在函数调用时立即检查，避免在异步操作过程中 editingHomework 被重置
  if (editingHomework.value) {
    handleUpdateHomework();
  } else {
    handleCreateHomework();
  }
};

// 更新作业
const handleUpdateHomework = async () => {
  if (!homeworkFormRef.value) return;
  
  // 检查是否在编辑模式
  if (!editingHomework.value) {
    ElMessage.error('未选择要编辑的作业');
    return;
  }
  
  try {
    await homeworkFormRef.value.validate();
    
    if (!homeworkForm.value.deadline) {
      ElMessage.warning('请选择截止时间');
      return;
    }
    
    // 检查截止时间是否早于当前时间，如果是则提示用户确认
    const currentDeadline = homeworkForm.value.deadline;
    const isDeadlineChanged = currentDeadline !== originalDeadline.value;
    
    if (isDeadlineChanged) {
      const selectedTime = new Date(currentDeadline);
      const now = new Date();
      
      // 如果选择的截止时间早于当前时间，需要用户确认
      if (selectedTime.getTime() < now.getTime()) {
        try {
          await ElMessageBox.confirm(
            `您设置的截止时间（${currentDeadline}）早于当前时间，确定要继续修改吗？`,
            '确认修改截止时间',
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              type: 'warning',
            }
          );
          // 用户确认后继续执行
        } catch {
          // 用户取消，不执行更新
          return;
        }
      }
    }

    creatingHomework.value = true;
    
    const homeworkId = editingHomework.value;
    
    // 再次确认 homeworkId 有效
    if (!homeworkId) {
      ElMessage.error('作业ID无效，无法更新');
      creatingHomework.value = false;
      return;
    }
    
    console.log('老师端：开始更新作业', {
      courseId: courseId.value,
      homeworkId: homeworkId,
      editingHomework: editingHomework.value,
      formData: {
        title: homeworkForm.value.title,
        content: homeworkForm.value.content,
        deadline: homeworkForm.value.deadline,
        max_score: homeworkForm.value.max_score
      }
    });
    
    // 先更新作业的基本信息（不包含图片URLs）
    await updateHomework(courseId.value, homeworkId, {
      title: homeworkForm.value.title,
      content: homeworkForm.value.content,
      deadline: homeworkForm.value.deadline,
      max_score: homeworkForm.value.max_score,
    });
    
    // 检查是否有新上传的文件需要处理
    const newFiles = homeworkImageList.value.filter(file => file.raw);
    const existingUrls = homeworkImageUrls.value || [];
    
    if (newFiles.length > 0) {
      console.log('老师端：更新作业时发现新文件，开始上传', {
        homeworkId: homeworkId,
        newFileCount: newFiles.length,
        existingUrlCount: existingUrls.length
      });
      
      const uploadedUrls = [];
      for (let i = 0; i < newFiles.length; i++) {
        const fileItem = newFiles[i];
        try {
          console.log(`老师端：正在上传第 ${i + 1}/${newFiles.length} 个新文件`, {
            fileName: fileItem.name,
            fileSize: fileItem.size,
            fileType: fileItem.type,
            hasRaw: !!fileItem.raw
          });
          
          const formData = new FormData();
          formData.append('file', fileItem.raw);
          
          const uploadResponse = await uploadHomeworkImage(courseId.value, homeworkId, formData);
          console.log('老师端：上传响应', uploadResponse.data);
          
          // 处理响应，支持多种格式
          let uploadedUrl = null;
          if (uploadResponse.data?.image_urls && Array.isArray(uploadResponse.data.image_urls)) {
            uploadedUrl = uploadResponse.data.image_urls[0];
          } else if (uploadResponse.data?.image_url) {
            uploadedUrl = uploadResponse.data.image_url;
          } else if (uploadResponse.data?.url) {
            uploadedUrl = uploadResponse.data.url;
          }
          
          if (uploadedUrl) {
            uploadedUrls.push(uploadedUrl);
            console.log(`老师端：文件 ${fileItem.name} 上传成功，URL:`, uploadedUrl);
          } else {
            console.warn(`老师端：文件 ${fileItem.name} 上传成功但未返回URL`, uploadResponse.data);
            ElMessage.warning(`文件 ${fileItem.name} 上传成功但未返回URL，请刷新页面检查`);
          }
        } catch (error) {
          console.error(`老师端：文件 ${fileItem.name} 上传失败`, {
            error: error,
            errorMessage: error?.message,
            errorResponse: error?.response?.data,
            errorStatus: error?.response?.status,
          });
          logger.error('图片上传失败:', error);
          ElMessage.warning(`文件 ${fileItem.name} 上传失败，将跳过该文件`);
        }
      }
      
      // 合并现有的URLs和新上传的URLs
      const allImageUrls = [...existingUrls, ...uploadedUrls];
      
      // 更新作业的 image_urls
      if (uploadedUrls.length > 0) {
        try {
          console.log('老师端：准备更新作业的参考文件', {
            courseId: courseId.value,
            homeworkId: homeworkId,
            allImageUrls: allImageUrls,
            uploadedUrls: uploadedUrls,
            existingUrls: existingUrls
          });
          
          await updateHomework(courseId.value, homeworkId, {
            image_urls: allImageUrls,
          });
          
          console.log('老师端：更新作业成功，image_urls 已保存');
          // 更新本地状态
          homeworkImageUrls.value = allImageUrls;
        } catch (error) {
          console.error('老师端：更新作业的参考文件失败', {
            error: error,
            errorMessage: error?.message,
            errorResponse: error?.response?.data,
            errorStatus: error?.response?.status,
          });
          logger.error('更新作业的参考文件失败:', error);
          ElMessage.warning('作业基本信息已更新，但参考文件更新失败，请稍后重试');
        }
      } else if (newFiles.length > 0) {
        // 所有新文件都上传失败了
        ElMessage.warning('所有新文件上传失败，作业基本信息已更新，但参考文件未更新');
      }
    } else {
      // 没有新文件，但可能需要更新现有的 image_urls（如果用户删除了某些文件）
      // homeworkImageUrls.value 应该已经反映了用户的选择（通过 handleImageRemove）
      if (homeworkImageUrls.value && homeworkImageUrls.value.length >= 0) {
        try {
          await updateHomework(courseId.value, homeworkId, {
      image_urls: homeworkImageUrls.value,
    });
          console.log('老师端：更新作业的参考文件列表成功');
        } catch (error) {
          console.error('老师端：更新作业的参考文件列表失败', error);
          logger.error('更新作业的参考文件列表失败:', error);
          // 不显示错误，因为基本信息已经更新成功
        }
      }
    }
    
    ElMessage.success('作业更新成功');
    
    // 先重置状态，再关闭对话框（避免在关闭时触发 handleDialogClose 导致状态混乱）
    editingHomework.value = null;
    originalDeadline.value = null; // 重置原始截止时间
    homeworkForm.value = {
      title: '',
      content: '',
      deadline: '',
      max_score: 100,
    };
    homeworkImageList.value = [];
    homeworkImageUrls.value = [];
    if (homeworkFormRef.value) {
      homeworkFormRef.value.resetFields();
    }
    
    showCreateHomeworkDialog.value = false;
    creatingHomework.value = false;
    await fetchData();
  } catch (error) {
    const status = error?.response?.status;
    if (status === 400) {
      ElMessage.error(error?.response?.data?.error || '更新失败，请检查输入');
    } else if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else {
      ElMessage.error(error?.response?.data?.error || '更新失败，请重试');
    }
    logger.error('更新作业失败:', error);
  } finally {
    creatingHomework.value = false;
  }
};

// 删除作业（仅教师）
const handleDeleteHomework = async (homework) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除作业"${homework.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    await deleteHomework(courseId.value, homework.id);
    ElMessage.success('删除成功');
    await fetchData();
  } catch (error) {
    if (error !== 'cancel') {
      const status = error?.response?.status;
      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录');
        userStore.logout();
        router.push({ name: 'Login' });
      } else {
        ElMessage.error(error?.response?.data?.error || '删除失败，请重试');
      }
    }
  }
};

// 添加助教
const handleAddTA = async () => {
  if (!addTAFormRef.value) return;
  try {
    await addTAFormRef.value.validate();
    addingTA.value = true;
    
    await addTAToCourse(courseId.value, {
      student_no: addTAForm.value.student_no,
    });
    
    ElMessage.success('助教添加成功');
    showAddTADialog.value = false;
    addTAForm.value = {
      student_no: '',
    };
    // 刷新助教列表
    await fetchTAs();
  } catch (error) {
    const status = error?.response?.status;
    if (status === 400) {
      ElMessage.error(error?.response?.data?.error || '添加失败，请检查学号');
    } else if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else if (status === 403) {
      ElMessage.error('只有教师可以添加助教');
    } else {
      ElMessage.error(error?.response?.data?.error || '添加失败，请重试');
    }
  } finally {
    addingTA.value = false;
  }
};

// 判断文件是否为PDF
const isPDF = (file) => {
  if (!file) return false;
  const fileName = file.name || '';
  const fileType = file.type || '';
  return fileType === 'application/pdf' || fileName.toLowerCase().endsWith('.pdf');
};

// 判断文件是否为图片
const isImage = (file) => {
  if (!file) return false;
  const fileName = file.name || '';
  const fileType = file.type || '';
  // 检查文件类型
  if (fileType.startsWith('image/')) return true;
  // 检查文件扩展名
  const lowerFileName = fileName.toLowerCase();
  return lowerFileName.endsWith('.jpg') || lowerFileName.endsWith('.jpeg') || 
         lowerFileName.endsWith('.png') || lowerFileName.endsWith('.gif') || 
         lowerFileName.endsWith('.webp') || lowerFileName.endsWith('.bmp');
};

// 禁用早于当前时间+30分钟的日期
const disabledDate = (time) => {
  const now = new Date();
  const minTime = new Date(now.getTime() + 30 * 60 * 1000); // 当前时间+30分钟
  return time.getTime() < minTime.getTime();
};

// 禁用早于当前时间+30分钟的时间
const disabledTime = (date) => {
  const now = new Date();
  const minTime = new Date(now.getTime() + 30 * 60 * 1000); // 当前时间+30分钟
  
  // 如果选择的日期是今天，需要限制时间
  const selectedDate = new Date(date);
  const today = new Date();
  const isToday = selectedDate.toDateString() === today.toDateString();
  
  if (isToday) {
    const minHour = minTime.getHours();
    const minMinute = minTime.getMinutes();
    
    return {
      disabledHours: () => {
        const hours = [];
        for (let i = 0; i < minHour; i++) {
          hours.push(i);
        }
        return hours;
      },
      disabledMinutes: (selectedHour) => {
        if (selectedHour === minHour) {
          const minutes = [];
          for (let i = 0; i < minMinute; i++) {
            minutes.push(i);
          }
          return minutes;
        }
        return [];
      },
      disabledSeconds: () => [],
    };
  }
  
  return {
    disabledHours: () => [],
    disabledMinutes: () => [],
    disabledSeconds: () => [],
  };
};

// 上传前验证
const beforeUpload = (file) => {
  const isImageFile = isImage(file);
  const isPDFFile = isPDF(file);
  const isLt10M = file.size / 1024 / 1024 < 10;

  if (!isImageFile && !isPDFFile) {
    ElMessage.error('只能上传图片或PDF文件！');
    return false;
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB！');
    return false;
  }
  return true;
};

// 删除图片
const handleImageRemove = (file) => {
  // 从文件列表中移除
  const index = homeworkImageList.value.findIndex(item => item.uid === file.uid);
  if (index > -1) {
    homeworkImageList.value.splice(index, 1);
  }
  
  // 如果文件有 originalUrl（已上传的文件），也需要从 homeworkImageUrls 中移除
  // 优先使用 originalUrl，如果没有则尝试从 url 中提取
  let urlToRemove = file.originalUrl || null;
  
  if (!urlToRemove && file.url) {
    // 提取相对路径（从完整URL中提取 uploads/... 部分）
    try {
      // 尝试从URL中提取相对路径
      const urlMatch = file.url.match(/uploads\/.+$/);
      if (urlMatch) {
        urlToRemove = urlMatch[0];
      } else {
        // 如果匹配不到，尝试从URL路径中提取
        const urlObj = new URL(file.url);
        const pathname = urlObj.pathname;
        const uploadsIndex = pathname.indexOf('/uploads/');
        if (uploadsIndex !== -1) {
          urlToRemove = pathname.substring(uploadsIndex + 1); // 去掉开头的 '/'
        } else {
          // 如果还是找不到，直接使用URL作为标识
          urlToRemove = file.url;
        }
      }
    } catch (e) {
      // URL解析失败，直接使用file.url
      urlToRemove = file.url;
    }
    
    if (urlToRemove) {
      // 从 homeworkImageUrls 中移除对应的URL
      const urlIndex = homeworkImageUrls.value.findIndex(url => {
        const urlStr = String(url);
        const removeStr = String(urlToRemove);
        // 精确匹配
        if (urlStr === removeStr) return true;
        // 检查是否包含相对路径部分
        if (urlStr.includes(removeStr) || removeStr.includes(urlStr)) return true;
        // 如果 urlToRemove 是相对路径，检查 imageUrls 中是否包含
        if (removeStr.startsWith('uploads/') && urlStr.includes(removeStr)) return true;
        return false;
      });
      
      if (urlIndex > -1) {
        homeworkImageUrls.value.splice(urlIndex, 1);
        console.log('老师端：已从参考文件URL列表中移除', urlToRemove);
      }
    }
  }
};

// 预览文件
const handlePreview = (file) => {
  // 获取文件 URL
  let fileUrl = file.url;
  
  // 如果是新上传的文件（还没有URL），创建本地预览URL
  if (!fileUrl && file.raw) {
    fileUrl = URL.createObjectURL(file.raw);
  }
  
  if (!fileUrl) {
    ElMessage.warning('无法预览该文件');
    return;
  }
  
  // 判断文件类型
  const fileName = file.name || '';
  const fileType = file.type || '';
  const isPDFFile = isPDF(file) || fileType === 'application/pdf' || fileName.toLowerCase().endsWith('.pdf');
  const isImageFile = isImage(file) || fileType.startsWith('image/');
  
  // PDF文件直接在新窗口打开
  if (isPDFFile) {
    // 如果是本地文件（blob URL），直接打开
    if (fileUrl.startsWith('blob:')) {
      window.open(fileUrl, '_blank');
    } else {
      // 对于已上传的文件，使用完整URL
      const fullUrl = fileUrl.startsWith('http') ? fileUrl : getImageUrl(fileUrl, true);
      window.open(fullUrl, '_blank');
    }
    return;
  }
  
  // 图片文件使用图片预览器
  if (isImageFile) {
    // 获取所有图片文件的URL列表
    const imageFiles = homeworkImageList.value.filter(f => {
      const fName = f.name || '';
      const fType = f.type || '';
      return isImage(f) || fType.startsWith('image/');
    });
    
    // 构建图片URL列表
    imageViewerUrlList.value = imageFiles.map(f => {
      let url = f.url;
      if (!url && f.raw) {
        url = URL.createObjectURL(f.raw);
      } else if (url && !url.startsWith('http') && !url.startsWith('blob:')) {
        // 对于已上传的文件，使用完整URL
        url = getImageUrl(url, true);
      }
      return url;
    }).filter(url => url); // 过滤掉无效的URL
    
    // 找到当前图片在列表中的索引
    const currentIndex = imageFiles.findIndex(f => {
      if (f.uid === file.uid) return true;
      const fUrl = f.url || (f.raw ? URL.createObjectURL(f.raw) : '');
      return fUrl === fileUrl;
    });
    
    imageViewerInitialIndex.value = currentIndex >= 0 ? currentIndex : 0;
    showImageViewer.value = true;
    return;
  }
  
  // 其他文件类型不支持预览
  ElMessage.warning('该文件类型不支持预览');
  
  // 创建全屏图片预览
  const viewer = document.createElement('div');
  viewer.className = 'file-preview-viewer';
  viewer.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.95);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  `;
  
  const img = document.createElement('img');
  img.src = fileUrl;
  img.style.cssText = `
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
  `;
  img.onerror = () => {
    ElMessage.error('图片加载失败');
    if (document.body.contains(viewer)) {
      document.body.removeChild(viewer);
    }
    if (fileUrl.startsWith('blob:')) {
      URL.revokeObjectURL(fileUrl);
    }
  };
  
  const closeBtn = document.createElement('button');
  closeBtn.innerHTML = '×';
  closeBtn.style.cssText = `
    position: absolute;
    top: 20px;
    right: 20px;
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 50%;
    color: white;
    font-size: 30px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.3s;
    z-index: 10000;
  `;
  closeBtn.onmouseover = () => {
    closeBtn.style.background = 'rgba(255, 255, 255, 0.4)';
  };
  closeBtn.onmouseout = () => {
    closeBtn.style.background = 'rgba(255, 255, 255, 0.2)';
  };
  
  const closeViewer = () => {
    if (document.body.contains(viewer)) {
      document.body.removeChild(viewer);
    }
    if (fileUrl.startsWith('blob:')) {
      URL.revokeObjectURL(fileUrl);
    }
  };
  
  const escapeHandler = (e) => {
    if (e.key === 'Escape') {
      closeViewer();
      document.removeEventListener('keydown', escapeHandler);
    }
  };
  document.addEventListener('keydown', escapeHandler);
  
  viewer.onclick = (e) => {
    if (e.target === viewer || e.target === img) {
      closeViewer();
    }
  };
  
  closeBtn.onclick = (e) => {
    e.stopPropagation();
    closeViewer();
  };
  
  viewer.appendChild(img);
  viewer.appendChild(closeBtn);
  document.body.appendChild(viewer);
};

// 上传图片文件（使用FormData）
const uploadImageFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file.raw || file);
  
  // 使用课程ID作为临时标识，上传到临时位置
  // 注意：这里需要一个临时上传接口，或者我们可以先创建作业（不包含图片），然后上传图片并更新
  // 为了简化，我们先将图片转换为base64，在创建作业时一起发送
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const base64 = e.target.result;
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file.raw || file);
  });
};

// 创建作业
const handleCreateHomework = async () => {
  if (!homeworkFormRef.value) return;
  try {
    await homeworkFormRef.value.validate();
    
    if (!homeworkForm.value.deadline) {
      ElMessage.warning('请选择截止时间');
      return;
    }
    
    // 验证截止时间不能早于当前时间+30分钟
    const selectedTime = new Date(homeworkForm.value.deadline);
    const now = new Date();
    const minTime = new Date(now.getTime() + 30 * 60 * 1000);
    if (selectedTime.getTime() < minTime.getTime()) {
      ElMessage.error('截止时间不能早于当前时间+30分钟');
      return;
    }

    creatingHomework.value = true;
    
    // 先刷新作业列表，确保获取最新的作业序号（避免重复）
    try {
      await fetchData();
    } catch (error) {
      console.warn('刷新作业列表失败，继续使用当前列表', error);
    }
    
    // 先创建作业（不包含图片），获取作业ID
    const maxHwNo = homeworks.value.length > 0 
      ? Math.max(...homeworks.value.map(h => h.course_hw_no || 0))
      : 0;
    
    console.log('老师端：准备创建作业', {
      courseId: courseId.value,
      maxHwNo: maxHwNo,
      newHwNo: maxHwNo + 1,
      homeworkCount: homeworks.value.length
    });
    
    const homeworkResponse = await createHomework(courseId.value, {
      title: homeworkForm.value.title,
      content: homeworkForm.value.content,
      deadline: homeworkForm.value.deadline,
      course_hw_no: maxHwNo + 1,
      max_score: homeworkForm.value.max_score || 100,
      image_urls: [], // 先创建作业，不包含图片
    });
    
    const homeworkId = homeworkResponse.data?.homework?.id;
    
    if (!homeworkId) {
      throw new Error('创建作业失败：未返回作业ID');
    }
    
    // 如果有图片，上传图片并更新作业
    if (homeworkId && homeworkImageList.value && homeworkImageList.value.length > 0) {
      console.log('老师端：开始上传参考文件', {
        homeworkId: homeworkId,
        fileCount: homeworkImageList.value.length,
        files: homeworkImageList.value.map(f => ({ name: f.name, size: f.size, type: f.type }))
      });
      
      const imageUrls = [];
      for (let i = 0; i < homeworkImageList.value.length; i++) {
        const fileItem = homeworkImageList.value[i];
        try {
          console.log(`老师端：正在上传第 ${i + 1}/${homeworkImageList.value.length} 个文件`, {
            fileName: fileItem.name,
            fileSize: fileItem.size,
            fileType: fileItem.type,
            hasRaw: !!fileItem.raw
          });
          
          const formData = new FormData();
          const fileToUpload = fileItem.raw || fileItem;
          formData.append('file', fileToUpload);
          
          console.log('老师端：发送上传请求', {
            courseId: courseId.value,
            homeworkId: homeworkId,
            fileName: fileItem.name
          });
          
          const uploadResponse = await uploadHomeworkImage(courseId.value, homeworkId, formData);
          console.log('老师端：上传响应', uploadResponse.data);
          
          const uploadedUrl = uploadResponse.data?.image_urls?.[0] || uploadResponse.data?.image_url;
          if (uploadedUrl) {
            imageUrls.push(uploadedUrl);
            console.log(`老师端：文件 ${fileItem.name} 上传成功，URL:`, uploadedUrl);
          } else {
            console.warn(`老师端：文件 ${fileItem.name} 上传成功但未返回URL`, uploadResponse.data);
          }
        } catch (error) {
          console.error(`老师端：文件 ${fileItem.name} 上传失败`, {
            error: error,
            errorMessage: error?.message,
            errorResponse: error?.response?.data,
            errorStatus: error?.response?.status,
            errorStatusText: error?.response?.statusText,
            fullError: JSON.stringify(error, Object.getOwnPropertyNames(error))
          });
          logger.error('图片上传失败:', error);
          ElMessage.warning(`图片 ${fileItem.name} 上传失败，将跳过该图片`);
        }
      }
      
      console.log('老师端：所有文件上传完成', {
        totalFiles: homeworkImageList.value.length,
        successCount: imageUrls.length,
        imageUrls: imageUrls
      });
      
      // 更新作业，添加图片URLs
      if (imageUrls.length > 0) {
        try {
          console.log('老师端：准备更新作业的参考文件', {
            courseId: courseId.value,
            homeworkId: homeworkId,
            imageUrls: imageUrls,
            imageUrlsLength: imageUrls.length,
            imageUrlsType: typeof imageUrls,
            imageUrlsIsArray: Array.isArray(imageUrls)
          });
          const updateData = {
            image_urls: imageUrls,
          };
          console.log('老师端：发送更新请求的数据', updateData);
          await updateHomework(courseId.value, homeworkId, updateData);
          console.log('老师端：更新作业成功，image_urls 已保存');
          // 更新本地状态，确保后续编辑时能正确显示
          homeworkImageUrls.value = imageUrls;
        } catch (error) {
          console.error('老师端：更新作业失败', {
            error: error,
            errorMessage: error?.message,
            errorResponse: error?.response?.data,
            errorStatus: error?.response?.status,
            errorStatusText: error?.response?.statusText,
            fullError: JSON.stringify(error, Object.getOwnPropertyNames(error))
          });
          logger.error('更新作业失败:', error);
          // 如果更新失败，尝试删除已创建的作业（回滚）
          try {
            console.log('老师端：尝试删除已创建的作业（回滚）', homeworkId);
            await deleteHomework(courseId.value, homeworkId);
            console.log('老师端：已删除作业，回滚成功');
          } catch (deleteError) {
            console.error('老师端：删除作业失败', deleteError);
            logger.error('删除作业失败:', deleteError);
          }
          throw error; // 重新抛出错误，让外层catch处理
        }
      } else {
        console.warn('老师端：没有参考文件需要更新，imageUrls 为空', imageUrls);
        if (homeworkImageList.value.length > 0) {
          // 如果用户上传了文件但都失败了，询问是否保留作业
          ElMessage.warning('所有参考文件上传失败，作业已创建但没有参考文件');
        }
      }
    }
    
    ElMessage.success('作业发布成功');
    showCreateHomeworkDialog.value = false;
    handleDialogClose();
    await fetchData();
  } catch (error) {
    console.error('老师端：创建作业失败', {
      error: error,
      errorMessage: error?.message,
      errorResponse: error?.response?.data,
      errorStatus: error?.response?.status,
      errorStatusText: error?.response?.statusText,
      errorConfig: error?.config,
      fullError: error
    });
    logger.error('创建作业失败:', error);
    
    const status = error?.response?.status;
    if (status === 400) {
      const errorMsg = error?.response?.data?.error || '发布失败，请检查输入';
      console.error('老师端：400错误详情', errorMsg);
      // 检查是否是作业序号重复的错误
      if (errorMsg.includes('作业序号') && errorMsg.includes('已存在')) {
        ElMessage.error('作业序号已存在，请刷新页面后重试');
        // 自动刷新作业列表
        await fetchData();
      } else {
        ElMessage.error(errorMsg);
      }
    } else if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else if (status === 403) {
      ElMessage.error('无权执行此操作');
    } else if (status === 500) {
      ElMessage.error('服务器错误，请稍后重试');
    } else {
      const errorMsg = error?.response?.data?.error || error?.message || '发布失败，请重试';
      console.error('老师端：其他错误', errorMsg);
      ElMessage.error(errorMsg);
    }
  } finally {
    creatingHomework.value = false;
  }
};

// 获取数据
// 获取助教列表
const fetchTAs = async () => {
  loadingTAs.value = true;
  try {
    const res = await fetchCourseTAs(courseId.value);
    taList.value = res.data?.ta_list || [];
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else if (status === 403) {
      // 无权查看助教列表，静默失败
      taList.value = [];
    } else {
      // 其他错误也静默失败，不影响主流程
      taList.value = [];
    }
  } finally {
    loadingTAs.value = false;
  }
};

// 获取教师列表（助教登录时显示）
const fetchTeachers = async () => {
  loadingTeachers.value = true;
  try {
    const res = await fetchCourseTeachers(courseId.value);
    teacherList.value = res.data?.teacher_list || [];
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else if (status === 403) {
      // 无权查看教师列表，静默失败
      teacherList.value = [];
    } else {
      // 其他错误也静默失败，不影响主流程
      teacherList.value = [];
    }
  } finally {
    loadingTeachers.value = false;
  }
};

const fetchData = async () => {
  loading.value = true;
  try {
    // 获取课程信息
    const coursesRes = await fetchTeacherCourses();
    const courseList = coursesRes.data?.course_list || [];
    courseInfo.value = courseList.find(c => c.id === courseId.value);

    if (!courseInfo.value) {
      ElMessage.error('课程不存在或无权访问');
      router.push({ name: 'TeacherHome' });
      return;
    }

    // 获取作业列表
    const homeworksRes = await fetchCourseHomeworks(courseId.value);
    homeworks.value = homeworksRes.data?.homework_list || [];
    
    // 获取助教列表
    await fetchTAs();
    
    // 如果是助教登录，获取教师列表
    if (userStore.user?.role === 'ta') {
      await fetchTeachers();
    }
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else {
      ElMessage.error(error?.response?.data?.error || '获取数据失败');
    }
  } finally {
    loading.value = false;
  }
};

// 打开导出成绩单对话框
const handleExportGrades = async () => {
  try {
    await loadCourseStudents();
    // 默认全选所有作业和学生
    exportSelectedHomeworkIds.value = homeworks.value.map(hw => hw.id);
    exportSelectedStudentIds.value = courseStudents.value.map(stu => stu.id);
    exportHomeworkCheckAll.value = true;
    exportHomeworkIndeterminate.value = false;
    exportStudentCheckAll.value = true;
    exportStudentIndeterminate.value = false;
    exportDialogVisible.value = true;
  } catch {
    // 已在 loadCourseStudents 中处理提示
  }
};

// 作业选择变化
const handleExportHomeworkChange = (val) => {
  const checkedCount = val.length;
  const total = homeworks.value.length;
  exportHomeworkCheckAll.value = checkedCount === total;
  exportHomeworkIndeterminate.value = checkedCount > 0 && checkedCount < total;
};

const handleExportHomeworkCheckAll = (val) => {
  if (val) {
    exportSelectedHomeworkIds.value = homeworks.value.map(hw => hw.id);
  } else {
    exportSelectedHomeworkIds.value = [];
  }
  exportHomeworkIndeterminate.value = false;
};

// 学生选择变化
const handleExportStudentChange = (val) => {
  const checkedCountInFiltered = filteredCourseStudents.value.filter(stu =>
    val.includes(stu.id)
  ).length;
  const totalFiltered = filteredCourseStudents.value.length;
  exportStudentCheckAll.value = totalFiltered > 0 && checkedCountInFiltered === totalFiltered;
  exportStudentIndeterminate.value =
    checkedCountInFiltered > 0 && checkedCountInFiltered < totalFiltered;
};

const handleExportStudentCheckAll = (val) => {
  if (val) {
    // 全选当前筛选结果（在原有选择基础上合并）
    const idsToAdd = filteredCourseStudents.value.map(stu => stu.id);
    const set = new Set(exportSelectedStudentIds.value);
    idsToAdd.forEach(id => set.add(id));
    exportSelectedStudentIds.value = Array.from(set);
  } else {
    // 取消当前筛选结果中的所有学生
    const idsToRemove = new Set(filteredCourseStudents.value.map(stu => stu.id));
    exportSelectedStudentIds.value = exportSelectedStudentIds.value.filter(
      id => !idsToRemove.has(id)
    );
  }
  exportStudentIndeterminate.value = false;
};

// 获取学生列表容器 DOM（用于框选计算）
const getStudentListContainer = () => {
  const scroll = exportStudentListRef.value;
  if (!scroll) return null;
  // Element Plus el-scrollbar 内部有 wrap 元素，优先取 wrap
  const el = scroll.$el || scroll;
  return el.querySelector('.el-scrollbar__wrap') || el;
};

// 学生列表鼠标按下（开始框选）
const onStudentListMouseDown = (event) => {
  if (event.button !== 0) return; // 只响应左键
  const container = getStudentListContainer();
  if (!container) return;
  const rect = container.getBoundingClientRect();
  isDragSelectingStudents.value = true;
  dragStartPoint.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  };
  dragCurrentPoint.value = { ...dragStartPoint.value };
};

// 学生列表鼠标移动（更新框选区域）
const onStudentListMouseMove = (event) => {
  if (!isDragSelectingStudents.value) return;
  const container = getStudentListContainer();
  if (!container) return;
  const rect = container.getBoundingClientRect();
  dragCurrentPoint.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top,
  };
};

// 学生列表鼠标松开（结束框选并选中区域内学生）
const onStudentListMouseUp = () => {
  if (!isDragSelectingStudents.value) return;
  const container = getStudentListContainer();
  if (!container) {
    isDragSelectingStudents.value = false;
    return;
  }

  const containerRect = container.getBoundingClientRect();
  const x1 = Math.min(dragStartPoint.value.x, dragCurrentPoint.value.x) + containerRect.left;
  const y1 = Math.min(dragStartPoint.value.y, dragCurrentPoint.value.y) + containerRect.top;
  const x2 = Math.max(dragStartPoint.value.x, dragCurrentPoint.value.x) + containerRect.left;
  const y2 = Math.max(dragStartPoint.value.y, dragCurrentPoint.value.y) + containerRect.top;

  const newSelected = new Set(exportSelectedStudentIds.value);

  const checkboxEls = container.querySelectorAll('.export-checkbox-group .el-checkbox');
  checkboxEls.forEach((el) => {
    const box = el.getBoundingClientRect();
    const overlap = !(
      box.right < x1 ||
      box.left > x2 ||
      box.bottom < y1 ||
      box.top > y2
    );
    if (overlap) {
      const idStr = el.getAttribute('data-student-id') || el.dataset.studentId;
      const id = Number(idStr);
      if (!Number.isNaN(id)) {
        newSelected.add(id);
      }
    }
  });

  exportSelectedStudentIds.value = Array.from(newSelected);
  isDragSelectingStudents.value = false;
};

// 确认导出成绩单
const confirmExportGrades = async () => {
  if (!homeworks.value.length) {
    ElMessage.warning('当前课程暂无作业，无法导出成绩单');
    return;
  }
  if (!courseStudents.value.length) {
    ElMessage.warning('当前课程暂无学生，无法导出成绩单');
    return;
  }

  // 如果未选择，则默认全部
  const homeworkIds = exportSelectedHomeworkIds.value.length
    ? exportSelectedHomeworkIds.value
    : homeworks.value.map(hw => hw.id);
  const studentIds = exportSelectedStudentIds.value.length
    ? exportSelectedStudentIds.value
    : courseStudents.value.map(stu => stu.id);

  exporting.value = true;
  try {
    const filters = {
      homework_ids: homeworkIds.join(','),
      student_ids: studentIds.join(','),
    };
    const response = await exportCourseGrades(courseId.value, filters);

    // 创建 Blob 对象
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });

    // 创建下载链接
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `课程成绩表_${courseInfo.value?.course_name || '成绩'}_${new Date()
      .toISOString()
      .slice(0, 10)}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    ElMessage.success('成绩单导出成功');
    exportDialogVisible.value = false;
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else {
      ElMessage.error(error?.response?.data?.error || '导出失败，请重试');
    }
  } finally {
    exporting.value = false;
  }
};

onMounted(() => {
  fetchData();
  
  // 如果 URL 中有 action=create-homework，直接打开创建对话框
  if (route.query.action === 'create-homework') {
    showCreateHomeworkDialog.value = true;
  }
});
</script>

<style scoped>
.teacher-course-detail {
  min-height: 100vh;
  background: #f5f7fa;
}

.export-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.export-student-search {
  max-width: 260px;
}

.export-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  margin-top: 8px;
}

.export-student-list {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 8px 12px;
  margin-top: 8px;
}

.export-student-list-inner {
  position: relative;
  user-select: none;
}

.export-selection-rect {
  position: absolute;
  border: 1px dashed #409eff;
  background-color: rgba(64, 158, 255, 0.12);
  pointer-events: none;
  z-index: 10;
}

.export-loading-tip {
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
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

/* 顶部横幅 */
.course-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px 24px;
  margin-bottom: 20px;
  border-radius: 16px;
  background: linear-gradient(135deg, #1e293b, #3b82f6);
  color: #ffffff !important;
}

.course-hero-left {
  max-width: 60%;
}

.hero-breadcrumb {
  font-size: 12px;
  opacity: 0.95;
  margin: 0 0 4px;
  color: rgba(255, 255, 255, 0.95) !important;
}

.hero-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 10px;
  color: #ffffff !important;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.hero-code-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.35);
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.hero-code-pill:hover {
  background: rgba(15, 23, 42, 0.5);
  transform: translateY(-1px);
}

.code-label {
  font-size: 12px;
  opacity: 0.95;
  color: rgba(255, 255, 255, 0.95) !important;
}

.code-value {
  font-family: 'Courier New', monospace;
  letter-spacing: 2px;
  font-weight: 600;
  color: #ffffff !important;
}

.hero-text {
  font-size: 13px;
  opacity: 0.95;
  color: rgba(255, 255, 255, 0.95) !important;
}

.course-hero-right {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}

.course-hero-right .el-statistic .el-statistic__title {
  color: rgba(255, 255, 255, 0.8);
}

.course-hero-right .el-statistic .el-statistic__content {
  color: #ffffff;
}

/* 助教信息卡片 */
.ta-section {
  margin-bottom: 20px;
}

.ta-card {
  border-radius: 12px;
}

.ta-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ta-card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.ta-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.ta-section-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.ta-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.ta-card-item {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.ta-card-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.ta-card-content {
  padding: 4px;
}

.ta-card-header-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.ta-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
}

.teacher-avatar {
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
}

.ta-header-text {
  flex: 1;
  min-width: 0;
}

.ta-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.ta-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.ta-student-no {
  font-size: 13px;
  color: #909399;
}

.ta-card-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ta-detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.ta-detail-icon {
  color: #909399;
  font-size: 16px;
  flex-shrink: 0;
}

.ta-detail-text {
  flex: 1;
  min-width: 0;
  word-break: break-all;
}

.ta-no-contact {
  color: #c0c4cc;
  font-style: italic;
}

/* 工具栏 */
.course-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
}

.toolbar-left {
  flex: 1;
}

.toolbar-search {
  max-width: 320px;
}

.toolbar-right {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

/* 作业任务清单 */
.homework-task-section {
  margin-bottom: 24px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  border-radius: 10px;
  background-color: #ffffff;
  box-shadow: 0 1px 4px rgba(15, 23, 42, 0.04);
  transition: background-color 0.2s ease, transform 0.1s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.task-item:hover {
  background-color: #f9fafb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.task-icon {
  margin-right: 12px;
  font-size: 20px;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.task-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.task-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.task-title:hover {
  color: #3b82f6;
}

.task-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 13px;
  color: #909399;
}

.task-deadline {
  display: inline-flex;
  align-items: center;
}

.task-sub-info {
  display: inline-flex;
  align-items: center;
}

.task-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  margin-left: 16px;
}

.task-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.task-actions {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.progress-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-text {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

/* 上传组件样式优化 */
:deep(.el-upload--picture-card) {
  width: 100px;
  height: 100px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
}

:deep(.el-upload--picture-card:hover) {
  border-color: #409EFF;
}

:deep(.el-upload-list--picture-card) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

:deep(.el-upload-list--picture-card .el-upload-list__item) {
  width: 100px;
  height: 100px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  padding: 0;
}

/* 自定义文件项样式 */
.upload-file-item {
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-file-item:hover {
  background: #eef2ff;
}

.upload-file-item.is-pdf {
  background: #fff7e6;
}

.upload-file-item.is-pdf:hover {
  background: #ffecc7;
}

.upload-file-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
}

.upload-file-pdf-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #e6a23c;
  cursor: pointer;
}

.upload-file-pdf-text {
  font-size: 12px;
  font-weight: 600;
}

.upload-file-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.upload-file-actions {
  position: absolute;
  top: 0;
  right: 0;
  display: flex;
  gap: 4px;
  padding: 4px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 0 6px 0 6px;
  opacity: 0;
  transition: opacity 0.3s;
}

.upload-file-item:hover .upload-file-actions {
  opacity: 1;
}

.upload-file-preview,
.upload-file-delete {
  color: white;
  cursor: pointer;
  font-size: 16px;
  padding: 2px;
  transition: color 0.3s;
}

.upload-file-preview:hover {
  color: #409EFF;
}

.upload-file-delete:hover {
  color: #f56c6c;
}

.upload-file-name {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 10px;
  padding: 2px 4px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  text-align: center;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

@media (max-width: 768px) {
  .course-detail-container {
    padding: 16px;
  }

  .course-hero {
    flex-direction: column;
    gap: 12px;
  }
}
</style>

