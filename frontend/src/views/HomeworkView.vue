<template>
  <div class="homework-view">
    <el-header class="header">
      <div class="header-content">
        <el-button text @click="goBack" :icon="ArrowLeft">返回</el-button>
        <h1 class="header-title">{{ homeworkInfo?.title || '作业详情' }}</h1>
        <div></div>
      </div>
    </el-header>

    <div class="homework-view-container">
      <el-skeleton v-if="loading" animated :count="5" />
      <template v-else-if="homeworkInfo">
        <!-- 作业要求展示 -->
        <el-card class="homework-requirement-card" shadow="never">
          <template #header>
            <div class="card-title">作业要求</div>
          </template>
          <div class="homework-content">
            <div v-if="homeworkInfo.content" class="text-content" v-html="formatTextContent(homeworkInfo.content)"></div>
            <div v-if="homeworkImages.length > 0" class="requirement-images">
              <el-image
                v-for="(img, index) in homeworkImages"
                :key="index"
                :src="getImageUrl(img)"
                :preview-src-list="homeworkImages.map(i => getImageUrl(i))"
                :initial-index="index"
                fit="cover"
                class="requirement-image"
                lazy
              />
            </div>
          </div>
        </el-card>

        <!-- 批改反馈展示（如果已批改） -->
        <el-card v-if="submission?.is_graded && gradingInfo" class="grading-card" shadow="never">
          <template #header>
            <div class="card-title">批改反馈</div>
          </template>
          <div class="grading-content">
            <div class="score-section">
              <el-statistic :value="gradingInfo.score" :precision="0">
                <template #title>
                  <span class="score-label">最终得分</span>
                </template>
                <template #suffix>
                  <span class="score-unit">分</span>
                </template>
              </el-statistic>
            </div>
            <div v-if="gradingInfo.grader_name" class="grader-info">
              <el-tag type="info" size="small">批改人：{{ gradingInfo.grader_name }}</el-tag>
            </div>
            <div class="feedback-section">
              <el-alert
                :title="gradingInfo.grader_name ? '老师评语' : 'AI 助教点评'"
                type="info"
                :closable="false"
                show-icon
              >
                <template #default>
                  <div class="feedback-text">
                    {{ (gradingInfo.ai_feedback && gradingInfo.ai_feedback.trim()) ? gradingInfo.ai_feedback : '暂无评语' }}
                  </div>
                </template>
              </el-alert>
            </div>
          </div>
        </el-card>

        <!-- 查看提交按钮（如果已提交） -->
        <el-card v-if="submission" class="view-submission-card" shadow="never">
          <el-button type="primary" @click="goToSubmissionView">查看提交</el-button>
        </el-card>

        <!-- 提交表单（如果未批改或未提交） -->
        <el-card v-if="!submission?.is_graded" class="submission-card" shadow="never">
          <template #header>
            <div class="card-title">{{ submission ? '重新提交作业' : '提交作业' }}</div>
          </template>
          <!-- 如果已过ddl，显示提示信息 -->
          <el-alert
            v-if="isOverdue"
            title="作业已逾期"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 20px"
          >
            <template #default>
              <span>该作业的截止时间已过，无法提交或重新提交。您只能查看作业详情和已提交的内容。</span>
            </template>
          </el-alert>
          <el-form :model="submissionForm" ref="submissionFormRef" label-width="100px">
            <el-form-item label="文字内容">
              <el-input
                v-model="submissionForm.text_content"
                type="textarea"
                :rows="6"
                placeholder="请输入作业内容..."
                :disabled="isOverdue"
                @keydown.enter.ctrl="handleSubmit"
              />
            </el-form-item>
            <el-form-item label="图片附件">
              <el-upload
                v-model:file-list="fileList"
                :action="uploadAction"
                :headers="uploadHeaders"
                :before-upload="beforeUpload"
                :on-success="handleUploadSuccess"
                :on-remove="handleRemove"
                :on-error="handleUploadError"
                :on-progress="handleUploadProgress"
                :on-preview="handlePreview"
                :disabled="isOverdue"
                list-type="picture-card"
                :limit="10"
                accept="image/*"
                :auto-upload="true"
                :show-file-list="true"
                :preview-teleported="true"
              >
                <el-icon><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">支持上传图片，最多10张</div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSubmit" :loading="submitting" :disabled="isOverdue">
                {{ submission ? '重新提交' : '提交作业' }}
              </el-button>
              <el-button @click="goBack">取消</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 已提交内容展示（只读模式，如果已批改） -->
        <el-card v-if="submission?.is_graded" class="submission-display-card" shadow="never">
          <template #header>
            <div class="card-title">我的提交</div>
          </template>
          <div class="submission-content">
            <div v-if="submission.text_content" class="text-content">
              {{ submission.text_content }}
            </div>
            <div v-if="submissionImages.length > 0" class="submission-images">
              <div 
                v-for="(img, index) in submissionImages" 
                :key="index"
                class="submission-image-wrapper"
              >
                <div class="annotator-container">
                  <!-- 如果有批注，显示批注；否则显示原图 -->
                  <template v-if="hasAnnotationForImage(img)">
                    <ImageAnnotator
                      :image-url="getImageUrl(typeof img === 'string' ? img : (img.image_url || img.url || img), true)"
                      :model-value="getAnnotationForImage(img)"
                      :readonly="true"
                    />
                  </template>
                  <template v-else>
                    <!-- 没有批注，显示原图 -->
                    <el-image
                      :src="getImageUrl(typeof img === 'string' ? img : (img.image_url || img.url || img), true)"
                      :preview-src-list="submissionImages.map(i => {
                        const url = typeof i === 'string' ? i : (i.image_url || i.url || i);
                        return getImageUrl(url, true);
                      })"
                      :initial-index="index"
                      fit="cover"
                      class="submission-image-display"
                      lazy
                      :preview-teleported="true"
                      :z-index="3000"
                    />
                  </template>
                </div>
              </div>
            </div>
            <div class="submit-time">
              提交时间：{{ formatDateTime(submission.submit_time) }}
            </div>
          </div>
        </el-card>
      </template>
      <el-empty v-else description="作业不存在或无权访问" :image-size="100" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useRouter, useRoute, onBeforeRouteLeave } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { ArrowLeft, Plus, ZoomIn } from '@element-plus/icons-vue';
import { fetchHomeworkSubmission, submitHomework, uploadHomeworkImage } from '@/api/student';
import { fetchCourseHomeworks, fetchStudentCourses } from '@/api/student';
import { useUserStore } from '@/store/user';
import { getImageUrl, parseImageUrls } from '@/utils/image';
import ImageAnnotator from '@/components/ImageAnnotator.vue';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const loading = ref(false);
const homeworkInfo = ref(null);
const submission = ref(null);
const gradingInfo = ref(null);
const submitting = ref(false);
const hasUnsavedChanges = ref(false);

const submissionForm = ref({
  text_content: '',
});
const submissionFormRef = ref(null);
const fileList = ref([]);
const imageUrls = ref([]);

// 获取作业ID和课程ID
const homeworkId = computed(() => parseInt(route.params.id));

// 判断作业是否已逾期
const isOverdue = computed(() => {
  if (!homeworkInfo.value?.deadline) return false;
  const deadline = new Date(homeworkInfo.value.deadline);
  const now = new Date();
  return deadline < now;
});

// 获取批注数据
const getAnnotationForImage = (img) => {
  if (!gradingInfo.value?.annotation_data) return null;
  const imgUrl = typeof img === 'string' ? img : (img.image_url || img.url || img);
  const annotation = gradingInfo.value.annotation_data.find(
    ann => {
      const annUrl = ann.image_url || ann.url;
      return annUrl === imgUrl || annUrl === getImageUrl(imgUrl, true);
    }
  );
  // 如果找到批注且批注有elements，返回批注；否则返回null
  if (annotation && annotation.elements && annotation.elements.length > 0) {
    return annotation;
  }
  return null;
};

// 检查图片是否有批注
const hasAnnotationForImage = (img) => {
  const annotation = getAnnotationForImage(img);
  return annotation !== null && annotation.elements && annotation.elements.length > 0;
};

// 计算上传接口
const uploadAction = computed(() => {
  return `/api/students/me/homeworks/${homeworkId.value}/upload-image`;
});

// 上传请求头
const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token');
  return {
    Authorization: `Bearer ${token}`,
  };
});

// 解析作业图片
const homeworkImages = computed(() => {
  if (!homeworkInfo.value?.image_urls) return [];
  const parsed = parseImageUrls(homeworkInfo.value.image_urls);
  console.log('作业图片解析:', {
    raw: homeworkInfo.value.image_urls,
    parsed: parsed,
    urls: parsed.map(img => getImageUrl(img))
  });
  return parsed;
});

// 解析提交图片
const submissionImages = computed(() => {
  if (!submission.value?.image_urls) return [];
  let images = [];
  if (Array.isArray(submission.value.image_urls)) {
    images = submission.value.image_urls;
  } else {
    images = parseImageUrls(submission.value.image_urls);
  }
  // 确保返回的是字符串数组，如果是对象则提取 image_url 或直接使用
  return images.map(img => {
    if (typeof img === 'string') return img;
    if (typeof img === 'object' && img !== null) {
      return img.image_url || img.url || String(img);
    }
    return String(img);
  });
});

// 返回上一页
const goBack = () => {
  router.push({ name: 'StudentHome' });
};

// 跳转到提交查看页面
const goToSubmissionView = () => {
  router.push({ name: 'SubmissionView', params: { id: homeworkId.value } });
};

// 预览图片（用于已批改的提交）
const previewImage = (index) => {
  if (!submission.value?.image_urls || submissionImages.value.length === 0) return;
  
  // 构建预览图片列表（需要包含 token）
  const previewList = submissionImages.value.map(img => {
    const url = typeof img === 'string' ? img : (img.image_url || img.url || img);
    return getImageUrl(url, true);
  });
  
  // 使用 Element Plus 的图片预览功能
  // 创建一个临时的 el-image 来触发预览
  const imageUrl = previewList[index];
  if (imageUrl) {
    // 创建全屏预览
    const viewer = document.createElement('div');
    viewer.className = 'image-preview-viewer';
    viewer.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.9);
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    `;
    
    const img = document.createElement('img');
    img.src = imageUrl;
    img.style.cssText = `
      max-width: 90%;
      max-height: 90%;
      object-fit: contain;
    `;
    
    viewer.appendChild(img);
    document.body.appendChild(viewer);
    
    const close = () => {
      if (document.body.contains(viewer)) {
        document.body.removeChild(viewer);
      }
      document.removeEventListener('keydown', handleEsc);
    };
    
    viewer.addEventListener('click', close);
    // ESC 键关闭
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        close();
      }
    };
    document.addEventListener('keydown', handleEsc);
  }
};


// 格式化文本内容（支持换行）
const formatTextContent = (text) => {
  if (!text) return '';
  return text.replace(/\n/g, '<br>');
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

// 获取分数样式类
const getScoreClass = (score) => {
  if (score === null || score === undefined) return 'score-ungraded';
  if (score >= 90) return 'score-excellent';
  if (score >= 80) return 'score-good';
  if (score >= 60) return 'score-pass';
  return 'score-fail';
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

// 上传成功
const handleUploadSuccess = (response, file) => {
  // 后端返回格式：{ success_count: 1, image_urls: ["/uploads/...", ...], errors: [] }
  let imageUrl = null;
  if (response.image_urls && Array.isArray(response.image_urls) && response.image_urls.length > 0) {
    // 多文件上传，取最后一个（当前上传的文件）
    imageUrl = response.image_urls[response.image_urls.length - 1];
  } else if (response.image_url) {
    imageUrl = response.image_url;
  } else if (typeof response === 'string') {
    imageUrl = response;
  }
  
  if (imageUrl) {
    // 保存原始相对路径到 imageUrls（用于提交时使用）
    imageUrls.value.push(imageUrl);
    hasUnsavedChanges.value = true;
    
    // 找到当前上传的文件并更新其 URL
    const fileIndex = fileList.value.findIndex(f => f.uid === file.uid);
    // 由于图片访问需要认证，在 URL 中添加 token 参数
    const imageUrlFull = getImageUrl(imageUrl, true);
    
    if (fileIndex > -1) {
      // 使用服务器返回的 URL 替换 blob URL
      // 后端返回的是 /uploads/... 格式，需要转换为完整 URL
      // 使用 nextTick 确保 Vue 响应式更新
      nextTick(() => {
        if (fileList.value[fileIndex]) {
          // 创建新对象以确保响应式更新
          const updatedFile = {
            ...fileList.value[fileIndex],
            url: imageUrlFull,
            response: response,
            status: 'success',
          };
          // 清除上传进度
          if (updatedFile.percentage !== undefined) {
            delete updatedFile.percentage;
          }
          // 使用 Vue 3 的响应式更新方式
          fileList.value[fileIndex] = updatedFile;
        }
      });
    } else {
      // 如果找不到文件，添加一个新项
      fileList.value.push({
        uid: file.uid || `file-${Date.now()}-${Math.random()}`,
        name: file.name || `image-${Date.now()}.jpg`,
        url: imageUrlFull,
        status: 'success',
        response: response,
      });
    }
    
    ElMessage.success('图片上传成功');
  } else {
    ElMessage.error('上传失败：未返回图片URL');
    // 如果上传失败，标记为失败状态
    const fileIndex = fileList.value.findIndex(f => f.uid === file.uid);
    if (fileIndex > -1) {
      fileList.value[fileIndex].status = 'fail';
    }
  }
};

// 删除图片
const handleRemove = (file) => {
  // 从 imageUrls 中移除对应的 URL
  // file.response 可能是 { image_urls: [...] } 或 { image_url: "..." }
  let urlToRemove = null;
  if (file.response) {
    if (Array.isArray(file.response.image_urls)) {
      urlToRemove = file.response.image_urls[file.response.image_urls.length - 1];
    } else if (file.response.image_url) {
      urlToRemove = file.response.image_url;
    }
  } else if (file.url) {
    // 如果 file.url 是完整的图片 URL，需要提取相对路径
    // 例如：http://localhost:5000/api/images/uploads/... -> uploads/...
    const urlMatch = file.url.match(/uploads\/.+$/);
    if (urlMatch) {
      urlToRemove = urlMatch[0];
    } else {
      // 尝试从 URL 中提取路径部分
      try {
        const urlObj = new URL(file.url);
        urlToRemove = urlObj.pathname.replace('/api/images/', '');
      } catch {
        urlToRemove = file.url;
      }
    }
  }
  
  if (urlToRemove) {
    // 从 imageUrls 中移除
    const index = imageUrls.value.findIndex(url => {
      // 支持多种匹配方式
      const urlStr = String(url);
      const removeStr = String(urlToRemove);
      if (urlStr === removeStr) return true;
      // 检查是否包含相对路径部分
      if (urlStr.includes(removeStr) || removeStr.includes(urlStr)) return true;
      // 如果 urlToRemove 是相对路径，检查 imageUrls 中是否包含
      if (removeStr.startsWith('uploads/') && urlStr.includes(removeStr)) return true;
      return false;
    });
    if (index > -1) {
      imageUrls.value.splice(index, 1);
      hasUnsavedChanges.value = true;
    }
  }
};

// 上传进度
const handleUploadProgress = (event, file) => {
  // 更新上传进度
  const fileIndex = fileList.value.findIndex(f => f.uid === file.uid);
  if (fileIndex > -1) {
    fileList.value[fileIndex].status = 'uploading';
    fileList.value[fileIndex].percentage = Math.round(event.percent);
  }
};

// 上传失败
const handleUploadError = (error, file) => {
  ElMessage.error('图片上传失败，请重试');
  console.error('Upload error:', error);
  // 标记文件为失败状态
  const fileIndex = fileList.value.findIndex(f => f.uid === file.uid);
  if (fileIndex > -1) {
    fileList.value[fileIndex].status = 'fail';
  }
};

// 预览上传的图片
const handlePreview = (file) => {
  // 获取图片 URL（优先使用 file.url，如果没有则从 response 中获取）
  let imageUrl = file.url;
  if (!imageUrl && file.response) {
    if (file.response.image_urls && Array.isArray(file.response.image_urls) && file.response.image_urls.length > 0) {
      imageUrl = file.response.image_urls[file.response.image_urls.length - 1];
    } else if (file.response.image_url) {
      imageUrl = file.response.image_url;
    }
    // 如果是相对路径，需要转换为完整 URL（包含 token）
    if (imageUrl && !imageUrl.startsWith('http')) {
      imageUrl = getImageUrl(imageUrl, true);
    }
  }
  
  if (!imageUrl) {
    ElMessage.warning('无法预览该图片');
    return;
  }
  
  // 构建所有图片的预览列表
  const previewList = fileList.value
    .filter(f => f.status === 'success')
    .map(f => {
      let url = f.url;
      if (!url && f.response) {
        if (f.response.image_urls && Array.isArray(f.response.image_urls) && f.response.image_urls.length > 0) {
          url = f.response.image_urls[f.response.image_urls.length - 1];
        } else if (f.response.image_url) {
          url = f.response.image_url;
        }
        if (url && !url.startsWith('http')) {
          url = getImageUrl(url, true);
        }
      }
      return url;
    })
    .filter(url => url);
  
  // 找到当前图片在列表中的索引
  const currentIndex = previewList.findIndex(url => url === imageUrl);
  
  // 使用 Element Plus 的 ImageViewer 或者自定义预览
  // 创建预览对话框
  const viewer = document.createElement('div');
  viewer.className = 'image-preview-viewer';
  viewer.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.9);
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  `;
  
  const img = document.createElement('img');
  img.src = imageUrl;
  img.style.cssText = `
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
  `;
  
  viewer.appendChild(img);
  document.body.appendChild(viewer);
  
  const close = () => {
    if (document.body.contains(viewer)) {
      document.body.removeChild(viewer);
    }
    document.removeEventListener('keydown', handleEsc);
  };
  
  viewer.addEventListener('click', close);
  // ESC 键关闭
  const handleEsc = (e) => {
    if (e.key === 'Escape') {
      close();
    }
  };
  document.addEventListener('keydown', handleEsc);
};

// 提交作业
const handleSubmit = async () => {
  if (!submissionFormRef.value) return;

  // 验证至少要有文字或图片
  if (!submissionForm.value.text_content.trim() && imageUrls.value.length === 0) {
    ElMessage.warning('请至少输入文字内容或上传一张图片');
    return;
  }

  try {
    submitting.value = true;
    await submitHomework(homeworkId.value, {
      text_content: submissionForm.value.text_content.trim(),
      image_urls: imageUrls.value,
    });
    ElMessage.success('作业提交成功');
    hasUnsavedChanges.value = false;
    // 刷新数据
    await fetchData();
    // 提交成功后，清空表单和图片列表
    submissionForm.value.text_content = '';
    imageUrls.value = [];
    fileList.value = [];
  } catch (error) {
    const status = error?.response?.status;
    if (status === 400) {
      ElMessage.error(error?.response?.data?.error || '提交失败，请检查输入');
    } else if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else {
      ElMessage.error(error?.response?.data?.error || '提交失败，请重试');
    }
  } finally {
    submitting.value = false;
  }
};

// 监听表单变化
watch(
  () => [submissionForm.value.text_content, imageUrls.value.length],
  () => {
    if (!submission.value?.is_graded) {
      hasUnsavedChanges.value = true;
    }
  },
  { deep: true }
);

// 路由守卫：移除未保存修改的提示，允许直接退出
onBeforeRouteLeave((to, from, next) => {
  // 直接允许离开，不再提示未保存的修改
  next();
});

// 获取数据
const fetchData = async () => {
  loading.value = true;
  try {
    // 先获取作业信息（需要从课程中查找）
    // 由于没有直接通过 homework_id 获取作业的接口，我们需要先找到课程ID
    // 这里简化处理：从所有课程中查找包含该作业的课程
    const coursesRes = await fetchStudentCourses();
    const courseList = coursesRes.data?.course_list || [];

    let foundHomework = null;
    let foundCourseId = null;

    for (const course of courseList) {
      try {
        const homeworksRes = await fetchCourseHomeworks(course.id);
        const homeworkList = homeworksRes.data?.homework_list || [];
        const hw = homeworkList.find(h => h.id === homeworkId.value);
        if (hw) {
          foundHomework = hw;
          foundCourseId = course.id;
          break;
        }
      } catch (error) {
        // 记录错误但继续查找下一个课程
        console.warn(`获取课程 ${course.id} 的作业列表失败:`, error);
        // 继续查找下一个课程
        continue;
      }
    }

    if (!foundHomework || !foundCourseId) {
      ElMessage.error('作业不存在或无权访问');
      router.push({ name: 'StudentHome' });
      return;
    }

    // 先设置作业信息，确保页面可以显示
    homeworkInfo.value = foundHomework;

    // 检查作业信息中是否包含提交状态（从课程列表返回的）
    // 如果已提交，才获取完整的提交信息
    // 注意：即使获取提交信息失败，也不应该阻止页面显示作业
    // 但是不自动填充表单，只有在用户点击"查看提交"时才填充
    if (foundHomework.submission) {
      // 有提交状态，尝试获取完整提交信息
      // 但即使失败也不应该影响作业显示
      try {
        const submissionRes = await fetchHomeworkSubmission(foundCourseId, homeworkId.value);
        submission.value = submissionRes.data?.submission || null;

        // 如果已批改，获取批改信息
        if (submission.value?.is_graded) {
          // 从 submission 中获取批改信息（后端已返回）
          gradingInfo.value = {
            score: submission.value.score !== undefined ? submission.value.score : null,
            ai_feedback: submission.value.ai_feedback || null,
            annotation_data: submission.value.annotation_data || [],
            grader_name: submission.value.grader_name || null,
          };
        } else {
          // 如果未批改，清空批改信息
          gradingInfo.value = null;
        }
        // 注意：不在这里填充表单，只有在用户点击"查看提交"时才填充
      } catch (error) {
        // 获取提交详情失败，但不阻止页面显示
        // 404 表示提交记录不存在（可能是数据不一致），静默处理
        if (error?.response?.status === 404) {
          console.warn('提交记录不存在（可能已删除）:', error);
          submission.value = null;
        } else {
          // 其他错误，记录但不阻止页面显示
          console.error('获取提交详情失败:', error);
          // 不显示错误消息，避免干扰用户
          submission.value = null;
        }
      }
    } else {
      // 如果没有提交状态，说明未提交，不需要获取提交记录
      submission.value = null;
    }
    
    // 重置表单和图片列表（查看详情时应该是空的）
    submissionForm.value.text_content = '';
    imageUrls.value = [];
    fileList.value = [];
    
    // 重置表单和图片列表（查看详情时应该是空的）
    submissionForm.value.text_content = '';
    imageUrls.value = [];
    fileList.value = [];
  } catch (error) {
    const status = error?.response?.status;
    console.error('获取作业信息时发生错误:', error);
    if (status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      userStore.logout();
      router.push({ name: 'Login' });
    } else if (status === 403) {
      ElMessage.error('无权访问该作业');
      router.push({ name: 'StudentHome' });
    } else {
      // 如果已经找到了作业信息，即使后续出错也显示作业
      if (homeworkInfo.value) {
        console.warn('获取作业信息时部分失败，但已找到作业信息，继续显示');
        // 不显示错误消息，让用户可以看到作业
      } else {
        ElMessage.error(error?.response?.data?.error || '获取作业信息失败');
        router.push({ name: 'StudentHome' });
      }
    }
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.homework-view {
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

.homework-view-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.homework-requirement-card,
.grading-card,
.submission-card,
.submission-display-card {
  margin-bottom: 24px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.homework-content {
  line-height: 1.8;
}

.text-content {
  font-size: 14px;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-word;
  margin-bottom: 16px;
}

.requirement-images {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

.requirement-image {
  width: 200px;
  height: 200px;
  border-radius: 8px;
  cursor: pointer;
}

.submission-images {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 16px;
}

.submission-image-wrapper {
  width: 100%;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  position: relative;
}

.annotator-container {
  position: relative;
  width: 100%;
}

.preview-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 40px;
  height: 40px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  transition: background 0.3s;
}

.preview-overlay:hover {
  background: rgba(0, 0, 0, 0.8);
}

.preview-icon {
  color: #fff;
  font-size: 20px;
}

.grading-content {
  padding: 16px 0;
}

.score-section {
  margin-bottom: 16px;
}

.score-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.score-value {
  font-size: 24px;
  font-weight: 600;
  margin-left: 12px;
}

.score-excellent {
  color: #67c23a;
}

.score-good {
  color: #e6a23c;
}

.score-pass {
  color: #409eff;
}

.score-fail {
  color: #f56c6c;
}

.score-ungraded {
  color: #909399;
}

.feedback-section {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.feedback-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
  margin-bottom: 8px;
}

.feedback-text {
  font-size: 14px;
  color: #303133;
  line-height: 1.8;
  white-space: pre-wrap;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.submit-time {
  font-size: 12px;
  color: #909399;
  margin-top: 16px;
  text-align: right;
}

@media (max-width: 768px) {
  .homework-view-container {
    padding: 16px;
  }

  .header-title {
    font-size: 18px;
  }

  .requirement-image,
  .submission-image {
    width: 100%;
    height: auto;
    max-height: 300px;
  }
}
</style>
