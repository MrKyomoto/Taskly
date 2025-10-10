<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>{{ isRegister ? '注册' : '登录' }}</span>
        </div>
      </template>
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="80px">
        <el-form-item label="学号" prop="student_no">
          <el-input v-model="formData.student_no" placeholder="请输入学号"></el-input>
        </el-form-item>
        <el-form-item v-if="isRegister" label="姓名" prop="name">
          <el-input v-model="formData.name" placeholder="请输入姓名"></el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="formData.password" type="password" placeholder="请输入密码" show-password></el-input>
        </el-form-item>
        <el-form-item v-if="isRegister" label="确认密码" prop="confirmPassword">
          <el-input v-model="formData.confirmPassword" type="password" placeholder="请再次输入密码" show-password></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" class="submit-btn">{{ isRegister ? '注册' : '登录' }}</el-button>
        </el-form-item>
      </el-form>
      <div class="switch-link">
        <el-link type="primary" @click="toggleRegister">
          {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
        </el-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { useUserStore } from '@/store/user';
import { ElMessage } from 'element-plus';

const userStore = useUserStore();
const formRef = ref(null);
const isRegister = ref(false);

const formData = reactive({
  student_no: '',
  name: '',
  password: '',
  confirmPassword: '',
});

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'));
  } else {
    if (isRegister.value && formData.confirmPassword !== '') {
      formRef.value.validateField('confirmPassword');
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
  const baseRules = {
    student_no: [{ required: true, message: '请输入学号', trigger: 'blur' }],
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
  formRef.value.validate(async (valid) => {
    if (valid) {
      if (isRegister.value) {
        try {
          await userStore.register({
            student_no: formData.student_no,
            name: formData.name,
            password: formData.password,
          });
          ElMessage.success('注册成功，请登录');
          toggleRegister();
        } catch (error) {
          ElMessage.error(error.response?.data?.error || '注册失败');
        }
      } else {
        try {
          await userStore.login({
            student_no: formData.student_no,
            password: formData.password,
          });
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

const toggleRegister = () => {
  isRegister.value = !isRegister.value;
  formRef.value.resetFields();
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
}

.card-header {
  text-align: center;
  font-size: 20px;
}

.submit-btn {
  width: 100%;
}

.switch-link {
  text-align: center;
  margin-top: 10px;
}
</style>