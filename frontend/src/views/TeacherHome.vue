<template>
  <div class="teacher-home">
    <el-header class="header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="header-title">我的教学课程</h1>
          <el-tag v-if="userStore.user?.role === 'ta'" type="info" size="small" class="role-tag">
            当前身份：助教
          </el-tag>
        </div>
        <div class="header-actions">
          <el-button 
            v-if="userStore.user?.role === 'teacher'" 
            type="primary" 
            @click="showCreateCourseDialog = true" 
            :icon="Plus"
          >
            新增教学课程
          </el-button>
          <el-dropdown @command="handleCommand">
            <span class="dropdown-trigger">
              {{ profile?.name || '老师' }}
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-header>

    <div class="teacher-home-container" v-loading="loading">
      <template v-if="!loading">
        <!-- 课程看板 -->
        <section class="course-center">
          <div class="section-header">
            <h2 class="section-title">我的课程</h2>
            <!-- 搜索 -->
            <div class="search-filter-section">
              <el-input
                v-model="courseSearchQuery"
                placeholder="搜索课程名称或课程号..."
                clearable
                style="width: 300px;"
                :prefix-icon="Search"
              />
            </div>
          </div>

          <el-tabs v-model="activeCourseTab" class="course-tabs">
            <!-- 当前学期课程 -->
            <el-tab-pane label="当前学期课程" name="current">
              <p v-if="!currentSemester" class="semester-tip">
                当前暂无学期信息，请在创建课程时填写学期。
              </p>
              <el-row v-if="filteredCurrentCourses.length > 0" :gutter="20">
                <el-col
                  v-for="course in filteredCurrentCourses"
                  :key="course.id"
                  :xs="24"
                  :sm="12"
                  :md="8"
                  :lg="6"
                  :xl="6"
                >
                  <el-card 
                    class="course-card app-card" 
                    shadow="hover"
                    @click="goToCourseDetail(course.id)"
                  >
                    <!-- 封面区域 -->
                    <div
                      class="course-cover"
                      :style="{ background: getCourseGradient(course.course_code) }"
                    >
                      <div class="course-cover-inner">
                        <h3 class="course-name">{{ course.course_name }}</h3>
                        <p class="course-semester">{{ course.semester || '未设置学期' }}</p>
                      </div>
                    </div>
                    <div class="course-card-body">
                      <div class="course-tags">
                        <el-tag type="info" size="small" effect="plain">
                          {{ course.semester || '未设置学期' }}
                        </el-tag>
                        <el-tag type="success" size="small" effect="plain">
                          学生 {{ course.student_count || 0 }}
                        </el-tag>
                      </div>
                      <div
                        class="course-code-section"
                        @click.stop="copyCourseCode(course.course_code)"
                      >
                        <span class="course-code-label">课程号</span>
                        <div class="course-code-display">
                          <span class="course-code-value">{{ course.course_code }}</span>
                          <el-button 
                            text 
                            type="primary" 
                            size="small" 
                            :icon="DocumentCopy"
                            class="copy-btn"
                          >
                            复制
                          </el-button>
                        </div>
                      </div>
                      <div class="course-stats">
                        <span class="stat-item">
                          <span class="stat-label">学生人数：</span>
                          <span class="stat-value">{{ course.student_count || 0 }}</span>
                        </span>
                      </div>
                    </div>
                    <div class="course-card-actions" @click.stop>
                      <el-button type="primary" size="small" @click="goToCourseDetail(course.id)">
                        课程详情
                      </el-button>
                      <el-button type="success" size="small" @click="showCreateHomeworkDialog(course.id)">
                        发布作业
                      </el-button>
                      <el-button type="info" size="small" @click="goToGradingCenter(course.id)">
                        批改中心
                      </el-button>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
              <el-empty 
                v-else 
                :description="courseSearchQuery ? '当前学期中没有找到匹配的课程' : '当前学期暂无课程'"
                :image-size="100" 
              />
            </el-tab-pane>

            <!-- 历史学期课程 -->
            <el-tab-pane label="历史学期课程" name="history">
              <div class="history-semester-filter" v-if="historySemesters.length">
                <span class="history-semester-label">学期：</span>
                <el-select
                  v-model="selectedHistorySemester"
                  placeholder="按时间顺序选择学期（最近 → 最远）"
                  clearable
                  style="width: 260px;"
                >
                  <el-option
                    v-for="semester in historySemesters"
                    :key="semester"
                    :label="semester"
                    :value="semester"
                  />
                </el-select>
              </div>
              <p v-else class="semester-tip">
                暂无历史学期课程。
              </p>

              <el-row v-if="filteredHistoryCourses.length > 0" :gutter="20">
                <el-col
                  v-for="course in filteredHistoryCourses"
                  :key="course.id"
                  :xs="24"
                  :sm="12"
                  :md="8"
                  :lg="6"
                  :xl="6"
                >
                  <el-card 
                    class="course-card app-card" 
                    shadow="hover"
                    @click="goToCourseDetail(course.id)"
                  >
                    <!-- 封面区域 -->
                    <div
                      class="course-cover"
                      :style="{ background: getCourseGradient(course.course_code) }"
                    >
                      <div class="course-cover-inner">
                        <h3 class="course-name">{{ course.course_name }}</h3>
                        <p class="course-semester">{{ course.semester || '未设置学期' }}</p>
                      </div>
                    </div>
                    <div class="course-card-body">
                      <div class="course-tags">
                        <el-tag type="info" size="small" effect="plain">
                          {{ course.semester || '未设置学期' }}
                        </el-tag>
                        <el-tag type="success" size="small" effect="plain">
                          学生 {{ course.student_count || 0 }}
                        </el-tag>
                      </div>
                      <div
                        class="course-code-section"
                        @click.stop="copyCourseCode(course.course_code)"
                      >
                        <span class="course-code-label">课程号</span>
                        <div class="course-code-display">
                          <span class="course-code-value">{{ course.course_code }}</span>
                          <el-button 
                            text 
                            type="primary" 
                            size="small" 
                            @click="copyCourseCode(course.course_code)"
                            :icon="DocumentCopy"
                            class="copy-btn"
                          >
                            复制
                          </el-button>
                        </div>
                      </div>
                      <div class="course-stats">
                        <span class="stat-item">
                          <span class="stat-label">学生人数：</span>
                          <span class="stat-value">{{ course.student_count || 0 }}</span>
                        </span>
                      </div>
                    </div>
                    <div class="course-card-actions" @click.stop>
                      <el-button type="primary" size="small" @click="goToCourseDetail(course.id)">
                        课程详情
                      </el-button>
                      <el-button type="success" size="small" @click="showCreateHomeworkDialog(course.id)">
                        发布作业
                      </el-button>
                      <el-button type="info" size="small" @click="goToGradingCenter(course.id)">
                        批改中心
                      </el-button>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
              <el-empty 
                v-else 
                :description="courseSearchQuery || selectedHistorySemester ? '该学期中没有找到匹配的课程' : '该学期暂无课程'"
                :image-size="100" 
              />
            </el-tab-pane>
          </el-tabs>
        </section>
      </template>
    </div>

    <!-- 新增教学课程对话框 -->
    <el-dialog 
      v-model="showCreateCourseDialog" 
      title="新增教学课程" 
      width="500px"
      @closed="handleDialogClosed"
    >
      <el-form 
        :model="createCourseForm" 
        :rules="createCourseRules" 
        ref="createCourseFormRef" 
        label-width="100px"
        @keyup.enter="handleCreateCourse"
      >
        <el-form-item label="课程名称" prop="course_name">
          <el-input
            v-model="createCourseForm.course_name"
            placeholder="请输入课程名称"
            @keyup.enter="handleCreateCourse"
          />
        </el-form-item>
        <el-form-item label="学期" prop="semester">
          <div class="semester-select-group">
            <el-input-number
              v-model="createCourseForm.semesterYear"
              :min="2000"
              :max="2100"
              :precision="0"
              controls-position="right"
              style="width: 140px; margin-right: 8px;"
            />
            <el-select
              v-model="createCourseForm.semesterTerm"
              placeholder="请选择学期"
              style="width: 160px;"
            >
              <el-option label="Spring" value="Spring" />
              <el-option label="Summer" value="Summer" />
              <el-option label="Fall" value="Fall" />
            </el-select>
          </div>
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input
            v-model="createCourseForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入课程描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateCourseDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateCourse" :loading="creatingCourse">新增</el-button>
      </template>
    </el-dialog>

    <!-- 个人资料抽屉 -->
    <el-drawer v-model="profileDrawerVisible" title="个人资料" size="30%">
      <div v-if="profile" class="profile-details">
        <div v-if="!isEditing" class="profile-view">
          <div class="profile-item">
            <span class="label">姓名：</span>
            <span class="value">{{ profile.name }}</span>
          </div>
          <div class="profile-item">
            <span class="label">工号：</span>
            <span class="value">{{ profile.staff_no }}</span>
          </div>
          <div class="profile-item">
            <span class="label">邮箱：</span>
            <span class="value">{{ profile.email || '未填写' }}</span>
          </div>
          <div class="profile-item">
            <span class="label">电话：</span>
            <span class="value">{{ profile.phone || '未填写' }}</span>
          </div>
          <div class="profile-actions">
            <el-button type="primary" @click="startEditing">编辑资料</el-button>
            <el-button @click="showPasswordDialog">修改密码</el-button>
          </div>
        </div>
        <div v-else class="profile-edit">
          <el-form :model="editForm" label-width="80px" ref="editFormRef">
            <el-form-item label="姓名">
              <el-input v-model="editForm.name" @keydown.enter="saveProfile" />
            </el-form-item>
            <el-form-item label="邮箱">
              <div class="email-input-group">
                <el-input 
                  v-model="editForm.emailPrefix" 
                  placeholder="邮箱前缀" 
                  @keydown.enter="saveProfile"
                  style="flex: 2; min-width: 200px"
                ></el-input>
                <span class="email-separator">@</span>
                <el-select 
                  v-model="editForm.emailSuffix" 
                  placeholder="选择或输入后缀"
                  style="width: 140px"
                  @keydown.enter.native="saveProfile"
                  filterable
                  allow-create
                  default-first-option
                  :max-height="200"
                >
                  <el-option
                    v-for="suffix in emailSuffixes"
                    :key="suffix"
                    :label="suffix"
                    :value="suffix"
                  />
                </el-select>
              </div>
            </el-form-item>
            <el-form-item label="电话">
              <div class="phone-input-group">
                <el-select 
                  v-model="editForm.phoneCode" 
                  placeholder="区号"
                  style="width: 100px"
                  @keydown.enter.native="saveProfile"
                >
                  <el-option
                    v-for="code in phoneCodes"
                    :key="code.value"
                    :label="code.label"
                    :value="code.value"
                  />
                </el-select>
                <el-input 
                  v-model="editForm.phoneNumber" 
                  placeholder="手机号" 
                  @keydown.enter="saveProfile"
                  style="flex: 2; margin-left: 8px; min-width: 180px"
                ></el-input>
              </div>
            </el-form-item>
          </el-form>
          <div class="profile-actions">
            <el-button type="primary" @click="saveProfile" :loading="saving">保存</el-button>
            <el-button @click="cancelEditing">取消</el-button>
          </div>
        </div>
      </div>
      <el-empty v-else description="尚未获取资料" />
    </el-drawer>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="原密码" prop="old_password">
          <el-input v-model="passwordForm.old_password" type="password" show-password @keyup.enter="submitPassword" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password @keyup.enter="submitPassword" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password @keyup.enter="submitPassword" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPassword" :loading="changingPassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter, onBeforeRouteLeave } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, ArrowDown, DocumentCopy, Search } from '@element-plus/icons-vue';
import { useUserStore } from '@/store/user';
import { fetchTeacherProfile, fetchTeacherCourses, createCourse, updateTeacherProfile, updateTeacherPassword } from '@/api/teacher';
import { validatePassword } from '@/utils/validators';

const router = useRouter();
const userStore = useUserStore();

const loading = ref(false);
const profile = ref(null);
const courses = ref([]);
const courseSearchQuery = ref('');
const activeCourseTab = ref('current');
const selectedHistorySemester = ref('');
const showCreateCourseDialog = ref(false);

// 可用学期列表（从课程中提取）
const availableSemesters = computed(() => {
  const semesters = new Set();
  courses.value.forEach(course => {
    if (course.semester) {
      semesters.add(course.semester);
    }
  });
  return Array.from(semesters).sort().reverse(); // 按时间倒序
});

// 当前学期（按学期列表中最新的一项作为当前学期）
const currentSemester = computed(() => availableSemesters.value[0] || '');

// 历史学期列表（去掉当前学期，其余从近到远）
const historySemesters = computed(() => {
  return availableSemesters.value.slice(1);
});

// 当前学期课程
const filteredCurrentCourses = computed(() => {
  let result = courses.value;

  if (currentSemester.value) {
    result = result.filter(course => course.semester === currentSemester.value);
  }

  if (courseSearchQuery.value && courseSearchQuery.value.trim()) {
    const query = courseSearchQuery.value.trim().toLowerCase();
    result = result.filter(course => {
      const nameMatch = course.course_name?.toLowerCase().includes(query);
      const codeMatch = course.course_code?.toLowerCase().includes(query);
      return nameMatch || codeMatch;
    });
  }

  return result;
});

// 历史学期课程
const filteredHistoryCourses = computed(() => {
  let result = courses.value;

  if (currentSemester.value) {
    result = result.filter(course => course.semester && course.semester !== currentSemester.value);
  } else {
    // 如果没有当前学期定义，则不显示历史课程
    result = [];
  }

  if (selectedHistorySemester.value) {
    result = result.filter(course => course.semester === selectedHistorySemester.value);
  }

  if (courseSearchQuery.value && courseSearchQuery.value.trim()) {
    const query = courseSearchQuery.value.trim().toLowerCase();
    result = result.filter(course => {
      const nameMatch = course.course_name?.toLowerCase().includes(query);
      const codeMatch = course.course_code?.toLowerCase().includes(query);
      return nameMatch || codeMatch;
    });
  }

  return result;
});
const creatingCourse = ref(false);
const profileDrawerVisible = ref(false);
const isEditing = ref(false);
const hasChanged = ref(false);
const saving = ref(false);
const editForm = ref({
  name: '',
  emailPrefix: '',
  emailSuffix: 'ustc.edu.cn', // 教师默认
  phoneCode: '+86',
  phoneNumber: '',
});
const editFormRef = ref(null);

// 邮箱后缀选项
const emailSuffixes = ['ustc.edu.cn', 'mail.ustc.edu.cn', 'gmail.com', '163.com', 'qq.com', 'outlook.com', 'sina.com', 'yahoo.com', 'hotmail.com'];

// 全球区号选项
const phoneCodes = [
  { label: '中国 +86', value: '+86' },
  { label: '美国 +1', value: '+1' },
  { label: '英国 +44', value: '+44' },
  { label: '日本 +81', value: '+81' },
  { label: '韩国 +82', value: '+82' },
  { label: '德国 +49', value: '+49' },
  { label: '法国 +33', value: '+33' },
  { label: '加拿大 +1', value: '+1' },
  { label: '澳大利亚 +61', value: '+61' },
  { label: '新加坡 +65', value: '+65' },
];

const passwordDialogVisible = ref(false);
const changingPassword = ref(false);
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: '',
});
const passwordFormRef = ref(null);

const passwordRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.new_password) {
          callback(new Error('两次输入的密码不一致'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ],
};

const currentYear = new Date().getFullYear();

const createCourseForm = ref({
  course_name: '',
  semesterYear: currentYear,
  semesterTerm: 'Fall',
  semester: '',
  description: '',
});

const createCourseFormRef = ref(null);

const createCourseRules = {
  course_name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  semester: [
    {
      validator: (_rule, _value, callback) => {
        const { semesterYear, semesterTerm } = createCourseForm.value;
        if (!semesterYear || !semesterTerm) {
          callback(new Error('请选择学期'));
        } else {
          callback();
        }
      },
      trigger: 'change',
    },
  ],
};

// 根据年份和学期拼接最终学期字符串（例如 2024-Fall）
const updateSemesterString = () => {
  const { semesterYear, semesterTerm } = createCourseForm.value;
  if (!semesterYear || !semesterTerm) {
    createCourseForm.value.semester = '';
  } else {
    createCourseForm.value.semester = `${semesterYear}-${semesterTerm}`;
  }
};

watch(
  () => [createCourseForm.value.semesterYear, createCourseForm.value.semesterTerm],
  () => {
    updateSemesterString();
  },
  { immediate: true }
);

// 获取数据
const fetchData = async () => {
  loading.value = true;
  try {
    const [profileRes, coursesRes] = await Promise.all([
      fetchTeacherProfile(),
      fetchTeacherCourses(),
    ]);
    profile.value = profileRes.data;
    courses.value = coursesRes.data?.course_list || [];
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

// 当历史学期列表变化时，如果当前没有选择，则默认选中最近的一个历史学期
watch(historySemesters, (list) => {
  if (!selectedHistorySemester.value && list.length > 0) {
    selectedHistorySemester.value = list[0];
  }
});

// 新增教学课程
const handleCreateCourse = async () => {
  if (!createCourseFormRef.value) return;
  try {
    await createCourseFormRef.value.validate();
    creatingCourse.value = true;
    // 确保学期字符串已更新
    updateSemesterString();
    const payload = {
      course_name: createCourseForm.value.course_name,
      semester: createCourseForm.value.semester,
      description: createCourseForm.value.description,
    };
    const response = await createCourse(payload);
    const courseCode = response.data?.course?.course_code;
    
    // 显示创建成功并高亮课程号
    showCreateCourseDialog.value = false;
    createCourseForm.value = {
      course_name: '',
      semesterYear: currentYear,
      semesterTerm: 'Fall',
      semester: '',
      description: '',
    };
    
    // 显示课程号提示
    ElMessageBox.alert(
      `教学课程新增成功！\n\n课程号：${courseCode}\n\n请将此课程号分享给学生，学生可通过课程号加入课程。`,
      '新增成功',
      {
        confirmButtonText: '复制课程号',
        type: 'success',
      }
    ).then(() => {
      copyCourseCode(courseCode);
    });
    
    await fetchData();
  } catch (error) {
    const status = error?.response?.status;
    if (status === 400) {
      ElMessage.error(error?.response?.data?.error || '创建失败，请检查输入');
    } else if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else {
      ElMessage.error(error?.response?.data?.error || '创建失败，请重试');
    }
  } finally {
    creatingCourse.value = false;
  }
};

// 复制课程号
const copyCourseCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code);
    ElMessage.success(`课程号 ${code} 已复制到剪贴板`);
  } catch (error) {
    // 降级方案：使用传统方法
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

// 跳转到课程详情
const goToCourseDetail = (courseId) => {
  router.push({ name: 'TeacherCourseDetail', params: { id: courseId } });
};

// 显示创建作业对话框
const showCreateHomeworkDialog = (courseId) => {
  router.push({ name: 'TeacherCourseDetail', params: { id: courseId }, query: { action: 'create-homework' } });
};

// 跳转到批改中心（暂时跳转到课程详情页，后续步骤会实现批改中心）
const goToGradingCenter = (courseId) => {
  router.push({ name: 'TeacherCourseDetail', params: { id: courseId } });
};

// 课程封面渐变色，根据课程号做一个稳定的颜色分布
const courseGradients = [
  'linear-gradient(135deg, #1e3a8a, #3b82f6)',
  'linear-gradient(135deg, #064e3b, #10b981)',
  'linear-gradient(135deg, #7c2d12, #f97316)',
  'linear-gradient(135deg, #4c1d95, #a855f7)',
  'linear-gradient(135deg, #0f172a, #64748b)',
];

const getCourseGradient = (code) => {
  if (!code) return courseGradients[0];
  let sum = 0;
  for (let i = 0; i < code.length; i += 1) {
    sum += code.charCodeAt(i);
  }
  const idx = sum % courseGradients.length;
  return courseGradients[idx];
};

// 处理对话框关闭
const handleDialogClosed = () => {
  // 重置表单
  createCourseForm.value = {
    course_name: '',
    semesterYear: currentYear,
    semesterTerm: 'Fall',
    semester: '',
    description: '',
  };
  // 清除验证状态
  if (createCourseFormRef.value) {
    createCourseFormRef.value.clearValidate();
  }
};

// 处理下拉菜单命令
const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout();
  } else if (command === 'profile') {
    profileDrawerVisible.value = true;
  }
};

// 解析邮箱
const parseEmail = (email) => {
  if (!email) return { prefix: '', suffix: 'ustc.edu.cn' };
  const parts = email.split('@');
  if (parts.length === 2) {
    return { prefix: parts[0], suffix: parts[1] };
  }
  return { prefix: email, suffix: 'ustc.edu.cn' };
};

// 解析电话
const parsePhone = (phone) => {
  if (!phone) return { code: '+86', number: '' };
  // 尝试匹配区号
  for (const code of phoneCodes) {
    if (phone.startsWith(code.value)) {
      return { code: code.value, number: phone.substring(code.value.length) };
    }
  }
  return { code: '+86', number: phone };
};

// 开始编辑个人资料
const startEditing = () => {
  if (profile.value) {
    const emailParts = parseEmail(profile.value.email);
    const phoneParts = parsePhone(profile.value.phone);
    editForm.value = {
      name: profile.value.name || '',
      emailPrefix: emailParts.prefix,
      emailSuffix: emailParts.suffix || 'ustc.edu.cn',
      phoneCode: phoneParts.code || '+86',
      phoneNumber: phoneParts.number || '',
    };
    isEditing.value = true;
    hasChanged.value = false;
  }
};

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false;
  hasChanged.value = false;
  editForm.value = {
    name: '',
    emailPrefix: '',
    emailSuffix: 'ustc.edu.cn',
    phoneCode: '+86',
    phoneNumber: '',
  };
};

// 保存个人资料
const saveProfile = async () => {
  if (!editFormRef.value) return;
  
  try {
    await editFormRef.value.validate();
    saving.value = true;
    
    // 拼接完整邮箱和电话
    const email = editForm.value.emailPrefix + '@' + editForm.value.emailSuffix;
    const phone = editForm.value.phoneCode + editForm.value.phoneNumber;
    
    await updateTeacherProfile({
      name: editForm.value.name,
      email: email,
      phone: phone,
    });
    ElMessage.success('个人资料更新成功');
    await fetchData(); // 重新获取数据
    isEditing.value = false;
    hasChanged.value = false;
  } catch (error) {
    if (error?.response?.data?.error) {
      ElMessage.error(error.response.data.error);
    } else if (typeof error === 'object' && error !== null) {
      // 表单验证错误，不显示错误消息
    } else {
      ElMessage.error('更新失败，请重试');
    }
  } finally {
    saving.value = false;
  }
};

// 显示修改密码对话框
const showPasswordDialog = () => {
  passwordDialogVisible.value = true;
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: '',
  };
  if (passwordFormRef.value) {
    passwordFormRef.value.clearValidate();
  }
};

// 提交密码修改
const submitPassword = async () => {
  if (!passwordFormRef.value) return;
  
  try {
    await passwordFormRef.value.validate();
    changingPassword.value = true;
    await updateTeacherPassword({
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
    });
    ElMessage.success('密码修改成功，请重新登录');
    passwordDialogVisible.value = false;
    // 延迟一下再退出，让用户看到成功消息
    setTimeout(() => {
      userStore.logout();
      router.push({ name: 'Login' });
    }, 1500);
  } catch (error) {
    if (error?.response?.data?.error) {
      ElMessage.error(error.response.data.error);
    } else if (typeof error === 'object' && error !== null) {
      // 表单验证错误，不显示错误消息
    } else {
      ElMessage.error('修改失败，请重试');
    }
  } finally {
    changingPassword.value = false;
  }
};

// 检查是否有未保存的修改
const checkUnsavedChanges = () => {
  return new Promise((resolve) => {
    if (isEditing.value) {
      ElMessageBox.confirm(
        '您有未保存的修改，确定要离开吗？',
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).then(() => {
        isEditing.value = false;
        hasChanged.value = false;
        resolve(true);
      }).catch(() => {
        resolve(false);
      });
    } else {
      resolve(true);
    }
  });
};

// 监听 drawer 关闭，检查是否有未保存的修改
watch(profileDrawerVisible, async (newVal, oldVal) => {
  if (oldVal === true && newVal === false) {
    const shouldClose = await checkUnsavedChanges();
    if (!shouldClose) {
      profileDrawerVisible.value = true;
    }
  }
});

// 监听表单变化
watch(editForm, () => {
  if (isEditing.value) {
    hasChanged.value = true;
  }
}, { deep: true });

// 路由守卫：检查是否有未保存的修改
onBeforeRouteLeave(async (to, from, next) => {
  const shouldLeave = await checkUnsavedChanges();
  if (shouldLeave) {
    next();
  } else {
    next(false);
  }
});

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.teacher-home {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.role-tag {
  margin-left: 8px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.dropdown-trigger {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.teacher-home-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.course-center {
  margin-bottom: 30px;
}

.course-tabs {
  margin-top: 8px;
}

.semester-tip {
  font-size: 13px;
  color: #909399;
  margin: 4px 0 12px;
}

.history-semester-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.history-semester-label {
  font-size: 13px;
  color: #606266;
}

.section-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.search-filter-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.course-card {
  margin-bottom: 20px;
  cursor: pointer;
}

.course-cover {
  height: 100px;
  border-radius: 12px 12px 0 0;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: flex-end;
  padding: 16px 16px 14px;
  color: #fff;
}

.course-cover-inner {
  position: relative;
  z-index: 1;
}

.course-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.course-semester {
  font-size: 13px;
  opacity: 0.85;
  margin: 4px 0 0 0;
}

.course-card-body {
  margin-bottom: 16px;
  padding-top: 10px;
}

.course-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.course-code-section {
  margin: 8px 0 0;
  padding: 8px 14px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2ff 100%);
  border: 1px dashed #c0c4cc;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.course-code-label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.course-code-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.course-code-value {
  font-size: 20px;
  color: #3b82f6;
  font-weight: 700;
  font-family: 'Courier New', monospace;
  letter-spacing: 3px;
}

.copy-btn {
  flex-shrink: 0;
}

.course-stats {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.stat-item {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.stat-label {
  color: #606266;
}

.stat-value {
  color: #303133;
  font-weight: 600;
  margin-left: 4px;
}

.course-card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .teacher-home-container {
    padding: 16px;
  }

  .course-card-actions {
    flex-direction: column;
  }

  .course-card-actions .el-button {
    width: 100%;
  }
}

/* 个人资料样式 */
.profile-details {
  padding: 20px;
}

.profile-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.profile-item:last-child {
  border-bottom: none;
}

.profile-item .label {
  font-weight: 600;
  color: #606266;
  min-width: 80px;
  margin-right: 12px;
}

.profile-item .value {
  color: #303133;
  flex: 1;
}

.profile-edit {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.email-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.email-separator {
  color: #909399;
  font-weight: 600;
}

.phone-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
