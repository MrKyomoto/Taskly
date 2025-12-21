<template>
  <div class="admin-dashboard" :style="{ backgroundColor: personalizationStore.backgroundColor }">
    <el-header class="header" :style="headerStyle">
      <div class="header-content">
        <h1 class="header-title">系统管理控制台</h1>
        <el-button :icon="Setting" @click="showPersonalization = true" circle />
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
                  <div>
                    <el-button type="primary" size="small" @click="showCreateStudentDialog = true">
                      <el-icon><Plus /></el-icon>
                      添加学生
                    </el-button>
                    <el-button type="default" size="small" @click="refreshStudents" style="margin-left: 8px;">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                  </div>
                </div>
              </template>
              <el-table :data="students" style="width: 100%" v-loading="studentsLoading" stripe>
                <el-table-column prop="student_no" label="学号" width="150" align="center" />
                <el-table-column prop="name" label="姓名" width="120" align="center" />
                <el-table-column prop="email" label="邮箱" min-width="200" align="center" />
                <el-table-column prop="phone" label="电话" width="150" align="center" />
                <el-table-column prop="create_time" label="注册时间" width="180">
                  <template #default="{ row }">
                    {{ formatDateTime(row.create_time) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="250" fixed="right">
                  <template #default="{ row }">
                    <el-button 
                      type="primary" 
                      size="small" 
                      link
                      @click="handleEditStudent(row)"
                    >
                      编辑
                    </el-button>
                    <el-button 
                      type="warning" 
                      size="small" 
                      link
                      @click="handleResetPassword('student', row.id)"
                    >
                      重置密码
                    </el-button>
                    <el-button 
                      type="danger" 
                      size="small" 
                      link
                      @click="handleDeleteUser('student', row.id)"
                    >
                      删除
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
              <el-table :data="staffList" style="width: 100%" v-loading="staffLoading" stripe>
                <el-table-column prop="staff_no" label="工号" width="150" align="center" />
                <el-table-column prop="name" label="姓名" width="120" align="center" />
                <el-table-column prop="role" label="角色" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag :type="row.role === 'teacher' ? 'success' : 'info'" size="small">
                      {{ row.role === 'teacher' ? '教师' : '助教' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="email" label="邮箱" min-width="200" align="center" />
                <el-table-column prop="phone" label="电话" width="150" align="center" />
                <el-table-column prop="create_time" label="注册时间" width="180" align="center">
                  <template #default="{ row }">
                    {{ formatDateTime(row.create_time) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="250" fixed="right" align="center">
                  <template #default="{ row }">
                    <el-button 
                      type="primary" 
                      size="small" 
                      link
                      @click="handleEditStaff(row)"
                    >
                      编辑
                    </el-button>
                    <el-button 
                      type="warning" 
                      size="small" 
                      link
                      @click="handleResetPassword('staff', row.id)"
                    >
                      重置密码
                    </el-button>
                    <el-button 
                      type="danger" 
                      size="small" 
                      link
                      @click="handleDeleteUser('staff', row.id)"
                    >
                      删除
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
                  <div>
                    <el-button type="primary" size="small" @click="showCreateCourseDialog = true">
                      <el-icon><Plus /></el-icon>
                      添加课程
                    </el-button>
                    <el-button type="default" size="small" @click="refreshCourses" style="margin-left: 8px;">
                    <el-icon><Refresh /></el-icon>
                    刷新
                  </el-button>
                  </div>
                </div>
              </template>
              <el-table :data="courses" style="width: 100%" v-loading="coursesLoading" stripe>
                <el-table-column prop="course_code" label="课程代码" width="150" align="center" />
                <el-table-column prop="course_name" label="课程名称" min-width="200" align="center" />
                <el-table-column prop="semester" label="学期" width="120" align="center" />
                <el-table-column prop="status" label="状态" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small">
                      {{ getStatusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="create_time" label="创建时间" width="180" align="center">
                  <template #default="{ row }">
                    {{ formatDateTime(row.create_time) }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="400" fixed="right" align="center">
                  <template #default="{ row }">
                    <el-button 
                      type="primary" 
                      size="small" 
                      link
                      @click="handleEditCourse(row)"
                    >
                      编辑
                    </el-button>
                    <el-button 
                      type="info" 
                      size="small" 
                      link
                      @click="handleManageCourseMembers(row)"
                    >
                      管理成员
                    </el-button>
                    <el-button 
                      v-if="row.status === 'pending'"
                      type="success" 
                      size="small" 
                      link
                      @click="handleApproveCourse(row.id, true)"
                    >
                      通过
                    </el-button>
                    <el-button 
                      v-if="row.status === 'pending'"
                      type="danger" 
                      size="small" 
                      link
                      @click="handleApproveCourse(row.id, false)"
                    >
                      驳回
                    </el-button>
                    <el-button 
                      v-if="row.status === 'approved'"
                      type="warning" 
                      size="small" 
                      link
                      @click="handleCloseCourse(row.id)"
                    >
                      结课
                    </el-button>
                    <el-button 
                      type="danger" 
                      size="small" 
                      link
                      @click="handleDeleteCourse(row.id)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!courses.length && !coursesLoading" description="暂无课程" :image-size="100" />
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </template>
    </div>

    <!-- 课程成员管理对话框 -->
    <el-dialog v-model="showCourseMembersDialog" title="课程成员管理" width="800px">
      <el-tabs v-model="memberTab" v-if="currentCourse">
        <el-tab-pane label="添加教师" name="add-teacher">
          <el-form :model="addTeacherForm" :rules="addMemberRules" ref="addTeacherFormRef" label-width="100px">
            <el-form-item label="课程信息">
              <div>
                <el-tag>{{ currentCourse.course_name }}</el-tag>
                <el-tag type="info" style="margin-left: 8px;">{{ currentCourse.semester }}</el-tag>
              </div>
            </el-form-item>
            <el-form-item label="教师工号" prop="staff_no">
              <el-input
                v-model="addTeacherForm.staff_no"
                placeholder="请输入教师工号"
                @keyup.enter="handleAddTeacherToCourse"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleAddTeacherToCourse" :loading="addingTeacher">
                添加教师
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="添加助教" name="add-ta">
          <el-form :model="addTAForm" :rules="addMemberRules" ref="addTAFormRef" label-width="100px">
            <el-form-item label="课程信息">
              <div>
                <el-tag>{{ currentCourse.course_name }}</el-tag>
                <el-tag type="info" style="margin-left: 8px;">{{ currentCourse.semester }}</el-tag>
              </div>
            </el-form-item>
            <el-form-item label="学生学号" prop="student_no">
              <el-input
                v-model="addTAForm.student_no"
                placeholder="请输入学生学号（助教从学生中选择）"
                @keyup.enter="handleAddTAToCourse"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleAddTAToCourse" :loading="addingTA">
                添加助教
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="添加学生" name="add-student">
          <el-form :model="addStudentForm" :rules="addMemberRules" ref="addStudentFormRef" label-width="100px">
            <el-form-item label="课程信息">
              <div>
                <el-tag>{{ currentCourse.course_name }}</el-tag>
                <el-tag type="info" style="margin-left: 8px;">{{ currentCourse.semester }}</el-tag>
              </div>
            </el-form-item>
            <el-form-item label="学生学号" prop="student_no">
              <el-input
                v-model="addStudentForm.student_no"
                placeholder="请输入学生学号"
                @keyup.enter="handleAddStudentToCourse"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleAddStudentToCourse" :loading="addingStudent">
                添加学生
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

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
        <el-form-item>
          <el-text type="info" size="small">新增的教职工默认为教师角色，初始密码：123456</el-text>
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

    <!-- 添加学生对话框 -->
    <el-dialog v-model="showCreateStudentDialog" title="添加学生" width="500px" @close="handleCloseStudentDialog">
      <el-form :model="createStudentForm" :rules="createStudentRules" ref="createStudentFormRef" label-width="100px">
        <el-form-item label="学号" prop="student_no">
          <el-input
            v-model="createStudentForm.student_no"
            placeholder="请输入学号"
            @keyup.enter="handleCreateStudent"
          />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="createStudentForm.name"
            placeholder="请输入姓名"
            @keyup.enter="handleCreateStudent"
          />
        </el-form-item>
        <el-form-item>
          <el-text type="info" size="small">初始密码默认为：123456</el-text>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input
            v-model="createStudentForm.email"
            placeholder="请输入邮箱（可选）"
            @keyup.enter="handleCreateStudent"
          />
        </el-form-item>
        <el-form-item label="电话">
          <el-input
            v-model="createStudentForm.phone"
            placeholder="请输入电话（可选）"
            @keyup.enter="handleCreateStudent"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateStudentDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateStudent" :loading="creatingStudent">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑学生对话框 -->
    <el-dialog v-model="showEditStudentDialog" title="编辑学生" width="500px" @close="handleCloseEditStudentDialog">
      <el-form :model="editStudentForm" :rules="editStudentRules" ref="editStudentFormRef" label-width="100px">
        <el-form-item label="学号">
          <el-input
            v-model="editStudentForm.student_no"
            disabled
          />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="editStudentForm.name"
            placeholder="请输入姓名"
            @keyup.enter="handleUpdateStudent"
          />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input
            v-model="editStudentForm.email"
            placeholder="请输入邮箱（可选）"
            @keyup.enter="handleUpdateStudent"
          />
        </el-form-item>
        <el-form-item label="电话">
          <el-input
            v-model="editStudentForm.phone"
            placeholder="请输入电话（可选）"
            @keyup.enter="handleUpdateStudent"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditStudentDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateStudent" :loading="updatingStudent">更新</el-button>
      </template>
    </el-dialog>

    <!-- 编辑教职工对话框 -->
    <el-dialog v-model="showEditStaffDialog" title="编辑教职工" width="500px" @close="handleCloseEditStaffDialog">
      <el-form :model="editStaffForm" :rules="editStaffRules" ref="editStaffFormRef" label-width="100px">
        <el-form-item label="工号">
          <el-input
            v-model="editStaffForm.staff_no"
            disabled
          />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="editStaffForm.name"
            placeholder="请输入姓名"
            @keyup.enter="handleUpdateStaff"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-input
            :value="editStaffForm.role === 'teacher' ? '教师' : '助教'"
            disabled
          />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input
            v-model="editStaffForm.email"
            placeholder="请输入邮箱（可选）"
            @keyup.enter="handleUpdateStaff"
          />
        </el-form-item>
        <el-form-item label="电话">
          <el-input
            v-model="editStaffForm.phone"
            placeholder="请输入电话（可选）"
            @keyup.enter="handleUpdateStaff"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditStaffDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateStaff" :loading="updatingStaff">更新</el-button>
      </template>
    </el-dialog>

    <!-- 添加课程对话框 -->
    <el-dialog 
      v-model="showCreateCourseDialog" 
      title="新增教学课程" 
      width="500px"
      @closed="handleCloseCreateCourseDialog"
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
        <el-form-item label="课程号" prop="course_code">
          <el-input
            v-model="createCourseForm.course_code"
            placeholder="请输入课程号"
            @keyup.enter="handleCreateCourse"
            maxlength="20"
            show-word-limit
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

    <!-- 编辑课程对话框 -->
    <el-dialog v-model="showEditCourseDialog" title="编辑课程" width="500px" @close="handleCloseEditCourseDialog">
      <el-form :model="editCourseForm" :rules="editCourseRules" ref="editCourseFormRef" label-width="100px">
        <el-form-item label="课程代码">
          <el-input
            v-model="editCourseForm.course_code"
            disabled
          />
        </el-form-item>
        <el-form-item label="课程名称" prop="course_name">
          <el-input
            v-model="editCourseForm.course_name"
            placeholder="请输入课程名称"
            @keyup.enter="handleUpdateCourse"
          />
        </el-form-item>
        <el-form-item label="学期" prop="semester">
          <div class="semester-select-group">
            <el-input-number
              v-model="editCourseForm.semesterYear"
              :min="2000"
              :max="2100"
              :precision="0"
              controls-position="right"
              style="width: 140px; margin-right: 8px;"
            />
            <el-select
              v-model="editCourseForm.semesterTerm"
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
            v-model="editCourseForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入课程描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditCourseDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateCourse" :loading="updatingCourse">更新</el-button>
      </template>
    </el-dialog>

    <!-- 个性化设置面板 -->
    <PersonalizationPanel v-model="showPersonalization" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { ArrowDown, Plus, Refresh, Setting } from '@element-plus/icons-vue';
import { usePersonalizationStore } from '@/store/personalization';
import PersonalizationPanel from '@/components/PersonalizationPanel.vue';
import { useUserStore } from '@/store/user';
import { formatDateTime as formatDateUtil } from '@/utils/date-formatter';
import { logger } from '@/utils/logger';
import { getCurrentSemester } from '@/utils/semester';
import { 
  fetchAllStudents, 
  fetchAllStaff, 
  fetchAllCourses, 
  createStaff, 
  createStudent,
  updateStudent,
  updateStaff,
  createCourse,
  updateCourse,
  deleteCourse,
  closeCourse,
  approveCourse,
  resetUserPassword,
  deleteUser,
  addTeacherToCourse,
  addTAToCourse,
  addStudentToCourse
} from '@/api/admin';

const router = useRouter();
const userStore = useUserStore();
const personalizationStore = usePersonalizationStore();

const loading = ref(false);
const showPersonalization = ref(false);
const profile = ref(null);

// 个性化样式
const headerStyle = computed(() => {
  const module = personalizationStore.modules.header;
  return {
    backgroundColor: module.backgroundColor,
    color: module.textColor,
  };
});
const activeTab = ref('staff');

// 学生管理
const students = ref([]);
const studentsLoading = ref(false);
const showCreateStudentDialog = ref(false);
const creatingStudent = ref(false);
const createStudentForm = ref({
  student_no: '',
  name: '',
  email: '',
  phone: '',
});
const createStudentFormRef = ref(null);
const createStudentRules = {
  student_no: [{ required: true, message: '请输入学号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
};

// 编辑学生
const showEditStudentDialog = ref(false);
const updatingStudent = ref(false);
const editStudentForm = ref({
  id: null,
  student_no: '',
  name: '',
  email: '',
  phone: '',
});
const editStudentFormRef = ref(null);
const editStudentRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
};

// 教职工管理
const staffList = ref([]);
const staffLoading = ref(false);
const showCreateStaffDialog = ref(false);
const creatingStaff = ref(false);
const createStaffForm = ref({
  staff_no: '',
  name: '',
  email: '',
  phone: '',
});
const createStaffFormRef = ref(null);
const createStaffRules = {
  staff_no: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
};

// 编辑教职工
const showEditStaffDialog = ref(false);
const updatingStaff = ref(false);
const editStaffForm = ref({
  id: null,
  staff_no: '',
  name: '',
  role: '',
  email: '',
  phone: '',
});
const editStaffFormRef = ref(null);
const editStaffRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
};

// 课程概览
const courses = ref([]);
const coursesLoading = ref(false);
const showCreateCourseDialog = ref(false);
const creatingCourse = ref(false);
// 获取当前学期信息
const currentSemesterInfo = getCurrentSemester();
const currentYear = currentSemesterInfo.year;
const createCourseForm = ref({
  course_name: '',
  course_code: '',
  semesterYear: currentSemesterInfo.year,
  semesterTerm: currentSemesterInfo.term,
  semester: '',
  description: '',
});
const createCourseFormRef = ref(null);
const createCourseRules = {
  course_name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  course_code: [
    { required: true, message: '请输入课程号', trigger: 'blur' },
    { min: 1, max: 20, message: '课程号长度应在1-20个字符之间', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: '课程号只能包含字母、数字、下划线和连字符', trigger: 'blur' },
  ],
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

// 编辑课程
const showEditCourseDialog = ref(false);
const updatingCourse = ref(false);
const editCourseForm = ref({
  id: null,
  course_code: '',
  course_name: '',
  semesterYear: currentSemesterInfo.year,
  semesterTerm: currentSemesterInfo.term,
  semester: '',
  description: '',
});
const editCourseFormRef = ref(null);
const editCourseRules = {
  course_name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  semester: [
    {
      validator: (_rule, _value, callback) => {
        const { semesterYear, semesterTerm } = editCourseForm.value;
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

// 根据年份和学期拼接最终学期字符串（编辑课程用）
const updateEditSemesterString = () => {
  const { semesterYear, semesterTerm } = editCourseForm.value;
  if (!semesterYear || !semesterTerm) {
    editCourseForm.value.semester = '';
  } else {
    editCourseForm.value.semester = `${semesterYear}-${semesterTerm}`;
  }
};

// 从学期字符串解析年份和学期（格式：2024-Fall）
const parseSemester = (semesterStr) => {
  if (!semesterStr) {
    return { year: currentYear, term: 'Fall' };
  }
  const match = semesterStr.match(/^(\d{4})-(Spring|Summer|Fall)$/);
  if (match) {
    return { year: parseInt(match[1]), term: match[2] };
  }
  // 如果格式不匹配，返回默认值
  return { year: currentYear, term: 'Fall' };
};

watch(
  () => [editCourseForm.value.semesterYear, editCourseForm.value.semesterTerm],
  () => {
    updateEditSemesterString();
  },
  { immediate: true }
);

// 课程成员管理
const showCourseMembersDialog = ref(false);
const currentCourse = ref(null);
const memberTab = ref('add-teacher');
const addingTeacher = ref(false);
const addingTA = ref(false);
const addingStudent = ref(false);
const addTeacherForm = ref({ staff_no: '' });
const addTAForm = ref({ student_no: '' });
const addStudentForm = ref({ student_no: '' });
const addTeacherFormRef = ref(null);
const addTAFormRef = ref(null);
const addStudentFormRef = ref(null);
const addMemberRules = {
  staff_no: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  student_no: [{ required: true, message: '请输入学号', trigger: 'blur' }],
};

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
  return formatDateUtil(dateString, 'YYYY-MM-DD HH:mm');
};

// 获取课程状态标签
const getStatusType = (status) => {
  const statusMap = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger',
    'closed': 'info',
  };
  return statusMap[status] || 'info';
};

const getStatusLabel = (status) => {
  const labelMap = {
    'pending': '待审核',
    'approved': '已通过',
    'rejected': '已驳回',
    'closed': '已结课',
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
      // 不传密码，后端会使用默认密码123456
      // 新增的教职工默认为教师角色
      const staffData = {
        ...createStaffForm.value,
        role: 'teacher', // 固定为教师角色
      };
      await createStaff(staffData);
      ElMessage.success('教职工创建成功（教师角色），初始密码：123456');
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
    // 表单验证失败，已在validate中显示错误信息
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

// 创建学生
const handleCreateStudent = async () => {
  if (!createStudentFormRef.value) return;
  
  try {
    await createStudentFormRef.value.validate();
    creatingStudent.value = true;
    
    try {
      // 不传密码，后端会使用默认密码123456
      await createStudent(createStudentForm.value);
      ElMessage.success('学生创建成功，初始密码：123456');
      showCreateStudentDialog.value = false;
      createStudentFormRef.value.resetFields();
      fetchStudents();
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
      creatingStudent.value = false;
    }
  } catch (error) {
    // 表单验证失败，已在validate中显示错误信息
  }
};

// 编辑学生
const handleEditStudent = (student) => {
  editStudentForm.value = {
    id: student.id,
    student_no: student.student_no,
    name: student.name,
    email: student.email || '',
    phone: student.phone || '',
  };
  showEditStudentDialog.value = true;
};

// 更新学生
const handleUpdateStudent = async () => {
  if (!editStudentFormRef.value) return;
  
  try {
    await editStudentFormRef.value.validate();
    updatingStudent.value = true;
    
    try {
      await updateStudent(editStudentForm.value.id, {
        name: editStudentForm.value.name,
        email: editStudentForm.value.email,
        phone: editStudentForm.value.phone,
      });
      ElMessage.success('学生信息更新成功');
      showEditStudentDialog.value = false;
      fetchStudents();
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
      updatingStudent.value = false;
    }
  } catch (error) {
    // 表单验证失败，已在validate中显示错误信息
  }
};

// 关闭学生对话框
const handleCloseStudentDialog = () => {
  createStudentForm.value = {
    student_no: '',
    name: '',
    email: '',
    phone: '',
  };
  createStudentFormRef.value?.resetFields();
};

const handleCloseEditStudentDialog = () => {
  editStudentForm.value = {
    id: null,
    student_no: '',
    name: '',
    email: '',
    phone: '',
  };
  editStudentFormRef.value?.resetFields();
};

// 编辑教职工
const handleEditStaff = (staff) => {
  editStaffForm.value = {
    id: staff.id,
    staff_no: staff.staff_no,
    name: staff.name,
    role: staff.role,
    email: staff.email || '',
    phone: staff.phone || '',
  };
  showEditStaffDialog.value = true;
};

// 更新教职工
const handleUpdateStaff = async () => {
  if (!editStaffFormRef.value) return;
  
  try {
    await editStaffFormRef.value.validate();
    updatingStaff.value = true;
    
    try {
      await updateStaff(editStaffForm.value.id, {
        name: editStaffForm.value.name,
        email: editStaffForm.value.email,
        phone: editStaffForm.value.phone,
      });
      ElMessage.success('教职工信息更新成功');
      showEditStaffDialog.value = false;
      fetchStaff();
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
      updatingStaff.value = false;
    }
  } catch (error) {
    // 表单验证失败，已在validate中显示错误信息
  }
};

const handleCloseStaffDialog = () => {
  createStaffForm.value = {
    staff_no: '',
    name: '',
    email: '',
    phone: '',
  };
  createStaffFormRef.value?.resetFields();
};

const handleCloseEditStaffDialog = () => {
  editStaffForm.value = {
    id: null,
    staff_no: '',
    name: '',
    role: '',
    email: '',
    phone: '',
  };
  editStaffFormRef.value?.resetFields();
};

// 创建课程
const handleCreateCourse = async () => {
  if (!createCourseFormRef.value) return;
  try {
    await createCourseFormRef.value.validate();
    creatingCourse.value = true;
    // 确保学期字符串已更新
    updateSemesterString();
    const payload = {
      course_name: createCourseForm.value.course_name,
      course_code: createCourseForm.value.course_code.trim(),
      semester: createCourseForm.value.semester,
      description: createCourseForm.value.description,
    };
    const response = await createCourse(payload);
    const courseCode = response.data?.course?.course_code;
    
    // 显示创建成功并高亮课程号
    showCreateCourseDialog.value = false;
    createCourseForm.value = {
      course_name: '',
      course_code: '',
  semesterYear: currentSemesterInfo.year,
  semesterTerm: currentSemesterInfo.term,
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
      // 复制课程号到剪贴板
      if (navigator.clipboard) {
        navigator.clipboard.writeText(courseCode).then(() => {
          ElMessage.success('课程号已复制到剪贴板');
        });
      }
    });
    
    await fetchCourses();
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

// 编辑课程
const handleEditCourse = (course) => {
  const { year, term } = parseSemester(course.semester);
  editCourseForm.value = {
    id: course.id,
    course_code: course.course_code,
    course_name: course.course_name,
    semesterYear: year,
    semesterTerm: term,
    semester: course.semester || '',
    description: course.description || '',
  };
  updateEditSemesterString();
  showEditCourseDialog.value = true;
};

// 更新课程
const handleUpdateCourse = async () => {
  if (!editCourseFormRef.value) return;
  
  try {
    await editCourseFormRef.value.validate();
    updatingCourse.value = true;
    // 确保学期字符串已更新
    updateEditSemesterString();
    
    try {
      await updateCourse(editCourseForm.value.id, {
        course_name: editCourseForm.value.course_name,
        semester: editCourseForm.value.semester,
        description: editCourseForm.value.description,
      });
      ElMessage.success('课程信息更新成功');
      showEditCourseDialog.value = false;
      fetchCourses();
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
      updatingCourse.value = false;
    }
  } catch (error) {
    // 表单验证失败，已在validate中显示错误信息
  }
};

const handleCloseCreateCourseDialog = () => {
  createCourseForm.value = {
    course_name: '',
    course_code: '',
  semesterYear: currentSemesterInfo.year,
  semesterTerm: currentSemesterInfo.term,
    semester: '',
    description: '',
  };
  createCourseFormRef.value?.resetFields();
  updateSemesterString();
};

const handleCloseEditCourseDialog = () => {
  editCourseForm.value = {
    id: null,
    course_code: '',
    course_name: '',
  semesterYear: currentSemesterInfo.year,
  semesterTerm: currentSemesterInfo.term,
    semester: '',
    description: '',
  };
  editCourseFormRef.value?.resetFields();
  updateEditSemesterString();
};

// 管理课程成员
const handleManageCourseMembers = (course) => {
  currentCourse.value = course;
  memberTab.value = 'add-teacher';
  addTeacherForm.value = { staff_no: '' };
  addTAForm.value = { student_no: '' };
  addStudentForm.value = { student_no: '' };
  showCourseMembersDialog.value = true;
};

// 添加教师到课程
const handleAddTeacherToCourse = async () => {
  if (!addTeacherFormRef.value || !currentCourse.value) return;
  
  try {
    await addTeacherFormRef.value.validate();
    addingTeacher.value = true;
    
    try {
      await addTeacherToCourse(currentCourse.value.id, {
        staff_no: addTeacherForm.value.staff_no,
      });
      ElMessage.success('教师添加成功');
      addTeacherForm.value = { staff_no: '' };
      addTeacherFormRef.value.resetFields();
    } catch (error) {
      const status = error?.response?.status;
      if (status === 400) {
        ElMessage.error(error?.response?.data?.error || '添加失败，请检查输入');
      } else if (status === 401) {
        ElMessage.error('登录已过期，请重新登录');
        userStore.logout();
        router.push({ name: 'Login' });
      } else {
        ElMessage.error(error?.response?.data?.error || '添加失败，请重试');
      }
    } finally {
      addingTeacher.value = false;
    }
  } catch (error) {
    // 表单验证失败
  }
};

// 添加助教到课程
const handleAddTAToCourse = async () => {
  if (!addTAFormRef.value || !currentCourse.value) return;
  
  try {
    await addTAFormRef.value.validate();
    addingTA.value = true;
    
    try {
      await addTAToCourse(currentCourse.value.id, {
        student_no: addTAForm.value.student_no,
      });
      ElMessage.success('助教添加成功');
      addTAForm.value = { student_no: '' };
      addTAFormRef.value.resetFields();
    } catch (error) {
      const status = error?.response?.status;
      if (status === 400) {
        ElMessage.error(error?.response?.data?.error || '添加失败，请检查输入');
      } else if (status === 401) {
        ElMessage.error('登录已过期，请重新登录');
        userStore.logout();
        router.push({ name: 'Login' });
      } else {
        ElMessage.error(error?.response?.data?.error || '添加失败，请重试');
      }
    } finally {
      addingTA.value = false;
    }
  } catch (error) {
    // 表单验证失败
  }
};

// 添加学生到课程
const handleAddStudentToCourse = async () => {
  if (!addStudentFormRef.value || !currentCourse.value) return;
  
  try {
    await addStudentFormRef.value.validate();
    addingStudent.value = true;
    
    try {
      await addStudentToCourse(currentCourse.value.id, {
        student_no: addStudentForm.value.student_no,
      });
      ElMessage.success('学生添加成功');
      addStudentForm.value = { student_no: '' };
      addStudentFormRef.value.resetFields();
    } catch (error) {
      const status = error?.response?.status;
      if (status === 400) {
        ElMessage.error(error?.response?.data?.error || '添加失败，请检查输入');
      } else if (status === 401) {
        ElMessage.error('登录已过期，请重新登录');
        userStore.logout();
        router.push({ name: 'Login' });
      } else {
        ElMessage.error(error?.response?.data?.error || '添加失败，请重试');
      }
    } finally {
      addingStudent.value = false;
    }
  } catch (error) {
    // 表单验证失败
  }
};

// 审核课程
const handleApproveCourse = async (courseId, approve) => {
  try {
    await ElMessageBox.confirm(
      `确定要${approve ? '通过' : '驳回'}该课程吗？`,
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    try {
      await approveCourse(courseId, approve);
      ElMessage.success(`课程已${approve ? '通过' : '驳回'}审核`);
      fetchCourses();
    } catch (error) {
      const status = error?.response?.status;
      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录');
        userStore.logout();
        router.push({ name: 'Login' });
      } else {
        ElMessage.error(error?.response?.data?.error || '操作失败');
      }
    }
  } catch (error) {
    // 用户取消
  }
};

// 课程结课
const handleCloseCourse = async (courseId) => {
  try {
    await ElMessageBox.confirm(
      '确定要结课该课程吗？结课后该课程将不再接受新的作业提交。',
      '确认结课',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    try {
      await closeCourse(courseId);
      ElMessage.success('课程已结课');
      fetchCourses();
    } catch (error) {
      const status = error?.response?.status;
      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录');
        userStore.logout();
        router.push({ name: 'Login' });
      } else {
        ElMessage.error(error?.response?.data?.error || '结课失败');
      }
    }
  } catch (error) {
    // 用户取消
  }
};

// 删除课程
const handleDeleteCourse = async (courseId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该课程吗？删除后将无法恢复，所有相关数据将被删除。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    try {
      await deleteCourse(courseId);
      ElMessage.success('课程已删除');
      fetchCourses();
    } catch (error) {
      const status = error?.response?.status;
      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录');
        userStore.logout();
        router.push({ name: 'Login' });
      } else {
        ElMessage.error(error?.response?.data?.error || '删除失败');
      }
    }
  } catch (error) {
    // 用户取消
  }
};

// 删除用户
const handleDeleteUser = async (userType, userId) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除该${userType === 'staff' ? '教职工' : '学生'}吗？删除后将无法恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    try {
      await deleteUser(userType === 'staff' ? 'teacher' : 'student', userId);
      ElMessage.success('删除成功');
      if (userType === 'staff') {
        fetchStaff();
      } else {
        fetchStudents();
      }
    } catch (error) {
      const status = error?.response?.status;
      if (status === 401) {
        ElMessage.error('登录已过期，请重新登录');
        userStore.logout();
        router.push({ name: 'Login' });
      } else {
        ElMessage.error(error?.response?.data?.error || '删除失败');
      }
    }
  } catch (error) {
    // 用户取消
  }
};

onMounted(() => {
  profile.value = userStore.user;
  // 加载当前用户的个性化设置
  personalizationStore.loadUserSettings();
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
