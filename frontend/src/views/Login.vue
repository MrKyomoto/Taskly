<template>
  <div class="login-container">
    <el-card class="login-card app-card" body-style="padding: 0; display: flex;">
      <!-- 左侧品牌展示区域 -->
      <div class="welcome-section">
        <div class="welcome-overlay"></div>
        <div class="welcome-content">
          <div class="welcome-logo">
            <div class="logo-mark">T</div>
            <div class="logo-text">
              <div class="logo-title">Taskly</div>
              <div class="logo-subtitle">Smart Academic</div>
            </div>
          </div>
          <h2 class="welcome-title">Taskly 作业管理系统</h2>
          <p class="welcome-slogan">连接教与学，让批改更简单。</p>
          <p class="welcome-desc">为高校师生打造的一站式作业发布、提交与批改平台。</p>
        </div>
        <div class="welcome-decor">
          <span class="decor-circle decor-circle-lg"></span>
          <span class="decor-circle decor-circle-md"></span>
          <span class="decor-circle decor-circle-sm"></span>
        </div>
      </div>

      <!-- 右侧表单区域 -->
      <div class="form-section">
        <!-- 统一登录表单 -->
        <div v-if="!isRegisterMode">
          <h3 class="form-title">欢迎回来</h3>
          <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" label-width="80px" :validate-on-rule-change="false">
            <el-form-item label="账号" prop="username">
              <el-input 
                v-model="loginForm.username" 
                placeholder="请输入账号" 
                size="large"
                @keyup.enter="handleLogin"
              ></el-input>
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="请输入密码" 
                show-password 
                size="large"
                @keyup.enter="handleLogin"
              ></el-input>
            </el-form-item>
            <el-form-item>
              <div class="form-actions">
                <el-button
                  type="primary"
                  size="large"
                  @click="handleLogin"
                  class="submit-btn"
                  :loading="logging"
                >
                  登录
                </el-button>
                <div class="switch-link">
                  <el-link type="primary" @click="isRegisterMode = true">
                    没有账号？去注册
                  </el-link>
                </div>
              </div>
            </el-form-item>
            <el-form-item>
              <div class="password-links">
                <el-link type="primary" @click="showForgotPasswordDialog">忘记密码</el-link>
                <el-link type="primary" @click="showResetPasswordDialog">修改密码</el-link>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 注册表单（保留原有功能） -->
        <div v-else>
          <el-tabs v-model="activeTab" class="login-tabs">
            <!-- 学生标签页 -->
            <el-tab-pane label="学生" name="student">
              <h3 class="form-title">学生注册</h3>
              <el-form ref="studentFormRef" :model="formData" :rules="rules" label-width="80px" :validate-on-rule-change="false">
              <el-form-item label="学号" prop="student_no">
                <el-input v-model="formData.student_no" placeholder="请输入学号" @keyup.enter="handleSubmit"></el-input>
              </el-form-item>
              <el-form-item label="姓名" prop="name">
                <el-input v-model="formData.name" placeholder="请输入姓名" @keyup.enter="handleSubmit"></el-input>
              </el-form-item>
              <el-form-item label="邮箱" prop="email">
                <div class="email-input-group">
                  <el-input 
                    v-model="formData.emailPrefix" 
                    placeholder="邮箱前缀" 
                    @keyup.enter="handleSubmit"
                    style="flex: 2; min-width: 200px"
                  ></el-input>
                  <span class="email-separator">@</span>
                  <el-select 
                    v-model="formData.emailSuffix" 
                    placeholder="选择或输入后缀"
                    style="width: 140px"
                    @keyup.enter.native="handleSubmit"
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
              <el-form-item label="电话" prop="phone">
                <div class="phone-input-group">
                  <el-select 
                    v-model="formData.phoneCode" 
                    placeholder="区号"
                    style="width: 100px"
                    @keyup.enter.native="handleSubmit"
                  >
                    <el-option
                      v-for="code in phoneCodes"
                      :key="code.value"
                      :label="code.label"
                      :value="code.value"
                    />
                  </el-select>
                  <el-input 
                    v-model="formData.phoneNumber" 
                    placeholder="手机号" 
                    @keyup.enter="handleSubmit"
                    style="flex: 2; margin-left: 8px; min-width: 180px"
                  ></el-input>
                </div>
              </el-form-item>
              <el-form-item label="密码" prop="password">
                <el-input v-model="formData.password" type="password" placeholder="请输入密码" show-password @keyup.enter="handleSubmit"></el-input>
              </el-form-item>
              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input v-model="formData.confirmPassword" type="password" placeholder="请再次输入密码" show-password @keyup.enter="handleSubmit"></el-input>
              </el-form-item>
              <el-form-item>
                <div class="form-actions">
                  <el-button type="primary" @click="handleSubmit" class="submit-btn">注册</el-button>
                  <div class="switch-link">
                    <el-link type="primary" @click="isRegisterMode = false">
                      已有账号？去登录
                    </el-link>
                  </div>
                </div>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <!-- 教师标签页 -->
          <el-tab-pane label="教师" name="teacher">
            <h3 class="form-title">教师注册</h3>
            <el-form ref="teacherFormRef" :model="formData" :rules="rules" label-width="80px" :validate-on-rule-change="false">
              <el-form-item label="工号" prop="staff_no">
                <el-input v-model="formData.staff_no" placeholder="请输入工号" @keyup.enter="handleSubmit"></el-input>
              </el-form-item>
              <el-form-item label="姓名" prop="name">
                <el-input v-model="formData.name" placeholder="请输入姓名" @keyup.enter="handleSubmit"></el-input>
              </el-form-item>
              <el-form-item label="邮箱" prop="email">
                <div class="email-input-group">
                  <el-input 
                    v-model="formData.emailPrefix" 
                    placeholder="邮箱前缀" 
                    @keyup.enter="handleSubmit"
                    style="flex: 2; min-width: 200px"
                  ></el-input>
                  <span class="email-separator">@</span>
                  <el-select 
                    v-model="formData.emailSuffix" 
                    placeholder="选择或输入后缀"
                    style="width: 140px"
                    @keyup.enter.native="handleSubmit"
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
              <el-form-item label="电话" prop="phone">
                <div class="phone-input-group">
                  <el-select 
                    v-model="formData.phoneCode" 
                    placeholder="区号"
                    style="width: 100px"
                    @keyup.enter.native="handleSubmit"
                  >
                    <el-option
                      v-for="code in phoneCodes"
                      :key="code.value"
                      :label="code.label"
                      :value="code.value"
                    />
                  </el-select>
                  <el-input 
                    v-model="formData.phoneNumber" 
                    placeholder="手机号" 
                    @keyup.enter="handleSubmit"
                    style="flex: 2; margin-left: 8px; min-width: 180px"
                  ></el-input>
                </div>
              </el-form-item>
              <el-form-item label="密码" prop="password">
                <el-input v-model="formData.password" type="password" placeholder="请输入密码" show-password @keyup.enter="handleSubmit"></el-input>
              </el-form-item>
              <el-form-item label="确认密码" prop="confirmPassword">
                <el-input v-model="formData.confirmPassword" type="password" placeholder="请再次输入密码" show-password @keyup.enter="handleSubmit"></el-input>
              </el-form-item>
              <el-form-item>
                <div class="form-actions">
                  <el-button type="primary" @click="handleSubmit" class="submit-btn">注册</el-button>
                  <div class="switch-link">
                    <el-link type="primary" @click="isRegisterMode = false">
                      已有账号？去登录
                    </el-link>
                  </div>
                </div>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
        </div>
      </div>
    </el-card>

    <!-- 忘记密码对话框 -->
    <el-dialog v-model="forgotPasswordDialogVisible" title="忘记密码" width="500px" @close="closeForgotPasswordDialog">
      <!-- 步骤1: 输入账号 -->
      <div v-if="forgotPasswordStep === 1">
        <el-form :model="forgotPasswordForm" :rules="forgotPasswordRules" ref="forgotPasswordFormRef" label-width="100px" @submit.prevent>
          <el-form-item label="账号" prop="identifier">
            <el-input v-model="forgotPasswordForm.identifier" placeholder="请输入账号" @keyup.enter.prevent="checkIdentifier"></el-input>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 步骤2: 选择验证方式 -->
      <div v-if="forgotPasswordStep === 2">
        <div style="text-align: center; margin-bottom: 20px;">
          <p>请选择验证方式：</p>
        </div>
        <div style="display: flex; gap: 20px; justify-content: center;">
          <el-button type="primary" @click="selectVerificationMethod('email')" size="large">通过邮箱重置</el-button>
          <el-button type="primary" @click="selectVerificationMethod('phone')" size="large">通过电话重置</el-button>
        </div>
      </div>
      
      <!-- 步骤3: 输入邮箱/电话并发送验证码 -->
      <div v-if="forgotPasswordStep === 3">
        <el-form :model="forgotPasswordForm" :rules="forgotPasswordVerificationRules" ref="forgotPasswordVerificationFormRef" label-width="100px">
          <el-form-item v-if="forgotPasswordVerificationMethod === 'email'" label="邮箱" prop="email">
            <div class="email-input-group">
              <el-input 
                v-model="forgotPasswordForm.emailPrefix" 
                placeholder="邮箱前缀" 
                style="flex: 2; min-width: 200px"
                @keyup.enter="sendVerificationCode"
              ></el-input>
              <span class="email-separator">@</span>
              <el-select 
                v-model="forgotPasswordForm.emailSuffix" 
                placeholder="选择或输入后缀"
                style="width: 140px"
                filterable
                allow-create
                default-first-option
                :max-height="200"
                @keyup.enter.native="sendVerificationCode"
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
          <el-form-item v-if="forgotPasswordVerificationMethod === 'phone'" label="电话" prop="phone">
            <div class="phone-input-group">
              <el-select 
                v-model="forgotPasswordForm.phoneCode" 
                placeholder="区号"
                style="width: 100px"
                @keyup.enter.native="sendVerificationCode"
              >
                <el-option
                  v-for="code in phoneCodes"
                  :key="code.value"
                  :label="code.label"
                  :value="code.value"
                />
              </el-select>
              <el-input 
                v-model="forgotPasswordForm.phoneNumber" 
                placeholder="手机号" 
                style="flex: 2; margin-left: 8px; min-width: 180px"
                @keyup.enter="sendVerificationCode"
              ></el-input>
            </div>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="sendVerificationCode" :loading="sendingCode" :disabled="countdown > 0">
              {{ countdown > 0 ? `重新发送(${countdown}s)` : '发送验证码' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 步骤4: 输入验证码和新密码 -->
      <div v-if="forgotPasswordStep === 4">
        <el-form :model="forgotPasswordForm" :rules="forgotPasswordResetRules" ref="forgotPasswordResetFormRef" label-width="100px">
          <el-form-item label="验证码" prop="verificationCode">
            <el-input v-model="forgotPasswordForm.verificationCode" placeholder="请输入6位验证码" maxlength="6" @keyup.enter="resetPasswordWithVerification"></el-input>
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input v-model="forgotPasswordForm.newPassword" type="password" show-password placeholder="请输入新密码" @keyup.enter="resetPasswordWithVerification"></el-input>
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="forgotPasswordForm.confirmPassword" type="password" show-password placeholder="请再次输入新密码" @keyup.enter="resetPasswordWithVerification"></el-input>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div v-if="forgotPasswordStep === 1">
          <el-button @click="closeForgotPasswordDialog">取消</el-button>
          <el-button type="primary" @click="checkIdentifier" :loading="checkingIdentifier">确认</el-button>
        </div>
        <div v-else-if="forgotPasswordStep === 2">
          <el-button @click="forgotPasswordStep = 1">返回</el-button>
        </div>
        <div v-else-if="forgotPasswordStep === 3">
          <el-button @click="forgotPasswordStep = 2">返回</el-button>
        </div>
        <div v-else-if="forgotPasswordStep === 4">
          <el-button @click="forgotPasswordStep = 3">返回</el-button>
          <el-button type="primary" @click="resetPasswordWithVerification" :loading="resettingPassword">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="resetPasswordDialogVisible" title="修改密码" width="400px" @close="resetPasswordDialogVisible = false">
      <el-form :model="resetPasswordForm" :rules="resetPasswordRules" ref="resetPasswordFormRef" label-width="100px" @submit.prevent>
        <el-form-item label="账号" prop="student_no">
          <el-input v-model="resetPasswordForm.student_no" placeholder="请输入账号" @keyup.enter="handleResetPassword"></el-input>
        </el-form-item>
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="resetPasswordForm.oldPassword" type="password" show-password placeholder="请输入原密码" @keyup.enter="handleResetPassword"></el-input>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="resetPasswordForm.newPassword" type="password" show-password placeholder="请输入新密码" @keyup.enter="handleResetPassword"></el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="resetPasswordForm.confirmPassword" type="password" show-password placeholder="请再次输入新密码" @keyup.enter="handleResetPassword"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetPasswordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleResetPassword">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue';
import { useUserStore } from '@/store/user';
import { ElMessage, ElMessageBox } from 'element-plus';
import { validateEmail, validatePhone, validatePassword } from '@/utils/validators';
import { resetPassword } from '@/api/auth';
import api from '@/api/index';

const userStore = useUserStore();
const studentFormRef = ref(null);
const teacherFormRef = ref(null);
const loginFormRef = ref(null);

// 登录表单
const loginForm = reactive({
  username: '',
  password: '',
});

// 登录状态
const logging = ref(false);
const isRegisterMode = ref(false);

// 登录验证规则
const loginRules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
};

// 登录处理函数
const handleLogin = async () => {
  if (!loginFormRef.value) return;
  
  try {
    await loginFormRef.value.validate();
    logging.value = true;
    
    // 清除之前的登录状态（不强制刷新页面）
    userStore.logout(false);
    
    // 调用统一登录接口
    await userStore.login({
      username: loginForm.username,
      password: loginForm.password,
    });
    
    // 登录成功，userStore 会自动跳转
    ElMessage.success('登录成功');
  } catch (error) {
    console.error('Login error:', error);
    const errorMessage = error?.response?.data?.error || '登录失败，请检查账号和密码';
    ElMessage.error(errorMessage);
  } finally {
    logging.value = false;
  }
};

const activeTab = ref('student'); // 'student' or 'teacher'
const isStudentRegister = ref(false);
const isTeacherRegister = ref(false);

const formData = reactive({
  student_no: '',
  staff_no: '',
  name: '',
  emailPrefix: '',
  emailSuffix: 'mail.ustc.edu.cn', // 默认值，会根据 activeTab 动态更新
  phoneCode: '+86',
  phoneNumber: '',
  password: '',
  confirmPassword: '',
});

// 邮箱后缀选项（不包含@符号，因为UI中已有@分隔符）
// USTC 邮箱放在最前面，然后是常用邮箱
const studentEmailSuffixes = ['mail.ustc.edu.cn', 'ustc.edu.cn', 'gmail.com', '163.com', 'qq.com', 'outlook.com', 'sina.com', 'yahoo.com', 'hotmail.com'];
const teacherEmailSuffixes = ['ustc.edu.cn', 'mail.ustc.edu.cn', 'gmail.com', '163.com', 'qq.com', 'outlook.com', 'sina.com', 'yahoo.com', 'hotmail.com'];

// 根据当前角色返回对应的邮箱后缀列表
const emailSuffixes = computed(() => {
  if (activeTab.value === 'student') {
    return studentEmailSuffixes;
  } else {
    return teacherEmailSuffixes;
  }
});

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

// 忘记密码和修改密码相关
const forgotPasswordDialogVisible = ref(false);
const resetPasswordDialogVisible = ref(false);
const forgotPasswordStep = ref(1); // 1: 输入学号/工号, 2: 选择验证方式, 3: 输入邮箱/电话, 4: 输入验证码和新密码
const forgotPasswordVerificationMethod = ref(''); // 'email' or 'phone'
const checkingIdentifier = ref(false);
const sendingCode = ref(false);
const resettingPassword = ref(false);
const countdown = ref(0);
const forgotPasswordForm = reactive({
  identifier: '',
  emailPrefix: '',
  emailSuffix: 'mail.ustc.edu.cn',
  phoneCode: '+86',
  phoneNumber: '',
  verificationCode: '',
  newPassword: '',
  confirmPassword: '',
  userId: null, // 存储验证后的用户ID
  userRole: '', // 'student' or 'teacher'
});
const forgotPasswordFormRef = ref(null);
const forgotPasswordVerificationFormRef = ref(null);
const forgotPasswordResetFormRef = ref(null);
const resetPasswordFormRef = ref(null);

// 修改密码表单
const resetPasswordForm = reactive({
  student_no: '',
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
});

// 切换标签页或注册/登录模式时重置表单
watch([activeTab, isStudentRegister, isTeacherRegister], () => {
  // 先清除验证状态，再重置字段
  const formRef = activeTab.value === 'student' ? studentFormRef.value : teacherFormRef.value;
  if (formRef) {
    formRef.clearValidate(); // 清除所有验证错误
    formRef.resetFields(); // 重置字段值
  }
  // 重置数据模型
  formData.student_no = '';
  formData.staff_no = '';
  formData.name = '';
  formData.emailPrefix = '';
  // 根据角色设置默认邮箱后缀
  formData.emailSuffix = activeTab.value === 'student' ? 'mail.ustc.edu.cn' : 'ustc.edu.cn';
  formData.phoneCode = '+86';
  formData.phoneNumber = '';
  formData.password = '';
  formData.confirmPassword = '';
});

const isRegister = computed(() => {
  // 如果 isRegisterMode 为 true，说明在注册模式
  if (isRegisterMode.value) {
    return true;
  }
  return activeTab.value === 'student' ? isStudentRegister.value : isTeacherRegister.value;
});

// 计算完整邮箱（用于验证和提交）
const computedEmail = computed(() => {
  if (!formData.emailPrefix || !formData.emailSuffix) return '';
  return formData.emailPrefix + '@' + formData.emailSuffix;
});

// 计算完整手机号（用于验证和提交）
const computedPhone = computed(() => {
  if (!formData.phoneCode || !formData.phoneNumber) return '';
  return formData.phoneCode + formData.phoneNumber;
});

// 密码验证
const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请输入密码'));
  } else {
    const result = validatePassword(value);
    if (!result.isValid) {
      callback(new Error(result.message));
    } else {
      if (isRegister.value && formData.confirmPassword !== '') {
        const formRef = activeTab.value === 'student' ? studentFormRef.value : teacherFormRef.value;
        formRef?.validateField('confirmPassword');
      }
      callback();
    }
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

// 邮箱验证
const validateEmailField = (rule, value, callback) => {
  const email = computedEmail.value;
  if (!formData.emailPrefix || !formData.emailSuffix) {
    callback(new Error('请输入邮箱'));
  } else if (!validateEmail(email)) {
    callback(new Error('邮箱格式不正确'));
  } else {
    callback();
  }
};

// 电话验证
const validatePhoneField = (rule, value, callback) => {
  const phone = computedPhone.value;
  if (!formData.phoneCode || !formData.phoneNumber) {
    callback(new Error('请输入电话'));
  } else if (!validatePhone(phone)) {
    callback(new Error('电话格式不正确，请输入完整的手机号'));
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
  if (isRegister.value && activeTab.value === 'student') {
    return {
      ...baseRules,
      name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
      email: [{ required: true, validator: validateEmailField, trigger: 'blur' }],
      phone: [{ required: true, validator: validatePhoneField, trigger: 'blur' }],
      confirmPassword: [{ required: true, validator: validatePass2, trigger: 'blur' }],
    };
  }
  if (isRegister.value && activeTab.value === 'teacher') {
    return {
      ...baseRules,
      name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
      email: [{ required: true, validator: validateEmailField, trigger: 'blur' }],
      phone: [{ required: true, validator: validatePhoneField, trigger: 'blur' }],
      confirmPassword: [{ required: true, validator: validatePass2, trigger: 'blur' }],
    };
  }
  return baseRules;
});

// 忘记密码验证规则
const forgotPasswordRules = computed(() => ({
  identifier: [{ required: true, message: '请输入账号', trigger: 'blur' }],
}));

// 计算完整邮箱和电话（用于验证）
const computedForgotEmail = computed(() => {
  if (!forgotPasswordForm.emailPrefix || !forgotPasswordForm.emailSuffix) return '';
  return forgotPasswordForm.emailPrefix + '@' + forgotPasswordForm.emailSuffix;
});

const computedForgotPhone = computed(() => {
  if (!forgotPasswordForm.phoneCode || !forgotPasswordForm.phoneNumber) return '';
  return forgotPasswordForm.phoneCode + forgotPasswordForm.phoneNumber;
});

// 忘记密码验证邮箱/电话规则
const validateForgotEmail = (rule, value, callback) => {
  const email = computedForgotEmail.value;
  if (!forgotPasswordForm.emailPrefix || !forgotPasswordForm.emailSuffix) {
    callback(new Error('请输入邮箱'));
  } else if (!validateEmail(email)) {
    callback(new Error('邮箱格式不正确'));
  } else {
    callback();
  }
};

const validateForgotPhone = (rule, value, callback) => {
  const phone = computedForgotPhone.value;
  if (!forgotPasswordForm.phoneCode || !forgotPasswordForm.phoneNumber) {
    callback(new Error('请输入电话'));
  } else if (!validatePhone(phone)) {
    callback(new Error('电话格式不正确，请输入完整的手机号'));
  } else {
    callback();
  }
};

const forgotPasswordVerificationRules = computed(() => {
  if (forgotPasswordVerificationMethod.value === 'email') {
    return {
      email: [{ required: true, validator: validateForgotEmail, trigger: 'blur' }],
    };
  } else {
    return {
      phone: [{ required: true, validator: validateForgotPhone, trigger: 'blur' }],
    };
  }
});

// 忘记密码重置规则
const validateForgotNewPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入新密码'));
  } else {
    const result = validatePassword(value);
    if (!result.isValid) {
      callback(new Error(result.message));
    } else {
      callback();
    }
  }
};

const validateForgotConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入新密码'));
  } else if (value !== forgotPasswordForm.newPassword) {
    callback(new Error("两次输入的密码不一致!"));
  } else {
    callback();
  }
};

const forgotPasswordResetRules = {
  verificationCode: [{ required: true, message: '请输入验证码', trigger: 'blur' }, { len: 6, message: '验证码为6位', trigger: 'blur' }],
  newPassword: [{ required: true, validator: validateForgotNewPassword, trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validateForgotConfirmPassword, trigger: 'blur' }],
};

// 修改密码验证规则
const validateResetPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入新密码'));
  } else {
    const result = validatePassword(value);
    if (!result.isValid) {
      callback(new Error(result.message));
    } else {
      // 检查新密码是否和原密码相同
      if (resetPasswordForm.oldPassword && value === resetPasswordForm.oldPassword) {
        callback(new Error('新密码不能与原密码相同'));
      } else {
        callback();
      }
    }
  }
};

const validateResetPassword2 = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入新密码'));
  } else if (value !== resetPasswordForm.newPassword) {
    callback(new Error("两次输入的密码不一致!"));
  } else {
    callback();
  }
};

const resetPasswordRules = {
  student_no: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [{ required: true, validator: validateResetPassword, trigger: 'blur' }],
  confirmPassword: [{ required: true, validator: validateResetPassword2, trigger: 'blur' }],
};

const handleSubmit = () => {
  const formRef = activeTab.value === 'student' ? studentFormRef.value : teacherFormRef.value;
  formRef.validate(async (valid) => {
    if (valid) {
      const currentRole = activeTab.value;
      if (isRegister.value) {
        const payload = currentRole === 'student'
          ? { 
              student_no: formData.student_no, 
              name: formData.name, 
              password: formData.password,
              email: computedEmail.value,
              phone: computedPhone.value
            }
          : { 
              staff_no: formData.staff_no, 
              name: formData.name, 
              password: formData.password,
              email: computedEmail.value,
              phone: computedPhone.value
            };
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

// 关闭忘记密码对话框
const closeForgotPasswordDialog = () => {
  forgotPasswordDialogVisible.value = false;
  forgotPasswordStep.value = 1;
  forgotPasswordVerificationMethod.value = '';
  forgotPasswordForm.identifier = '';
  forgotPasswordForm.emailPrefix = '';
  // 根据角色设置默认邮箱后缀
  const defaultSuffix = forgotPasswordForm.userRole === 'student' ? 'mail.ustc.edu.cn' : 'ustc.edu.cn';
  forgotPasswordForm.emailSuffix = defaultSuffix;
  forgotPasswordForm.phoneCode = '+86';
  forgotPasswordForm.phoneNumber = '';
  forgotPasswordForm.verificationCode = '';
  forgotPasswordForm.newPassword = '';
  forgotPasswordForm.confirmPassword = '';
  forgotPasswordForm.userId = null;
  forgotPasswordForm.userRole = '';
  countdown.value = 0;
  forgotPasswordFormRef.value?.clearValidate();
  forgotPasswordVerificationFormRef.value?.clearValidate();
  forgotPasswordResetFormRef.value?.clearValidate();
};

// 显示忘记密码对话框
const showForgotPasswordDialog = () => {
  forgotPasswordDialogVisible.value = true;
  forgotPasswordStep.value = 1;
  forgotPasswordForm.identifier = '';
  // 根据角色设置默认邮箱后缀
  const defaultSuffix = forgotPasswordForm.userRole === 'student' ? 'mail.ustc.edu.cn' : 'ustc.edu.cn';
  forgotPasswordForm.emailSuffix = defaultSuffix;
  forgotPasswordFormRef.value?.clearValidate();
};

// 检查账号是否存在（统一接口）
const checkIdentifier = async () => {
  if (!forgotPasswordFormRef.value) return;
  try {
    await forgotPasswordFormRef.value.validate();
    checkingIdentifier.value = true;
    const response = await api.post('/auth/check-identifier', {
      identifier: forgotPasswordForm.identifier,
    });
    forgotPasswordForm.userId = response.data.user_id;
    forgotPasswordForm.userRole = response.data.role;
    forgotPasswordStep.value = 2;
    ElMessage.success('验证成功，请选择验证方式');
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '账号不存在');
  } finally {
    checkingIdentifier.value = false;
  }
};

// 选择验证方式
const selectVerificationMethod = (method) => {
  forgotPasswordVerificationMethod.value = method;
  forgotPasswordStep.value = 3;
  // 重置邮箱/电话输入
  forgotPasswordForm.emailPrefix = '';
  // 根据角色设置默认邮箱后缀
  const defaultSuffix = forgotPasswordForm.userRole === 'student' ? 'mail.ustc.edu.cn' : 'ustc.edu.cn';
  forgotPasswordForm.emailSuffix = defaultSuffix;
  forgotPasswordForm.phoneCode = '+86';
  forgotPasswordForm.phoneNumber = '';
};

// 发送验证码
const sendVerificationCode = async () => {
  if (!forgotPasswordVerificationFormRef.value) return;
  try {
    await forgotPasswordVerificationFormRef.value.validate();
    sendingCode.value = true;
    const role = forgotPasswordForm.userRole;
    const contact = forgotPasswordVerificationMethod.value === 'email' 
      ? computedForgotEmail.value 
      : computedForgotPhone.value;
    
    await api.post(`/auth/${role === 'student' ? 'students' : 'teachers'}/send-verification-code`, {
      user_id: forgotPasswordForm.userId,
      contact: contact,
      method: forgotPasswordVerificationMethod.value,
    });
    
    ElMessage.success('验证码已发送');
    forgotPasswordStep.value = 4;
    
    // 开始倒计时
    countdown.value = 60;
    const timer = setInterval(() => {
      countdown.value--;
      if (countdown.value <= 0) {
        clearInterval(timer);
      }
    }, 1000);
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '发送验证码失败');
  } finally {
    sendingCode.value = false;
  }
};

// 通过验证码重置密码
const resetPasswordWithVerification = async () => {
  if (!forgotPasswordResetFormRef.value) return;
  try {
    await forgotPasswordResetFormRef.value.validate();
    resettingPassword.value = true;
    const role = forgotPasswordForm.userRole;
    
    await api.post(`/auth/${role === 'student' ? 'students' : 'teachers'}/reset-password-with-verification`, {
      user_id: forgotPasswordForm.userId,
      verification_code: forgotPasswordForm.verificationCode,
      new_password: forgotPasswordForm.newPassword,
    });
    
    ElMessage.success('密码重置成功，请使用新密码登录');
    closeForgotPasswordDialog();
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '密码重置失败');
  } finally {
    resettingPassword.value = false;
  }
};

// 显示修改密码对话框
const showResetPasswordDialog = () => {
  resetPasswordDialogVisible.value = true;
  resetPasswordForm.student_no = '';
  resetPasswordForm.oldPassword = '';
  resetPasswordForm.newPassword = '';
  resetPasswordForm.confirmPassword = '';
  resetPasswordFormRef.value?.clearValidate();
};


// 处理修改密码
const handleResetPassword = async () => {
  if (!resetPasswordFormRef.value) return;
  try {
    await resetPasswordFormRef.value.validate();
    // 调用重置密码接口
    await resetPassword({
      student_no: resetPasswordForm.student_no,
      old_password: resetPasswordForm.oldPassword,
      new_password: resetPasswordForm.newPassword,
    });
    ElMessage.success('密码修改成功，请使用新密码登录');
    resetPasswordDialogVisible.value = false;
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '密码修改失败');
  }
};

// 注意：Enter 键监听已通过 @keyup.enter 在组件级别实现，无需全局监听
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: var(--app-bg, #f5f7fa);
}

.login-card {
  width: 980px;
  border-radius: 16px;
  overflow: hidden;
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(16px);
}

.welcome-section {
  position: relative;
  width: 45%;
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 60%, #60a5fa 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 40px;
  overflow: hidden;
}

.welcome-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at top left, rgba(255, 255, 255, 0.16), transparent 55%);
  pointer-events: none;
}

.welcome-content {
  position: relative;
  z-index: 1;
}

.welcome-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
}

.logo-mark {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.16);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 20px;
  letter-spacing: 1px;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 20px;
  font-weight: 600;
}

.logo-subtitle {
  font-size: 12px;
  opacity: 0.8;
}

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 12px;
}

.welcome-slogan {
  font-size: 16px;
  margin: 0 0 8px;
}

.welcome-desc {
  font-size: 14px;
  opacity: 0.9;
  max-width: 260px;
}

.welcome-decor {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.decor-circle {
  position: absolute;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.28), transparent 60%);
}

.decor-circle-lg {
  width: 220px;
  height: 220px;
  right: -60px;
  top: -40px;
}

.decor-circle-md {
  width: 140px;
  height: 140px;
  left: -40px;
  bottom: -20px;
}

.decor-circle-sm {
  width: 80px;
  height: 80px;
  right: 40px;
  bottom: 60px;
}

.form-section {
  width: 55%;
  padding: 40px 56px;
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
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.form-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.submit-btn {
  width: 100%;
}

.switch-link {
  text-align: center;
}

.password-links {
  display: flex;
  justify-content: space-around;
  width: 100%;
  margin-top: 10px;
}

.email-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.email-separator {
  color: #606266;
  font-weight: 500;
}

.phone-input-group {
  display: flex;
  align-items: center;
}
</style>