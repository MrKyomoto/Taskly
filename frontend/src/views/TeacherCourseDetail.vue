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
                    <el-button type="primary" text size="small" @click="goToGrading(hw)">
                      去批改
                    </el-button>
                    <el-button
                      v-if="userStore.user?.role === 'teacher'"
                      type="success"
                      text
                      size="small"
                      :disabled="!canPublishGrades(hw)"
                      @click="handlePublishGrades(hw)"
                    >
                      发布成绩
                    </el-button>
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
        <el-form-item label="助教工号" prop="staff_no">
          <el-input
            v-model="addTAForm.staff_no"
            placeholder="请输入助教工号"
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
        <el-form-item label="参考图片">
          <el-upload
            v-model:file-list="homeworkImageList"
            :action="uploadAction"
            :headers="uploadHeaders"
            :before-upload="beforeUpload"
            :on-success="handleImageUploadSuccess"
            :on-remove="handleImageRemove"
            :on-error="handleImageUploadError"
            list-type="picture-card"
            :limit="5"
            accept="image/*"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">支持上传参考图片，最多5张</div>
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
        <el-button type="primary" @click="editingHomework ? handleUpdateHomework() : handleCreateHomework()" :loading="creatingHomework">
          {{ editingHomework ? '保存' : '发布' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { ArrowLeft, Plus, DocumentCopy, UserFilled, Download, Search, Timer, CircleCheck, Trophy } from '@element-plus/icons-vue';
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
} from '@/api/teacher';
import { getImageUrl, parseImageUrls } from '@/utils/image';

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
const showAddTADialog = ref(false);
const addingTA = ref(false);
const addTAForm = ref({
  staff_no: '',
});
const addTAFormRef = ref(null);
const addTARules = {
  staff_no: [{ required: true, message: '请输入助教工号', trigger: 'blur' }],
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

const homeworkRules = {
  title: [{ required: true, message: '请输入作业标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入作业描述', trigger: 'blur' }],
  deadline: [{ required: true, message: '请选择截止时间', trigger: 'change' }],
};

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
  router.push({ name: 'TeacherHome' });
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

// 发布某次作业的成绩（老师全部批改完成后手动提交）
const handlePublishGrades = async (homework) => {
  if (!canPublishGrades(homework)) {
    ElMessage.warning('还有未批改的学生，暂时不能发布成绩');
    return;
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
    console.error('发布成绩失败:', error);
    ElMessage.error(error.response?.data?.error || '发布成绩失败，请稍后重试');
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
  homeworkImageList.value = homeworkImageUrls.value.map((url, index) => ({
    uid: index,
    name: `image-${index}.jpg`,
    url: getImageUrl(url),
    status: 'success',
  }));
  
  showCreateHomeworkDialog.value = true;
};

// 取消作业对话框
const handleCancelHomeworkDialog = () => {
  showCreateHomeworkDialog.value = false;
  editingHomework.value = null;
  homeworkForm.value = {
    title: '',
    content: '',
    deadline: '',
    max_score: 100,  // 重置为默认值
  };
  homeworkImageList.value = [];
  homeworkImageUrls.value = [];
};

// 更新作业
const handleUpdateHomework = async () => {
  if (!homeworkFormRef.value) return;
  try {
    await homeworkFormRef.value.validate();
    
    if (!homeworkForm.value.deadline) {
      ElMessage.warning('请选择截止时间');
      return;
    }

    creatingHomework.value = true;
    
    await updateHomework(courseId.value, editingHomework.value, {
      title: homeworkForm.value.title,
      content: homeworkForm.value.content,
      deadline: homeworkForm.value.deadline,
      max_score: homeworkForm.value.max_score,
      image_urls: homeworkImageUrls.value,
    });
    
    ElMessage.success('作业更新成功');
    handleCancelHomeworkDialog();
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
      staff_no: addTAForm.value.staff_no,
    });
    
    ElMessage.success('助教添加成功');
    showAddTADialog.value = false;
    addTAForm.value = {
      staff_no: '',
    };
    await fetchData(); // 刷新数据
  } catch (error) {
    const status = error?.response?.status;
    if (status === 400) {
      ElMessage.error(error?.response?.data?.error || '添加失败，请检查工号');
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

// 上传前验证
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/');
  const isLt10M = file.size / 1024 / 1024 < 10;

  if (!isImage) {
    ElMessage.error('只能上传图片文件！');
    return false;
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB！');
    return false;
  }
  return true;
};

// 图片上传成功
const handleImageUploadSuccess = (response) => {
  const imageUrl = response?.image_urls?.[0] || response?.image_url || response;
  if (imageUrl) {
    homeworkImageUrls.value.push(imageUrl);
    ElMessage.success('图片上传成功');
  }
};

// 删除图片
const handleImageRemove = (file) => {
  const url = file.response?.image_urls?.[0] || file.response?.image_url || file.url;
  const index = homeworkImageUrls.value.findIndex(u => u === url);
  if (index > -1) {
    homeworkImageUrls.value.splice(index, 1);
  }
};

// 图片上传失败
const handleImageUploadError = () => {
  ElMessage.error('图片上传失败，请重试');
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

    creatingHomework.value = true;
    
    // 计算作业序号（当前课程最大序号 + 1）
    const maxHwNo = homeworks.value.length > 0 
      ? Math.max(...homeworks.value.map(h => h.course_hw_no || 0))
      : 0;
    
    await createHomework(courseId.value, {
      title: homeworkForm.value.title,
      content: homeworkForm.value.content,
      deadline: homeworkForm.value.deadline,
      course_hw_no: maxHwNo + 1,
      max_score: homeworkForm.value.max_score || 100,
      image_urls: homeworkImageUrls.value,
    });
    
    ElMessage.success('作业发布成功');
    handleCancelHomeworkDialog();
    await fetchData();
  } catch (error) {
    const status = error?.response?.status;
    if (status === 400) {
      ElMessage.error(error?.response?.data?.error || '发布失败，请检查输入');
    } else if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else {
      ElMessage.error(error?.response?.data?.error || '发布失败，请重试');
    }
  } finally {
    creatingHomework.value = false;
  }
};

// 获取数据
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
  color: #fff;
}

.course-hero-left {
  max-width: 60%;
}

.hero-breadcrumb {
  font-size: 12px;
  opacity: 0.8;
  margin: 0 0 4px;
}

.hero-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 10px;
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
  opacity: 0.85;
}

.code-value {
  font-family: 'Courier New', monospace;
  letter-spacing: 2px;
  font-weight: 600;
}

.hero-text {
  font-size: 13px;
  opacity: 0.9;
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

