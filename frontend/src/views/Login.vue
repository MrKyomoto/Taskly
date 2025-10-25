<template>
  <div class="login-container">
    <el-card class="login-card" body-style="padding: 0; display: flex;">
      <!-- 左侧欢迎区域 -->
      <div class="welcome-section">
        <h2>欢迎来到 Taskly</h2>
        <p>一个为师生设计的现代化任务管理平台。</p>
      </div>

      <!-- 右侧表单区域 -->
      <div class="form-section">
        <el-tabs v-model="activeTab" class="login-tabs">
          <!-- 学生标签页 -->
          <el-tab-pane label="学生" name="student">
            <h3 class="form-title">{{ isStudentRegister ? '学生注册' : '学生登录' }}</h3>
            <el-form ref="studentFormRef" :model="formData" :rules="rules" label-width="80px">
              <el-form-item label="学号" prop="student_no">
                <el-input v-model="formData.student_no" placeholder="请输入学号"></el-input>
              </el-form-item>
              <el-form-item v-if="isStudentRegister" label="姓名" prop="name">
                <el-input v-model="formData.name" placeholder="请输入姓名"></el-input>
              </el-form-item>
              <el-form-item label="密码" prop="password">
                <el-input v-model="formData.password" type="password" placeholder="请输入密码" show-password></el-input>
              </el-form-item>
              <el-form-item v-if="isStudentRegister" label="确认密码" prop="confirmPassword">
                <el-input v-model="formData.confirmPassword" type="password" placeholder="请再次输入密码" show-password></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleSubmit" class="submit-btn">{{ isStudentRegister ? '注册' : '登录' }}</el-button>
              </el-form-item>
            </el-form>
            <div class="switch-link">
              <el-link type="primary" @click="isStudentRegister = !isStudentRegister">
                {{ isStudentRegister ? '已有账号？去登录' : '没有账号？去注册' }}
              </el-link>
            </div>
          </el-tab-pane>

          <!-- 教师标签页 -->
          <el-tab-pane label="教师" name="teacher">
            <h3 class="form-title">{{ isTeacherRegister ? '教师注册' : '教师登录' }}</h3>
            <el-form ref="teacherFormRef" :model="formData" :rules="rules" label-width="80px">
              <el-form-item label="工号" prop="staff_no">
                <el-input v-model="formData.staff_no" placeholder="请输入工号"></el-input>
              </el-form-item>
              <el-form-item v-if="isTeacherRegister" label="姓名" prop="name">
                <el-input v-model="formData.name" placeholder="请输入姓名"></el-input>
              </el-form-item>
              <el-form-item label="密码" prop="password">
                <el-input v-model="formData.password" type="password" placeholder="请输入密码" show-password></el-input>
              </el-form-item>
              <el-form-item v-if="isTeacherRegister" label="确认密码" prop="confirmPassword">
                <el-input v-model="formData.confirmPassword" type="password" placeholder="请再次输入密码" show-password></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleSubmit" class="submit-btn">{{ isTeacherRegister ? '注册' : '登录' }}</el-button>
              </el-form-item>
            </el-form>
            <div class="switch-link">
              <el-link type="primary" @click="isTeacherRegister = !isTeacherRegister">
                {{ isTeacherRegister ? '已有账号？去登录' : '没有账号？去注册' }}
              </el-link>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue';
import { useUserStore } from '@/store/user';
import { ElMessage } from 'element-plus';

const userStore = useUserStore();
const studentFormRef = ref(null);
const teacherFormRef = ref(null);

const activeTab = ref('student'); // 'student' or 'teacher'
const isStudentRegister = ref(false);
const isTeacherRegister = ref(false);

const formData = reactive({
  student_no: '',
  staff_no: '',
  name: '',
  password: '',
  confirmPassword: '',
});

// 切换标签页或注册/登录模式时重置表单
watch([activeTab, isStudentRegister, isTeacherRegister], () => {
  studentFormRef.value?.resetFields();
  teacherFormRef.value?.resetFields();
  // 重置数据模型，但不包括在当前表单中可能仍然需要的字段
  Object.keys(formData).forEach(key => {
    formData[key] = '';
  });
});

const isRegister = computed(() => {
  return activeTab.value === 'student' ? isStudentRegister.value : isTeacherRegister.value;
});

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'));
  } else {
    if (isRegister.value && formData.confirmPassword !== '') {
      const formRef = activeTab.value === 'student' ? studentFormRef.value : teacherFormRef.value;
      formRef?.validateField('confirmPassword');
    }
    callback();
  }
};

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'));
  } else if (value !== formData.password) {
    callback(new Error("两次输入的密码不一致!"));
  } else {
    callback();
  }
};

const rules = computed(() => {
  const idProp = activeTab.value === 'student' ? 'student_no' : 'staff_no';
  const baseRules = {
    [idProp]: [{ required: true, message: activeTab.value === 'student' ? '请输入学号' : '请输入工号', trigger: 'blur' }],
    password: [{ required: true, validator: validatePass, trigger: 'blur' }],
  };
  if (isRegister.value) {
    return {
      ...baseRules,
      name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
      confirmPassword: [{ required: true, validator: validatePass2, trigger: 'blur' }],
    };
  }
  return baseRules;
});

const handleSubmit = () => {
  const formRef = activeTab.value === 'student' ? studentFormRef.value : teacherFormRef.value;
  formRef.validate(async (valid) => {
    if (valid) {
      const currentRole = activeTab.value;
      if (isRegister.value) {
        const payload = currentRole === 'student'
          ? { student_no: formData.student_no, name: formData.name, password: formData.password }
          : { staff_no: formData.staff_no, name: formData.name, password: formData.password };
        try {
          await userStore.register(payload, currentRole);
          ElMessage.success('注册成功，请登录');
          if (currentRole === 'student') isStudentRegister.value = false;
          else isTeacherRegister.value = false;
        } catch (error) {
          ElMessage.error(error.response?.data?.error || '注册失败');
        }
      } else {
        const payload = currentRole === 'student'
          ? { student_no: formData.student_no, password: formData.password }
          : { staff_no: formData.staff_no, password: formData.password };
        try {
          await userStore.login(payload, currentRole);
          ElMessage.success('登录成功');
        } catch (error) {
          ElMessage.error(error.response?.data?.error || '登录失败');
        }
      }
    } else {
      return false;
    }
  });
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 900px; /* 放大卡片 */
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.1);
}

.welcome-section {
  width: 50%; /* 调整左右比例，欢迎区略大 */
  background: linear-gradient(135deg, #409eff, #66b1ff);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  text-align: center;
}

.welcome-section h2 {
  font-size: 36px; /* 放大欢迎标题 */
  margin-bottom: 15px;
}

.welcome-section p {
  font-size: 18px; /* 放大副标题 */
}

/* 表单区宽度调整以匹配欢迎区 */
.form-section {
  width: 50%;
  padding: 20px 40px; /* 调整垂直内边距 */
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 放大 Tabs 标签（学生/教师）文字并增加内间距 */
::v-deep .login-tabs .el-tabs__header .el-tabs__item {
  font-size: 20px;
  padding: 10px 26px;
  min-width: 110px;
  justify-content: center;
}

/* 激活标签更醒目 */
::v-deep .login-tabs .el-tabs__header .el-tabs__item.is-active {
  font-weight: 700;
}

/* 表单内的大标题稍微放大 */
.form-title {
  text-align: center;
  margin-bottom: 20px;
  font-size: 22px;
  color: #303133;
}

.submit-btn {
  width: 100%;
}

.switch-link {
  text-align: center;
  margin-top: 10px;
}
</style>