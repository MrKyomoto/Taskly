<template>
  <div class="submission-view fade-in">
    <el-header class="header">
      <div class="header-content">
        <el-button text @click="goBack" :icon="ArrowLeft">返回</el-button>
        <h1 class="header-title">查看提交</h1>
        <div></div>
      </div>
    </el-header>

    <div class="submission-view-container">
      <el-skeleton v-if="loading" animated :count="5" />
      <template v-else-if="homeworkInfo">
        <!-- 作业基本信息 -->
        <el-card class="homework-info-card" shadow="never">
          <template #header>
            <div class="card-title">作业信息</div>
          </template>
          <div class="homework-basic-info">
            <h2>{{ homeworkInfo.title }}</h2>
            <p v-if="homeworkInfo.deadline" class="deadline">
              截止时间：{{ formatDateTime(homeworkInfo.deadline) }}
            </p>
          </div>
        </el-card>

        <!-- 提交内容展示 -->
        <el-card v-if="submission" class="submission-display-card" shadow="never">
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
                class="submission-file-wrapper"
              >
                <!-- PDF文件显示 -->
                <template v-if="isPDF(img)">
                  <div class="pdf-viewer-wrapper" @click="previewPDF(img, index)">
                    <div class="pdf-preview-thumbnail">
                      <el-icon class="pdf-icon"><Document /></el-icon>
                      <span class="pdf-name">{{ getFileName(img) }}</span>
                    </div>
                  </div>
                </template>
                <!-- 图片文件显示 -->
                <template v-else>
                  <el-image
                    :src="getImageUrl(typeof img === 'string' ? img : (img.image_url || img.url || img), true)"
                    :preview-src-list="submissionImages.filter(i => !isPDF(i)).map(i => {
                      const url = typeof i === 'string' ? i : (i.image_url || i.url || i);
                      return getImageUrl(url, true);
                    })"
                    :initial-index="submissionImages.filter(i => !isPDF(i)).findIndex(i => {
                      const url = typeof i === 'string' ? i : (i.image_url || i.url || i);
                      const imgUrl = typeof img === 'string' ? img : (img.image_url || img.url || img);
                      return url === imgUrl;
                    })"
                    fit="cover"
                    class="submission-image-wrapper"
                    lazy
                    :preview-teleported="true"
                    :z-index="3000"
                  />
                </template>
              </div>
            </div>
            <div v-if="submission.submit_time" class="submit-time">
              提交时间：{{ formatDateTime(submission.submit_time) }}
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
            <div v-if="gradingInfo.ai_feedback" class="feedback-section">
              <el-alert
                :title="gradingInfo.grader_name ? '老师评语' : 'AI 助教点评'"
                type="info"
                :closable="false"
                show-icon
              >
                <template #default>
                  <div class="feedback-text">{{ gradingInfo.ai_feedback }}</div>
                </template>
              </el-alert>
            </div>
            <!-- 批注图片展示：如果有批注则显示批注，否则显示原图 -->
            <div v-if="submissionImages.length > 0" class="annotation-images">
              <div 
                v-for="(img, index) in submissionImages" 
                :key="index"
                class="annotation-item"
              >
                <div class="annotator-container">
                  <!-- 查找该文件是否有批注 -->
                  <template v-if="hasAnnotationForImage(img)">
                    <!-- PDF文件显示批注 -->
                    <template v-if="isPDF(img)">
                      <PDFAnnotator
                        :pdf-url="getImageUrl(typeof img === 'string' ? img : (img.image_url || img.url || img), true)"
                        :model-value="getAnnotationForImage(img)"
                        :readonly="true"
                      />
                    </template>
                    <!-- 图片文件显示批注 -->
                    <template v-else>
                      <ImageAnnotator
                        :image-url="getImageUrl(typeof img === 'string' ? img : (img.image_url || img.url || img), true)"
                        :model-value="getAnnotationForImage(img)"
                        :readonly="true"
                      />
                    </template>
                  </template>
                  <template v-else>
                    <!-- 没有批注，显示原图或PDF -->
                    <template v-if="isPDF(img)">
                      <div class="pdf-viewer-wrapper" @click="previewPDF(img, index)">
                        <div class="pdf-preview-thumbnail">
                          <el-icon class="pdf-icon"><Document /></el-icon>
                          <span class="pdf-name">{{ getFileName(img) }}</span>
                        </div>
                      </div>
                    </template>
                    <template v-else>
                      <el-image
                        :src="getImageUrl(typeof img === 'string' ? img : (img.image_url || img.url || img), true)"
                        :preview-src-list="submissionImages.filter(i => !isPDF(i)).map(i => {
                          const url = typeof i === 'string' ? i : (i.image_url || i.url || i);
                          return getImageUrl(url, true);
                        })"
                        :initial-index="submissionImages.filter(i => !isPDF(i)).findIndex(i => {
                          const url = typeof i === 'string' ? i : (i.image_url || i.url || i);
                          const imgUrl = typeof img === 'string' ? img : (img.image_url || img.url || img);
                          return url === imgUrl;
                        })"
                        fit="cover"
                        class="submission-image-wrapper"
                        lazy
                        :preview-teleported="true"
                        :z-index="3000"
                      />
                    </template>
                  </template>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 未提交提示 -->
        <el-empty v-else-if="!submission" description="尚未提交该作业" :image-size="100">
          <el-button type="primary" @click="goToHomeworkDetail">去提交</el-button>
        </el-empty>
      </template>
      <el-empty v-else description="作业不存在或无权访问" :image-size="100" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { ArrowLeft, Document } from '@element-plus/icons-vue';
import { fetchHomeworkSubmission, fetchCourseHomeworks, fetchStudentCourses } from '@/api/student';
import { useUserStore } from '@/store/user';
import { formatDateTime as formatDateUtil } from '@/utils/date-formatter';
import { logger } from '@/utils/logger';
import { getImageUrl, parseImageUrls } from '@/utils/image';
import ImageAnnotator from '@/components/ImageAnnotator.vue';

const router = useRouter();
const route = useRoute();
const userStore = useUserStore();

const loading = ref(false);
const homeworkInfo = ref(null);
const submission = ref(null);
const gradingInfo = ref(null);

// 获取作业ID
const homeworkId = computed(() => parseInt(route.params.id));

// 解析提交图片
const submissionImages = computed(() => {
  if (!submission.value?.image_urls) return [];
  let images = [];
  if (Array.isArray(submission.value.image_urls)) {
    images = submission.value.image_urls;
  } else {
    images = parseImageUrls(submission.value.image_urls);
  }
  return images.map(img => {
    if (typeof img === 'string') return img;
    if (typeof img === 'object' && img !== null) {
      return img.image_url || img.url || String(img);
    }
    return String(img);
  });
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

// 获取文件名
const getFileName = (url) => {
  if (!url) return '文件';
  const urlStr = typeof url === 'string' ? url : (url.image_url || url.url || String(url));
  const parts = urlStr.split('/');
  return parts[parts.length - 1] || '文件';
};

// 预览PDF
const previewPDF = (img, index) => {
  const fileUrl = getImageUrl(typeof img === 'string' ? img : (img.image_url || img.url || img), true);
  
  // 创建预览对话框
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
    z-index: 10000;
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
  
  // PDF预览：使用iframe
  const iframe = document.createElement('iframe');
  iframe.src = fileUrl;
  iframe.style.cssText = `
    width: 100%;
    height: 100%;
    border: none;
    background: #fff;
  `;
  contentWrapper.appendChild(iframe);
  
  // 添加在新窗口打开的按钮
  const openBtn = document.createElement('button');
  openBtn.textContent = '在新窗口打开';
  openBtn.style.cssText = `
    position: absolute;
    bottom: 20px;
    right: 20px;
    padding: 10px 20px;
    background: #409EFF;
    color: #fff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    z-index: 10000;
  `;
  openBtn.onclick = () => {
    window.open(fileUrl, '_blank');
  };
  contentWrapper.appendChild(openBtn);
  
  viewer.appendChild(closeBtn);
  viewer.appendChild(contentWrapper);
  document.body.appendChild(viewer);
  
  const close = () => {
    if (document.body.contains(viewer)) {
      document.body.removeChild(viewer);
    }
    document.removeEventListener('keydown', handleEsc);
  };
  
  closeBtn.addEventListener('click', close);
  viewer.addEventListener('click', (e) => {
    if (e.target === viewer) {
      close();
    }
  });
  
  // ESC 键关闭
  const handleEsc = (e) => {
    if (e.key === 'Escape') {
      close();
    }
  };
  document.addEventListener('keydown', handleEsc);
};

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

// 跳转到作业详情页
const goToHomeworkDetail = () => {
  router.push({ name: 'HomeworkView', params: { id: homeworkId.value } });
};

// 格式化日期时间
const formatDateTime = (dateString) => {
  return formatDateUtil(dateString, 'YYYY-MM-DD HH:mm');
};

// 获取数据
const fetchData = async () => {
  loading.value = true;
  try {
    // 获取课程列表以找到作业所属的课程
    const coursesResponse = await fetchStudentCourses();
    
    // 确保正确获取课程列表
    let courseList = [];
    if (coursesResponse?.data) {
      // 如果 data 是数组，直接使用
      if (Array.isArray(coursesResponse.data)) {
        courseList = coursesResponse.data;
      } 
      // 如果 data 有 course_list 属性
      else if (coursesResponse.data.course_list && Array.isArray(coursesResponse.data.course_list)) {
        courseList = coursesResponse.data.course_list;
      }
    }
    
    let foundHomework = null;
    let courseId = null;

    // 遍历所有课程查找作业
    for (const course of courseList) {
      try {
        const homeworksResponse = await fetchCourseHomeworks(course.id);
        let homeworkList = [];
        if (homeworksResponse?.data) {
          // 如果 data 是数组，直接使用
          if (Array.isArray(homeworksResponse.data)) {
            homeworkList = homeworksResponse.data;
          }
          // 如果 data 有 homework_list 属性
          else if (homeworksResponse.data.homework_list && Array.isArray(homeworksResponse.data.homework_list)) {
            homeworkList = homeworksResponse.data.homework_list;
          }
        }
        
        if (homeworkList.length > 0) {
          foundHomework = homeworkList.find(hw => hw.id === homeworkId.value);
          if (foundHomework) {
            courseId = course.id;
            break;
          }
        }
      } catch (error) {
        // 单个课程获取失败，继续下一个
        console.warn(`获取课程 ${course.id} 的作业失败:`, error);
        continue;
      }
    }

    if (!foundHomework) {
      ElMessage.error('作业不存在或无权访问');
      router.push({ name: 'StudentHome' });
      return;
    }

    if (!courseId) {
      ElMessage.error('无法确定作业所属课程');
      router.push({ name: 'StudentHome' });
      return;
    }

    homeworkInfo.value = foundHomework;

    // 获取提交记录
    if (foundHomework.submission) {
      try {
        const submissionResponse = await fetchHomeworkSubmission(courseId, homeworkId.value);
        if (submissionResponse.data) {
          submission.value = submissionResponse.data.submission;
          gradingInfo.value = submissionResponse.data.grading || null;
        }
      } catch (error) {
        if (error?.response?.status !== 404) {
          logger.error('获取提交记录失败:', error);
        }
      }
    }
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
      ElMessage.error(error?.response?.data?.error || '获取作业信息失败');
      router.push({ name: 'StudentHome' });
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
.submission-view {
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

.submission-view-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.homework-info-card,
.submission-display-card,
.grading-card {
  margin-bottom: 24px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.homework-basic-info h2 {
  margin: 0 0 12px 0;
  font-size: 20px;
  color: #303133;
}

.deadline {
  color: #606266;
  font-size: 14px;
  margin: 0;
}

.submission-content {
  padding: 16px 0;
}

.text-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  color: #606266;
  margin-bottom: 16px;
}

.submission-images {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
}

.submission-file-wrapper {
  margin-bottom: 16px;
}

.submission-image-wrapper {
  width: 200px;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
}

.pdf-viewer-wrapper {
  width: 200px;
  height: 200px;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #f5f7fa;
}

.pdf-viewer-wrapper:hover {
  border-color: #409EFF;
  background: #ecf5ff;
}

.pdf-preview-thumbnail {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.pdf-icon {
  font-size: 48px;
  color: #409EFF;
}

.pdf-name {
  font-size: 12px;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.submit-time {
  margin-top: 16px;
  color: #909399;
  font-size: 14px;
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

.score-unit {
  font-size: 16px;
  margin-left: 4px;
}

.grader-info {
  margin-bottom: 16px;
}

.feedback-section {
  margin-bottom: 16px;
}

.feedback-text {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

.annotation-images {
  margin-top: 24px;
}

.annotation-item {
  margin-bottom: 24px;
}

.annotator-container {
  position: relative;
  width: 100%;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
</style>

