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
          </div>
        </el-card>

        <!-- 参考文件（老师上传的附件）- 单独卡片 -->
        <el-card v-if="homeworkAttachments.length > 0" class="reference-files-card" shadow="never">
          <template #header>
            <div class="card-title">参考文件</div>
            <div class="card-subtitle">老师发布的参考材料</div>
          </template>
          <div class="attachments-list">
            <div 
              v-for="(file, index) in homeworkAttachments" 
              :key="index"
              class="attachment-item"
            >
              <!-- 图片文件：可以在网页查看 -->
              <template v-if="isImage(file)">
                <el-image
                  :src="getImageUrl(file, true)"
                  :preview-src-list="homeworkAttachments.filter(f => isImage(f)).map(f => getImageUrl(f, true))"
                  :initial-index="homeworkAttachments.filter(f => isImage(f)).findIndex(f => f === file)"
                  fit="cover"
                  class="attachment-image"
                  lazy
                  :preview-teleported="true"
                />
                <div class="attachment-name">{{ getFileName(file) }}</div>
              </template>
              <!-- PDF文件：提供内嵌预览和下载 -->
              <template v-else-if="isPDF(file)">
                <div class="attachment-pdf-wrapper">
                  <div class="pdf-header">
                    <el-icon :size="24" class="pdf-icon"><Document /></el-icon>
                    <div class="pdf-name">{{ getFileName(file) }}</div>
                  </div>
                  <div class="pdf-viewer-container">
                    <iframe
                      :src="getImageUrl(file, true)"
                      class="pdf-viewer-iframe"
                      frameborder="0"
                    />
                  </div>
                  <div class="pdf-actions">
                    <el-button 
                      type="primary" 
                      size="small"
                      @click="previewPDF(file)"
                    >
                      <el-icon><ZoomIn /></el-icon>
                      在新窗口打开
                    </el-button>
                    <el-button 
                      type="primary" 
                      size="small"
                      @click="downloadFile(file)"
                    >
                      <el-icon><Download /></el-icon>
                      下载
                    </el-button>
                  </div>
                </div>
              </template>
              <!-- 其他文件类型 -->
              <template v-else>
                <div class="attachment-other">
                  <el-icon :size="48"><Document /></el-icon>
                  <div class="other-info">
                    <div class="other-name">{{ getFileName(file) }}</div>
                    <el-button 
                      type="primary" 
                      size="small"
                      @click="downloadFile(file)"
                    >
                      <el-icon><Download /></el-icon>
                      下载文件
                    </el-button>
                  </div>
                </div>
              </template>
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
                id="homework-text-content"
                name="text_content"
                v-model="submissionForm.text_content"
                type="textarea"
                :rows="6"
                placeholder="请输入作业内容..."
                :disabled="isOverdue"
                @keydown.enter.ctrl="handleSubmit"
              />
            </el-form-item>
            <el-form-item label="文件附件">
              <el-upload
                id="homework-file-upload"
                name="file"
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
                list-type="text"
                :limit="10"
                accept="image/*,application/pdf"
                :auto-upload="true"
                :show-file-list="true"
                :preview-teleported="true"
              >
                <el-button type="primary">
                <el-icon><Plus /></el-icon>
                  选择文件
                </el-button>
              </el-upload>
              <div class="upload-tip">
                支持上传图片（JPG、PNG、GIF等）和PDF文件，单个文件不超过10MB，最多10个文件
              </div>
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
            <el-empty v-else-if="submissionImages.length === 0" description="暂无提交内容" :image-size="80" />
            <div v-if="submissionImages.length > 0" class="submission-images">
              <div 
                v-for="(img, index) in submissionImages" 
                :key="index"
                class="submission-image-wrapper"
              >
                <div class="annotator-container">
                  <!-- PDF文件显示 -->
                  <template v-if="isPDF(img)">
                    <div class="pdf-viewer-wrapper">
                      <iframe
                        :src="getImageUrl(typeof img === 'string' ? img : (img.image_url || img.url || img), true)"
                        class="pdf-viewer"
                        frameborder="0"
                      />
                      <div class="pdf-download">
                        <el-button 
                          type="primary" 
                          size="small"
                          @click="window.open(getImageUrl(typeof img === 'string' ? img : (img.image_url || img.url || img), true), '_blank')"
                        >
                          在新窗口打开
                        </el-button>
                      </div>
                    </div>
                  </template>
                  <!-- 图片文件显示 -->
                  <template v-else-if="isImage(img)">
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
                        :preview-src-list="submissionImages.filter(i => isImage(i)).map(i => {
                        const url = typeof i === 'string' ? i : (i.image_url || i.url || i);
                        return getImageUrl(url, true);
                      })"
                        :initial-index="submissionImages.filter(i => isImage(i)).findIndex(i => {
                          const url = typeof i === 'string' ? i : (i.image_url || i.url || i);
                          const imgUrl = typeof img === 'string' ? img : (img.image_url || img.url || img);
                          return url === imgUrl;
                        })"
                      fit="cover"
                      class="submission-image-display"
                      lazy
                      :preview-teleported="true"
                      :z-index="3000"
                    />
                  </template>
                  </template>
                  <!-- 其他文件类型 -->
                  <template v-else>
                    <div class="file-viewer-wrapper">
                      <el-icon :size="48"><Document /></el-icon>
                      <p>{{ typeof img === 'string' ? img : (img.image_url || img.url || img) }}</p>
                      <el-button 
                        type="primary" 
                        size="small"
                        @click="window.open(getImageUrl(typeof img === 'string' ? img : (img.image_url || img.url || img), true), '_blank')"
                      >
                        下载文件
                      </el-button>
                    </div>
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
      <el-empty v-else description="作业不存在或无权访问" :image-size="100">
        <el-button type="primary" @click="goBack">返回</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { useRouter, useRoute, onBeforeRouteLeave } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { ArrowLeft, Plus, ZoomIn, Document, UploadFilled, Download } from '@element-plus/icons-vue';
import { fetchHomeworkSubmission, submitHomework, uploadHomeworkImage } from '@/api/student';
import { fetchCourseHomeworks, fetchStudentCourses } from '@/api/student';
import { useUserStore } from '@/store/user';
import { getImageUrl, parseImageUrls } from '@/utils/image';
import ImageAnnotator from '@/components/ImageAnnotator.vue';
import { formatDateTime as formatDateUtil } from '@/utils/date-formatter';
import { logger } from '@/utils/logger';

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

// 判断文件是否为PDF
const isPDF = (url) => {
  if (!url) return false;
  const urlStr = typeof url === 'string' ? url : (url.image_url || url.url || String(url));
  return urlStr.toLowerCase().endsWith('.pdf') || urlStr.toLowerCase().includes('.pdf');
};

// 判断文件是否为图片
const isImage = (url) => {
  if (!url) return false;
  const urlStr = typeof url === 'string' ? url : (url.image_url || url.url || String(url));
  const lowerUrl = urlStr.toLowerCase();
  return lowerUrl.endsWith('.jpg') || lowerUrl.endsWith('.jpeg') || 
         lowerUrl.endsWith('.png') || lowerUrl.endsWith('.gif') || 
         lowerUrl.endsWith('.webp') || lowerUrl.endsWith('.bmp');
};

// 根据分数获取颜色
const getScoreColor = (score, maxScore = 100) => {
  if (!score && score !== 0) return '#909399';
  const percentage = (score / maxScore) * 100;
  if (percentage >= 90) return '#67C23A'; // 绿色 - 优秀
  if (percentage >= 80) return '#409EFF'; // 蓝色 - 良好
  if (percentage >= 60) return '#E6A23C'; // 橙色 - 及格
  return '#F56C6C'; // 红色 - 不及格
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

// 解析作业附件（包括图片和PDF）
const homeworkAttachments = computed(() => {
  if (!homeworkInfo.value) {
    console.log('作业附件：homeworkInfo 为空');
    return [];
  }
  
  const imageUrls = homeworkInfo.value.image_urls;
  console.log('作业附件：原始 image_urls 数据', {
    image_urls: imageUrls,
    type: typeof imageUrls,
    isArray: Array.isArray(imageUrls),
    homeworkInfo: homeworkInfo.value
  });
  
  if (!imageUrls) {
    console.log('作业附件：image_urls 为空或未定义');
    return [];
  }
  
  const parsed = parseImageUrls(imageUrls);
  console.log('作业附件解析结果：', {
    parsed: parsed,
    length: parsed.length,
    isArray: Array.isArray(parsed)
  });
  return parsed;
});

// 兼容旧代码：保留 homeworkImages 计算属性
const homeworkImages = computed(() => {
  return homeworkAttachments.value.filter(file => isImage(file));
});

// 获取文件名
const getFileName = (url) => {
  if (!url) return '未知文件';
  const urlStr = typeof url === 'string' ? url : String(url);
  const parts = urlStr.split('/');
  const fileName = parts[parts.length - 1];
  // 移除可能的查询参数
  return fileName.split('?')[0] || '文件';
};

// 下载文件
const downloadFile = (file) => {
  const fileUrl = typeof file === 'string' ? file : (file.image_url || file.url || file);
  const fullUrl = getImageUrl(fileUrl, true);
  
  // 创建一个临时的 a 标签来触发下载
  const link = document.createElement('a');
  link.href = fullUrl;
  link.download = getFileName(fileUrl);
  link.target = '_blank';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

// 预览PDF文件
const previewPDF = (file) => {
  const fileUrl = typeof file === 'string' ? file : (file.image_url || file.url || file);
  const fullUrl = getImageUrl(fileUrl, true);
  // 在新窗口打开PDF
  window.open(fullUrl, '_blank');
};

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
  // 使用 router.back() 返回到上一个页面
  // 如果浏览器历史记录中没有上一个页面，则返回到主页
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push({ name: 'StudentHome' });
  }
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
  return formatDateUtil(dateString, 'YYYY-MM-DD HH:mm');
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
  const isPDF = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
  const isLt10M = file.size / 1024 / 1024 < 10;

  if (!isImage && !isPDF) {
    ElMessage.error('只能上传图片或PDF文件！');
    return false;
  }
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB！');
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
    
    const fileType = isPDF(file) ? 'PDF' : '图片';
    ElMessage.success(`${fileType}上传成功`);
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
  logger.error('Upload error:', error);
  // 标记文件为失败状态
  const fileIndex = fileList.value.findIndex(f => f.uid === file.uid);
  if (fileIndex > -1) {
    fileList.value[fileIndex].status = 'fail';
  }
};

// 预览上传的文件（图片或PDF）
const handlePreview = (file) => {
  // 获取文件 URL（优先使用 file.url，如果没有则从 response 中获取）
  let fileUrl = file.url;
  if (!fileUrl && file.response) {
    if (file.response.image_urls && Array.isArray(file.response.image_urls) && file.response.image_urls.length > 0) {
      fileUrl = file.response.image_urls[file.response.image_urls.length - 1];
    } else if (file.response.image_url) {
      fileUrl = file.response.image_url;
    }
    // 如果是相对路径，需要转换为完整 URL（包含 token）
    if (fileUrl && !fileUrl.startsWith('http')) {
      fileUrl = getImageUrl(fileUrl, true);
    }
  }
  
  if (!fileUrl) {
    ElMessage.warning('无法预览该文件');
    return;
  }
  
  // 判断文件类型
  const fileName = file.name || fileUrl;
  const isPDFFile = isPDF(fileName) || file.type === 'application/pdf';
  const isImageFile = isImage(fileName) || (file.type && file.type.startsWith('image/'));
  
  // PDF文件直接在新窗口打开，不创建预览对话框
  if (isPDFFile) {
    window.open(fileUrl, '_blank');
    return;
  }
  
  // 图片文件使用全屏预览
  if (!isImageFile) {
    ElMessage.warning('该文件类型不支持预览');
    return;
  }
  
  // 创建预览对话框（仅用于图片）
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
    flex-direction: column;
    align-items: center;
    justify-content: center;
  `;
  
  // 关闭按钮
  const closeBtn = document.createElement('div');
  closeBtn.className = 'preview-close-btn';
  closeBtn.innerHTML = '✕';
  closeBtn.style.cssText = `
    position: absolute;
    top: 20px;
    right: 20px;
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 24px;
    cursor: pointer;
    transition: background 0.3s;
    z-index: 10001;
  `;
  closeBtn.onmouseover = () => { closeBtn.style.background = 'rgba(255, 255, 255, 0.3)'; };
  closeBtn.onmouseout = () => { closeBtn.style.background = 'rgba(255, 255, 255, 0.2)'; };
  
  // 预览内容容器
  const contentWrapper = document.createElement('div');
  contentWrapper.style.cssText = `
    width: 95%;
    height: 95%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  `;
  
  if (isImageFile) {
    // 图片预览
    const img = document.createElement('img');
    img.src = fileUrl;
    img.style.cssText = `
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    `;
    contentWrapper.appendChild(img);
  } else {
    // 其他文件类型，显示下载提示
    const message = document.createElement('div');
    message.style.cssText = `
      color: #fff;
      font-size: 18px;
      text-align: center;
    `;
    message.innerHTML = `
      <p>该文件类型不支持预览</p>
      <button onclick="window.open('${fileUrl}', '_blank')" style="
        margin-top: 20px;
        padding: 10px 20px;
        background: #409EFF;
        color: #fff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
      ">下载文件</button>
    `;
    contentWrapper.appendChild(message);
  }
  
  viewer.appendChild(closeBtn);
  viewer.appendChild(contentWrapper);
  document.body.appendChild(viewer);
  
  const close = (e) => {
    // 阻止事件冒泡，避免触发其他点击事件
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (document.body.contains(viewer)) {
      document.body.removeChild(viewer);
    }
    document.removeEventListener('keydown', handleEsc);
  };
  
  closeBtn.addEventListener('click', (e) => {
    close(e);
  });
  viewer.addEventListener('click', (e) => {
    if (e.target === viewer) {
      close(e);
    }
  });
  
  // ESC 键关闭
  const handleEsc = (e) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      e.stopPropagation();
      close();
    }
  };
  document.addEventListener('keydown', handleEsc);
};

// 提交作业
const handleSubmit = async () => {
  if (!submissionFormRef.value) return;

  // 验证至少要有文字或文件（图片/PDF）
  if (!submissionForm.value.text_content.trim() && imageUrls.value.length === 0) {
    ElMessage.warning('请至少输入文字内容或上传一个文件（图片或PDF）');
    return;
  }
  
  // 验证是否有正在上传的文件
  const uploadingFiles = fileList.value.filter(f => f.status === 'uploading');
  if (uploadingFiles.length > 0) {
    ElMessage.warning('请等待文件上传完成后再提交');
    return;
  }
  
  // 验证是否有上传失败的文件
  const failedFiles = fileList.value.filter(f => f.status === 'fail');
  if (failedFiles.length > 0) {
    ElMessage.warning('有文件上传失败，请删除失败的文件或重新上传');
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
          console.log('找到作业，原始数据：', {
            id: hw.id,
            title: hw.title,
            image_urls: hw.image_urls,
            image_urls_type: typeof hw.image_urls,
            image_urls_isArray: Array.isArray(hw.image_urls),
            full_hw: hw
          });
          foundHomework = hw;
          foundCourseId = course.id;
          break;
        }
      } catch (error) {
        // 记录错误但继续查找下一个课程
        logger.warn(`获取课程 ${course.id} 的作业列表失败:`, error);
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
          logger.warn('提交记录不存在（可能已删除）:', error);
          submission.value = null;
        } else {
          // 其他错误，记录但不阻止页面显示
          logger.error('获取提交详情失败:', error);
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
    logger.error('获取作业信息时发生错误:', error);
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
        logger.warn('获取作业信息时部分失败，但已找到作业信息，继续显示');
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

// 事件监听器清理函数
let cleanupEscHandler = null;

onMounted(() => {
  fetchData();
  // 设置ESC键监听（如果需要）
  // cleanupEscHandler 在需要时设置
});

onBeforeUnmount(() => {
  // 清理事件监听器
  if (cleanupEscHandler) {
    cleanupEscHandler();
  }
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
.submission-display-card,
.view-submission-card {
  margin-bottom: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 12px;
}

.homework-requirement-card:hover,
.grading-card:hover,
.submission-card:hover,
.submission-display-card:hover,
.view-submission-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
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
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  margin-bottom: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
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
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.requirement-image:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

/* 参考附件样式 */
.requirement-attachments {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.attachments-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.attachments-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.attachment-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fff;
  transition: all 0.3s ease;
  min-width: 180px;
}

.attachment-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.attachment-image {
  width: 200px;
  height: 200px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.attachment-image:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.attachment-name {
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
  text-align: center;
  word-break: break-all;
  max-width: 200px;
}

.attachment-pdf-wrapper {
  width: 100%;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  margin-bottom: 16px;
}

.pdf-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.pdf-icon {
  color: #f56c6c;
}

.pdf-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  flex: 1;
}

.pdf-viewer-container {
  width: 100%;
  height: 600px;
  margin-bottom: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.pdf-viewer-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.pdf-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.attachment-other {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 16px;
}

.other-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.other-name {
  font-size: 12px;
  color: #606266;
  text-align: center;
  word-break: break-all;
  max-width: 200px;
}

/* 参考文件卡片样式 */
.reference-files-card {
  margin-top: 20px;
}

.reference-files-card .card-subtitle {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
  margin-top: 4px;
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
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.submission-image-wrapper:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
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
  margin-bottom: 20px;
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.score-section:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
  color: #606266;
  line-height: 1.8;
  white-space: pre-wrap;
  padding: 12px;
  background: #ffffff;
  border-radius: 8px;
  border-left: 3px solid #409EFF;
  margin-top: 8px;
}

.upload-tip {
  font-size: 12px;
  color: #606266;
  margin-top: 12px;
  padding: 10px 14px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  border-left: 3px solid #409EFF;
  line-height: 1.6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.upload-tip::before {
  content: '💡 ';
  margin-right: 4px;
}

.submit-time {
  font-size: 12px;
  color: #909399;
  margin-top: 16px;
  text-align: right;
}

.pdf-viewer-wrapper {
  width: 100%;
  min-height: 600px;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.pdf-viewer {
  width: 100%;
  flex: 1;
  min-height: 600px;
  border: none;
}

.pdf-download {
  padding: 12px;
  background: #fff;
  border-top: 1px solid #ebeef5;
  text-align: center;
}

.file-viewer-wrapper {
  padding: 40px;
  text-align: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8f0f8 100%);
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.file-viewer-wrapper:hover {
  background: linear-gradient(135deg, #e8f0f8 0%, #dbeafe 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.file-viewer-wrapper p {
  color: #606266;
  font-size: 14px;
  word-break: break-all;
  font-weight: 500;
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
