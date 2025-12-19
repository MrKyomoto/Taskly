<template>
  <div class="admin-dashboard">
    <el-header class="header">
      <div class="header-content">
        <h1 class="header-title">系统管理控制台</h1>
        <el-dropdown @command="handleCommand">
          <span class="dropdown-trigger">
            {{ profile?.name || '管理员' }}
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
    </el-header>

    <div class="admin-dashboard-container">
      <el-skeleton v-if="loading" animated :count="3" />
      <template v-else>
        <el-tabs v-model="activeTab" class="admin-tabs">
          <!-- 学生管理 -->
          <el-tab-pane label="学生管理" name="students">
            <el-card shadow="never">
              <template #header>
                <div class="card-header">
                  <span class="card-title">学生列表</span>
                  <el-button type="primary" size="small" @click="refreshStudents">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </template>
              <el-table :data="students" style="width: 100%" v-loading="studentsLoading">
                <el-table-column prop="student_no" label="学号" width="150" />
                <el-table-column prop="name" label="姓名" width="120" />
                <el-table-column prop="email" label="邮箱" min-width="200" />
                <el-table-column prop="phone" label="电话" width="150" />
                <el-table-column prop="create_time" label="注册时间" width="180">
                  <template #default="{ row }">
                    {{ formatDateTime(row.create_time) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{ row }">
                    <el-button 
                      type="warning" 
                      size="small" 
                      link
                      @click="handleResetPassword('student', row.id)"
                    >
                      重置密码
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!students.length && !studentsLoading" description="暂无学生" :image-size="100" />
            </el-card>
          </el-tab-pane>

          <!-- 教职工管理 -->
          <el-tab-pane label="教职工管理" name="staff">
            <el-card shadow="never">
              <template #header>
                <div class="card-header">
                  <span class="card-title">教职工列表</span>
                  <div>
                    <el-button type="primary" size="small" @click="showCreateStaffDialog = true">
                      <el-icon><Plus /></el-icon>
                      添加教职工
                    </el-button>
                    <el-button type="default" size="small" @click="refreshStaff" style="margin-left: 8px;">
                      <el-icon><Refresh /></el-icon>
                      刷新
                    </el-button>
                  </div>
                </div>
              </template>
              <el-table :data="staffList" style="width: 100%" v-loading="staffLoading">
                <el-table-column prop="staff_no" label="工号" width="150" />
                <el-table-column prop="name" label="姓名" width="120" />
                <el-table-column prop="role" label="角色" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.role === 'teacher' ? 'success' : 'info'" size="small">
                      {{ row.role === 'teacher' ? '教师' : '助教' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="email" label="邮箱" min-width="200" />
                <el-table-column prop="phone" label="电话" width="150" />
                <el-table-column prop="create_time" label="注册时间" width="180">
                  <template #default="{ row }">
                    {{ formatDateTime(row.create_time) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{ row }">
                    <el-button 
                      type="warning" 
                      size="small" 
                      link
                      @click="handleResetPassword('staff', row.id)"
                    >
                      重置密码
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!staffList.length && !staffLoading" description="暂无教职工" :image-size="100" />
            </el-card>
          </el-tab-pane>

          <!-- 课程概览 -->
          <el-tab-pane label="课程概览" name="courses">
            <el-card shadow="never">
              <template #header>
                <div class="card-header">
                  <span class="card-title">课程列表</span>
                  <el-button type="default" size="small" @click="refreshCourses">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                </div>
              </template>
              <el-table :data="courses" style="width: 100%" v-loading="coursesLoading">
                <el-table-column prop="course_code" label="课程代码" width="150" />
                <el-table-column prop="course_name" label="课程名称" min-width="200" />
                <el-table-column prop="semester" label="学期" width="120" />
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small">
                      {{ getStatusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="create_time" label="创建时间" width="180">
                  <template #default="{ row }">
                    {{ formatDateTime(row.create_time) }}
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!courses.length && !coursesLoading" description="暂无课程" :image-size="100" />
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </template>
    </div>

    <!-- 添加教职工对话框 -->
    <el-dialog v-model="showCreateStaffDialog" title="添加教职工" width="500px">
      <el-form :model="createStaffForm" :rules="createStaffRules" ref="createStaffFormRef" label-width="100px">
        <el-form-item label="工号" prop="staff_no">
          <el-input
            v-model="createStaffForm.staff_no"
            placeholder="请输入工号"
            @keyup.enter="handleCreateStaff"
          />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="createStaffForm.name"
            placeholder="请输入姓名"
            @keyup.enter="handleCreateStaff"
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="createStaffForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="教师" value="teacher" />
            <el-option label="助教" value="ta" />
          </el-select>
        </el-form-item>
        <el-form-item label="初始密码" prop="password">
          <el-input
            v-model="createStaffForm.password"
            type="password"
            placeholder="请输入初始密码（至少6位）"
            show-password
            @keyup.enter="handleCreateStaff"
          />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input
            v-model="createStaffForm.email"
            placeholder="请输入邮箱（可选）"
            @keyup.enter="handleCreateStaff"
          />
        </el-form-item>
        <el-form-item label="电话">
          <el-input
            v-model="createStaffForm.phone"
            placeholder="请输入电话（可选）"
            @keyup.enter="handleCreateStaff"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateStaffDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateStaff" :loading="creatingStaff">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { ArrowDown, Plus, Refresh } from '@element-plus/icons-vue';
import { useUserStore } from '@/store/user';
import { fetchAllStudents, fetchAllStaff, fetchAllCourses, createStaff, resetUserPassword } from '@/api/admin';

const router = useRouter();
const userStore = useUserStore();

const loading = ref(false);
const profile = ref(null);
const activeTab = ref('staff');

// 学生管理
const students = ref([]);
const studentsLoading = ref(false);

// 教职工管理
const staffList = ref([]);
const staffLoading = ref(false);
const showCreateStaffDialog = ref(false);
const creatingStaff = ref(false);
const createStaffForm = ref({
  staff_no: '',
  name: '',
  role: 'teacher',
  password: '',
  email: '',
  phone: '',
});
const createStaffFormRef = ref(null);
const createStaffRules = {
  staff_no: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [
    { required: true, message: '请输入初始密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
};

// 课程概览
const courses = ref([]);
const coursesLoading = ref(false);

// 处理下拉菜单命令
const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout();
    router.push({ name: 'Login' });
  } else if (command === 'profile') {
    ElMessage.info('个人中心功能开发中');
  }
};

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// 获取课程状态标签
const getStatusType = (status) => {
  const statusMap = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger',
  };
  return statusMap[status] || 'info';
};

const getStatusLabel = (status) => {
  const labelMap = {
    'pending': '待审核',
    'approved': '已通过',
    'rejected': '已驳回',
  };
  return labelMap[status] || status;
};

// 获取学生列表
const fetchStudents = async () => {
  studentsLoading.value = true;
  try {
    const response = await fetchAllStudents();
    students.value = response.data?.student_list || [];
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else {
      ElMessage.error(error?.response?.data?.error || '获取学生列表失败');
    }
  } finally {
    studentsLoading.value = false;
  }
};

// 刷新学生列表
const refreshStudents = () => {
  fetchStudents();
};

// 获取教职工列表
const fetchStaff = async () => {
  staffLoading.value = true;
  try {
    const response = await fetchAllStaff();
    staffList.value = response.data?.staff_list || [];
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else {
      ElMessage.error(error?.response?.data?.error || '获取教职工列表失败');
    }
  } finally {
    staffLoading.value = false;
  }
};

// 刷新教职工列表
const refreshStaff = () => {
  fetchStaff();
};

// 获取课程列表
const fetchCourses = async () => {
  coursesLoading.value = true;
  try {
    const response = await fetchAllCourses();
    courses.value = response.data?.course_list || [];
  } catch (error) {
    const status = error?.response?.status;
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else {
      ElMessage.error(error?.response?.data?.error || '获取课程列表失败');
    }
  } finally {
    coursesLoading.value = false;
  }
};

// 刷新课程列表
const refreshCourses = () => {
  fetchCourses();
};

// 创建教职工
const handleCreateStaff = async () => {
  if (!createStaffFormRef.value) return;
  
  try {
    await createStaffFormRef.value.validate();
    
    creatingStaff.value = true;
    try {
      await createStaff(createStaffForm.value);
      ElMessage.success('教职工创建成功');
      showCreateStaffDialog.value = false;
      createStaffFormRef.value.resetFields();
      fetchStaff();
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
      creatingStaff.value = false;
    }
  } catch (error) {
    console.error('表单验证失败:', error);
  }
};

// 重置密码
const handleResetPassword = async (userType, userId) => {
  try {
    await ElMessageBox.confirm(
      `确定要将该${userType === 'staff' ? '教职工' : '学生'}的密码重置为 "123456" 吗？`,
      '确认重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    try {
      await resetUserPassword(userType, userId, { default_password: '123456' });
      ElMessage.success('密码已重置为：123456');
    } catch (error) {
      const status = error?.response?.status;
      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录');
        userStore.logout();
        router.push({ name: 'Login' });
      } else {
        ElMessage.error(error?.response?.data?.error || '重置密码失败');
      }
    }
  } catch (error) {
    // 用户取消
  }
};

onMounted(() => {
  profile.value = userStore.user;
  fetchStaff();
  fetchStudents();
  fetchCourses();
});
</script>

<style scoped>
.admin-dashboard {
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
}

.dropdown-trigger {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.admin-dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.admin-tabs {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
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

.dashboard-content {
  padding: 20px 0;
}
</style>
