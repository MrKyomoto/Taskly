<template>
  <div class="grading-view">
      <el-header class="grading-header">
        <div class="grading-header-content">
          <div class="header-left">
            <el-button text @click="goBack" :icon="ArrowLeft" class="header-back-btn">返回课程</el-button>
          </div>
          <div class="header-center">
            <span class="header-current-student">
              当前学生：{{ currentSubmission?.student_name || '未选择' }}
            </span>
            <el-tag v-if="isReadOnly" type="info" size="small" style="margin-left: 12px;">
              查看模式（成绩已发布）
            </el-tag>
          </div>
          <div class="header-right">
            <span class="header-progress">
              已批改 {{ gradedCount }} / {{ totalCount }}
            </span>
          </div>
        </div>
      </el-header>
  
      <el-container class="grading-container" v-loading="loading">
        <!-- 左侧：学生列表 -->
        <el-aside width="240px" class="student-list-panel">
          <div class="filter-section">
            <!-- 搜索框 -->
            <div class="search-box">
              <el-input
                v-model="searchQuery"
                placeholder="搜索学生姓名或学号..."
                clearable
                size="small"
                :prefix-icon="Search"
                @keyup.enter.stop
              />
            </div>
            <el-radio-group v-model="filterType" size="small">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="pending">待批改</el-radio-button>
              <el-radio-button label="graded">已批改</el-radio-button>
              <el-radio-button label="unsubmitted">未提交</el-radio-button>
            </el-radio-group>
            <div v-if="filterType === 'unsubmitted' && unsubmittedStudents.length > 0 && !isReadOnly" class="batch-action">
              <el-button type="danger" size="small" @click="handleBatchZeroScore" :loading="batchGrading">
                一键0分
              </el-button>
            </div>
          </div>
          
          <div class="student-list">
            <div
              v-for="submission in filteredSubmissions"
              :key="submission.id || `unsubmitted-${submission.student_id}`"
              :class="['student-item', { active: currentSubmissionId === (submission.id || `unsubmitted-${submission.student_id}`) }]"
              @click="selectStudent(submission)"
            >
              <div class="student-info">
                <div class="student-name">{{ submission.student_name }}</div>
                <div class="student-no">{{ submission.student_no }}</div>
              </div>
              <el-tag 
                :type="!submission.has_submitted ? 'danger' : (submission.is_graded ? 'success' : 'warning')" 
                size="small"
              >
                {{ !submission.has_submitted ? '未提交' : (submission.is_graded ? '已批改' : '待批改') }}
              </el-tag>
            </div>
            <el-empty v-if="filteredSubmissions.length === 0" description="暂无数据" :image-size="80" />
          </div>
        </el-aside>
  
        <!-- 中间：作业内容展示区 -->
        <el-main class="content-panel">
          <div v-if="currentSubmission" class="submission-content">
            <!-- 文本内容 - 始终显示 -->
            <el-card class="text-content-card" shadow="never">
              <template #header>
                <div class="card-header">
                  <span>学生提交的文本内容</span>
                  <el-tag v-if="!currentSubmission.text_content" type="info" size="small">未提交文本</el-tag>
                </div>
              </template>
              <div v-if="currentSubmission.text_content" class="text-content">{{ currentSubmission.text_content }}</div>
              <div v-else class="text-content-empty">
                <el-empty description="该学生未提交文本内容" :image-size="60" />
              </div>
            </el-card>
  
            <!-- 文件批注舞台 - 支持多张图片、多个PDF，以及图片和PDF混合提交 -->
            <div class="image-stage" v-if="processedImageUrls.length > 0">
              <transition-group name="fade-in" tag="div">
                <div
                  v-for="(imageUrl, index) in processedImageUrls"
                  :key="`file-${index}-${imageUrl}`"
                  class="image-stage-item"
                >
                  <!-- 文件类型标签 -->
                  <div class="file-header">
                    <el-tag 
                      :type="isPDF(imageUrl) ? 'danger' : 'primary'" 
                      size="small"
                      effect="plain"
                    >
                      {{ isPDF(imageUrl) ? 'PDF文档' : '图片' }} {{ index + 1 }} / {{ processedImageUrls.length }}
                    </el-tag>
                  </div>
                  <div class="image-stage-inner">
                    <!-- PDF文件显示（支持批注） -->
                    <template v-if="isPDF(imageUrl)">
                      <PDFAnnotator
                        :pdf-url="getImageUrl(imageUrl, true)"
                        :model-value="annotationData[imageUrl] || { version: 2, pages: {} }"
                        :readonly="isReadOnly"
                        @update:model-value="(value) => {
                          if (!isReadOnly && (!annotationData[imageUrl] || JSON.stringify(annotationData[imageUrl]) !== JSON.stringify(value))) {
                            annotationData[imageUrl] = value;
                          }
                        }"
                      />
                    </template>
                    <!-- 图片文件显示（支持批注） -->
                    <template v-else>
                    <ImageAnnotator
                      :image-url="getImageUrl(imageUrl, true)"
                      :model-value="annotationData[imageUrl] || { version: 1, elements: [] }"
                      :readonly="isReadOnly"
                      @update:model-value="(value) => {
                        if (!isReadOnly && (!annotationData[imageUrl] || JSON.stringify(annotationData[imageUrl]) !== JSON.stringify(value))) {
                          annotationData[imageUrl] = value;
                        }
                      }"
                    />
                    </template>
                  </div>
                </div>
              </transition-group>
            </div>
  
            <el-empty 
              v-if="!currentSubmission.text_content && processedImageUrls.length === 0"
              description="该学生未提交任何内容"
              :image-size="100"
            />
          </div>
          <el-empty v-else description="请从左侧选择学生" :image-size="100" />
        </el-main>
  
        <!-- 右侧：评分控制区 -->
        <el-aside width="300px" class="grading-panel">
          <div v-if="currentSubmission" class="grading-content">
            <!-- 学生信息卡片 -->
            <el-card class="student-info-card" shadow="never">
              <div class="student-basic-info">
                <div class="student-name-large">{{ currentSubmission.student_name }}</div>
                <div class="student-no-small">{{ currentSubmission.student_no }}</div>
                <div v-if="currentSubmission.grading?.grader_name" class="grader-info">
                  批改人：{{ currentSubmission.grading.grader_name }}
                </div>
              </div>
            </el-card>
  
            <!-- 评分表单 -->
            <el-card class="grading-form-card" shadow="never">
              <el-form :model="gradingForm" :rules="gradingRules" ref="gradingFormRef" label-width="60px">
                <el-form-item label="分数" prop="score" required>
                  <el-input-number
                    v-model="gradingForm.score"
                    :min="0"
                    :max="homeworkInfo?.max_score || 100"
                    :step="0.5"
                    :precision="2"
                    style="width: 100%"
                    :disabled="isReadOnly"
                    @keyup.enter="handleSaveAndNext"
                  />
                  <div class="form-tip" v-if="homeworkInfo?.max_score">
                    本次作业分数上限：{{ homeworkInfo.max_score }}分
                  </div>
                </el-form-item>
                <el-form-item label="评语">
                  <el-input
                    v-model="gradingForm.feedback"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入评语..."
                    :disabled="isReadOnly"
                    @keydown.enter.ctrl="handleSaveAndNext"
                  />
                </el-form-item>
                <el-form-item v-if="!isReadOnly">
                  <el-button 
                    type="success" 
                    :icon="MagicStick"
                    @click="handleAIGenerate"
                    :loading="aiGenerating"
                    style="width: 100%;"
                  >
                    ✨ AI 一键预批改
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
  
            <!-- 操作按钮 -->
            <div class="action-buttons" v-if="!isReadOnly">
              <el-button 
                type="default" 
                @click="handleSaveOnly"
                :loading="saving"
              >
                仅保存
              </el-button>
              <el-button 
                type="primary" 
                @click="handleSaveAndNext"
                :loading="saving"
              >
                保存并批改下一个
              </el-button>
              <div class="shortcut-hint">提示：在评分框或空白处按 Enter 键快速提交</div>
            </div>
            <div v-else class="readonly-notice">
              <el-alert
                type="info"
                :closable="false"
                show-icon
              >
                <template #title>
                  <span>成绩已发布，当前为查看模式，无法修改批改内容</span>
                </template>
              </el-alert>
            </div>

            <!-- 成绩统计（仅当本次作业已全部批改完成时显示） -->
            <el-card
              v-if="scoreStats && isAllGraded"
              class="score-stats-card"
              shadow="never"
              style="margin-top: 12px;"
            >
              <template #header>
                <div class="card-header">
                  <span>成绩统计（本次作业）</span>
                </div>
              </template>
              <div class="stats-summary">
                <div>最高分：<strong>{{ scoreStats.max }}</strong></div>
                <div>最低分：<strong>{{ scoreStats.min }}</strong></div>
                <div>平均分：<strong>{{ scoreStats.avg }}</strong></div>
                <div>参与人数：<strong>{{ scoreStats.total }}</strong></div>
              </div>
              <div class="stats-chart" v-if="scoreStats && scoreStats.buckets && scoreStats.buckets.length > 0">
                <div
                  v-for="bucket in scoreStats.buckets"
                  :key="bucket.label"
                  class="stats-bar-item"
                  :class="{ active: selectedScoreBucket && selectedScoreBucket.label === bucket.label }"
                  @click="toggleScoreBucket(bucket)"
                >
                  <div class="stats-bar-count">{{ bucket.count }}</div>
                  <div
                    class="stats-bar"
                    :style="{
                      height: scoreStats.maxCount > 0
                        ? Math.max((bucket.count / scoreStats.maxCount) * 80, bucket.count > 0 ? 10 : 0) + '%'
                        : (bucket.count > 0 ? '10%' : '0%')
                    }"
                  ></div>
                  <div class="stats-bar-label">{{ bucket.label }}</div>
                </div>
              </div>
              <div v-else class="stats-chart-empty">
                <el-empty description="暂无成绩数据" :image-size="60" />
              </div>
            </el-card>
          </div>
          <el-empty v-else description="请选择学生" :image-size="80" />
        </el-aside>
      </el-container>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import { ElMessage, ElMessageBox } from 'element-plus';
  import { ArrowLeft, MagicStick, InfoFilled, Search } from '@element-plus/icons-vue';
  import { useUserStore } from '@/store/user';
  import { fetchStudentSubmissions, gradeSubmission, gradeUnsubmittedStudent, fetchCourseHomeworks } from '@/api/teacher';
  import { generateAIFeedback } from '@/api/ai';
  import ImageAnnotator from '@/components/ImageAnnotator.vue';
  import PDFAnnotator from '@/components/PDFAnnotator.vue';
  import { getImageUrl, parseImageUrls } from '@/utils/image';
import { logger } from '@/utils/logger';
  
  const router = useRouter();
  const route = useRoute();
  const userStore = useUserStore();
  
  const loading = ref(false);
  const saving = ref(false);
  const submissions = ref([]);
  const currentSubmissionId = ref(null);
  const filterType = ref('all');
  const annotationData = ref({});
  const gradingForm = ref({
    score: null,
    feedback: '',
  });
  // 是否有未保存的批改修改（分数 / 评语 / 批注）
  const hasUnsavedChanges = ref(false);
  // 是否处于初始化 / 加载数据阶段（此时的表单和批注变化不应视为“修改”）
  const isInitializing = ref(false);
  const aiGenerating = ref(false);
  const batchGrading = ref(false);
  const searchQuery = ref('');
  const gradingFormRef = ref(null);
  const homeworkInfo = ref(null);  // 存储作业信息，包括max_score
  const gradedCount = computed(() => submissions.value.filter(s => s.is_graded).length);
  const totalCount = computed(() => submissions.value.length);
  
  // 是否只读模式（成绩已发布时只读）
  const isReadOnly = computed(() => {
    return homeworkInfo.value?.grades_published === true;
  });
  
  // AI生成评语
  const handleAIGenerate = async () => {
    if (isReadOnly.value) {
      ElMessage.warning('成绩已发布，无法修改');
      return;
    }
    if (!currentSubmission.value) {
      ElMessage.warning('请先选择学生');
      return;
    }
    
    if (!currentSubmission.value.has_submitted) {
      ElMessage.warning('该学生未提交作业，无法生成AI评语');
      return;
    }
    
    aiGenerating.value = true;
    try {
      const response = await generateAIFeedback({
        submission_id: currentSubmission.value.id,
        text_content: currentSubmission.value.text_content || '',
        image_urls: currentSubmission.value.image_urls || []
      });
      
      if (response.data?.feedback) {
        gradingForm.value.feedback = response.data.feedback;
        hasUnsavedChanges.value = true;
        ElMessage.success('AI评语生成成功');
      } else {
        ElMessage.warning('AI评语生成失败，请重试');
      }
    } catch (error) {
      logger.error('AI生成评语失败:', error);
      ElMessage.error(error?.response?.data?.error || 'AI评语生成失败，请重试');
    } finally {
      aiGenerating.value = false;
    }
  };
  
  // 表单验证规则（动态，根据作业的max_score）
  const gradingRules = computed(() => {
    const maxScore = homeworkInfo.value?.max_score || 100;
    return {
      score: [
        { required: true, message: '请输入分数', trigger: 'blur' },
        {
          validator: (_rule, value, callback) => {
            if (value === null || value === undefined || value === '') {
              callback(new Error('请输入分数'));
              return;
            }
            const num = Number(value);
            if (Number.isNaN(num)) {
              callback(new Error('分数必须是数字'));
              return;
            }
            // 老师打分：要求 > 0 且 <= 上限
            if (num <= 0 || num > maxScore) {
              callback(new Error(`分数必须大于0且小于等于${maxScore}`));
              return;
            }
            callback();
          },
          trigger: 'blur',
        },
      ],
    };
  });
  
  const courseId = computed(() => parseInt(route.params.courseId));
  const homeworkId = computed(() => parseInt(route.params.homeworkId));
  
  const currentSubmission = computed(() => {
    // 支持通过 id 或 student_id 查找（未提交学生可能没有 id）
    return submissions.value.find(s => {
      if (s.id === currentSubmissionId.value) return true;
      if (!s.id && currentSubmissionId.value === `unsubmitted-${s.student_id}`) return true;
      return false;
    });
  });

  // 是否“全部批改完成”（用于显示成绩统计）
  // 定义：已过 ddl 且本次作业所有学生（无论是否提交）都已被老师批改完（is_graded 为 true）
  const isAllGraded = computed(() => {
    if (!submissions.value.length || !homeworkInfo.value?.deadline) return false;

    const deadline = new Date(homeworkInfo.value.deadline);
    const now = new Date();
    const isAfterDeadline = now > deadline;
    if (!isAfterDeadline) return false;

    // 所有记录（包括未提交但被打 0 分的）都要求 is_graded 为 true
    return submissions.value.every(s => s.is_graded);
  });

  // 当前选中的成绩段（用于从成绩统计反向筛选学生）
  const selectedScoreBucket = ref(null);

  // 成绩统计信息（最高分、最低分、平均分和分布）
  const scoreStats = computed(() => {
    if (!submissions.value.length) return null;

    // 统计所有有评分的记录（包括未提交但被打0分的学生）
    const scores = submissions.value
      .filter(s => s.is_graded && s.grading && typeof s.grading.score === 'number')
      .map(s => s.grading.score);

    if (!scores.length) return null;

    const min = Math.min(...scores);
    const max = Math.max(...scores);
    const sum = scores.reduce((acc, v) => acc + v, 0);
    const avg = Number((sum / scores.length).toFixed(2));

    const maxScore = homeworkInfo.value?.max_score || 100;
    // 将分数上限均分为 10 个区间（类似 Excel 柱状图分段）
    const bucketSize = maxScore / 10;
    const bucketCount = 10;

    const buckets = [];
    for (let i = 0; i < bucketCount; i++) {
      const start = Math.round(i * bucketSize);
      const end = Math.round(i === bucketCount - 1 ? maxScore : (i + 1) * bucketSize - 1);
      buckets.push({
        label: `${start}-${end}`,
        start,
        end,
        count: 0,
      });
    }

    // 统计每个分段的人数
    scores.forEach(score => {
      const idx = Math.min(
        Math.floor(score / bucketSize),
        bucketCount - 1
      );
      buckets[idx].count += 1;
    });

    const maxCount = Math.max(...buckets.map(b => b.count), 0);

    return {
      min,
      max,
      avg,
      total: scores.length,
      buckets,
      maxCount,
    };
  });

  // 点击成绩分布柱状图的某个分数段，筛选对应学生
  const toggleScoreBucket = (bucket) => {
    if (!bucket) return;
    // 如果再次点击同一分段，则取消筛选
    if (selectedScoreBucket.value && selectedScoreBucket.value.label === bucket.label) {
      selectedScoreBucket.value = null;
      return;
    }
    selectedScoreBucket.value = {
      label: bucket.label,
      start: bucket.start,
      end: bucket.end,
    };
  };

  // 处理图片 URL 列表（确保是数组格式）
  const processedImageUrls = computed(() => {
    if (!currentSubmission.value?.image_urls) return [];
    let images = currentSubmission.value.image_urls;
    
    // 如果是字符串，尝试解析为数组
    if (typeof images === 'string') {
      try {
        images = JSON.parse(images);
      } catch (e) {
        images = parseImageUrls(images);
      }
    }
    
    // 确保返回字符串数组
    if (!Array.isArray(images)) {
      // 如果不是数组，尝试转换为数组
      if (images && typeof images === 'object') {
        images = [images];
      } else {
        return [];
      }
    }
    
    // 处理数组中的每个元素，确保返回字符串URL
    const result = images.map((img, index) => {
      if (typeof img === 'string') {
        // 如果是字符串，直接返回
        return img.trim();
      }
      if (typeof img === 'object' && img !== null) {
        // 如果是对象，尝试提取 image_url 或 url 属性
        return img.image_url || img.url || String(img);
      }
      // 其他情况，转换为字符串
      return String(img);
    }).filter(url => url && url.trim() !== ''); // 过滤掉空字符串
    
    return result;
  });

  // 判断文件是否为PDF
  const isPDF = (url) => {
    if (!url) return false;
    const urlStr = typeof url === 'string' ? url : String(url);
    return urlStr.toLowerCase().endsWith('.pdf') || urlStr.toLowerCase().includes('.pdf');
  };

  const filteredSubmissions = computed(() => {
    let result = submissions.value;
    
    // 先按类型过滤
    if (filterType.value === 'pending') {
      result = result.filter(s => !s.is_graded && s.has_submitted);
    } else if (filterType.value === 'graded') {
      result = result.filter(s => s.is_graded);
    } else if (filterType.value === 'unsubmitted') {
      result = result.filter(s => !s.has_submitted);
    }

    // 如果选择了成绩分段，则只保留落在该分段内、且有评分的学生
    if (selectedScoreBucket.value) {
      const { start, end } = selectedScoreBucket.value;
      result = result.filter(s => {
        const score = s.grading?.score;
        if (typeof score !== 'number') return false;
        return score >= start && score <= end;
      });
    }
    
    // 再按搜索关键词过滤
    if (searchQuery.value && searchQuery.value.trim()) {
      const query = searchQuery.value.trim().toLowerCase();
      result = result.filter(s => {
        const nameMatch = s.student_name?.toLowerCase().includes(query);
        const noMatch = s.student_no?.toLowerCase().includes(query);
        return nameMatch || noMatch;
      });
    }
    
    return result;
  });
  
  const unsubmittedStudents = computed(() => {
    return submissions.value.filter(s => !s.has_submitted);
  });
  
  // 监听批注数据变化（使用 flush: 'post' 避免递归更新）
  // 监听批注数据变化（使用 flush: 'post' 和 nextTick 避免递归更新）
  watch(annotationData, () => {
    if (isInitializing.value || isReadOnly.value) return;
    // 使用 nextTick 延迟更新，避免在更新过程中触发新的更新
    nextTick(() => {
      if (!isInitializing.value && !isReadOnly.value) {
        hasUnsavedChanges.value = true;
      }
    });
  }, { deep: true, flush: 'post' });
  
  // 监听评分表单变化
  watch(gradingForm, () => {
    if (isInitializing.value || isReadOnly.value) return;
    hasUnsavedChanges.value = true;
  }, { deep: true });
  
  // 全局 Enter 键监听
  const handleKeyDown = (event) => {
    // 如果在文本框中，Enter 是换行
    if (event.target.tagName === 'TEXTAREA') {
      return;
    }
    
    // 排除搜索框（通过检查placeholder或class）
    const target = event.target;
    const isSearchInput = target.placeholder?.includes('搜索') || 
                         target.closest('.search-box') ||
                         target.classList.contains('el-input__inner') && target.placeholder?.includes('搜索');
    
    // 如果在搜索框中，不触发保存
    if (isSearchInput && event.key === 'Enter') {
      return; // 搜索框的Enter只用于搜索，不触发保存
    }
    
    // 如果在输入框中，Enter 触发提交（排除搜索框）
    if (event.target.tagName === 'INPUT' && event.key === 'Enter' && !isSearchInput) {
      event.preventDefault();
      handleSaveAndNext();
    }
    
    // Ctrl + Enter 全局提交
    if (event.ctrlKey && event.key === 'Enter') {
      event.preventDefault();
      handleSaveAndNext();
    }
  };
  
  onMounted(() => {
    fetchData();
    document.addEventListener('keydown', handleKeyDown);
  });
  
  onBeforeUnmount(() => {
    document.removeEventListener('keydown', handleKeyDown);
  });
  
  // 获取数据
  const fetchData = async () => {
    loading.value = true;
    try {
      // 获取作业信息（包括max_score）
      const homeworkResponse = await fetchCourseHomeworks(courseId.value);
      const homeworkList = homeworkResponse.data?.homework_list || homeworkResponse.data || [];
      const homework = homeworkList.find(h => h.id === homeworkId.value);
      if (homework) {
        homeworkInfo.value = homework;
      }
      
      // 获取学生提交列表
      const response = await fetchStudentSubmissions(courseId.value, homeworkId.value);
      submissions.value = response.data?.submission_list || [];
      
      // 如果有待批改的学生，自动选择第一个
      if (submissions.value.length > 0 && !currentSubmissionId.value) {
        const firstPending = submissions.value.find(s => !s.is_graded);
        if (firstPending) {
          selectStudent(firstPending);
        } else {
          selectStudent(submissions.value[0]);
        }
      }
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
  
  // 选择学生
  const selectStudent = async (submission) => {
    // 如果当前已有选择并且存在未保存的修改，则进行确认
    if (hasUnsavedChanges.value && currentSubmissionId.value) {
      try {
        await ElMessageBox.confirm(
          '当前批改尚未保存，确定要切换学生吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
          }
        );
      } catch {
        // 用户取消，不切换学生
        return;
      }
    }

    // 标记为初始化阶段，避免触发“未保存修改”逻辑
    isInitializing.value = true;

    // 使用 student_id 作为唯一标识（未提交学生可能没有 submission.id）
    currentSubmissionId.value = submission.id || `unsubmitted-${submission.student_id}`;
    
    // 如果是未提交的学生，清空批改表单并允许批改
    if (!submission.has_submitted) {
      gradingForm.value = {
        score: submission.grading?.score || null,
        feedback: submission.grading?.ai_feedback || '',
      };
      // 清空批注数据
      annotationData.value = {};
      await nextTick();
      hasUnsavedChanges.value = false;
      isInitializing.value = false;
      return; // 未提交学生不能查看提交内容，但可以批改
    }
    
    // 加载该学生的批改数据
    if (submission.grading) {
      gradingForm.value = {
        score: submission.grading.score,
        feedback: submission.grading.ai_feedback || '',
      };
      
      // 处理图片 URL（确保是数组格式）
      let imageUrls = submission.image_urls;
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
      const processedUrls = imageUrls.map(img => {
        if (typeof img === 'string') return img;
        if (typeof img === 'object' && img !== null) {
          return img.image_url || img.url || String(img);
        }
        return String(img);
      });

      // 加载批注数据
      if (submission.grading?.annotation_data && processedUrls.length > 0) {
          const annotations = submission.grading.annotation_data;
        
        // 如果 annotation_data 是数组，通过 image_url 匹配每个文件的批注
        if (Array.isArray(annotations)) {
          processedUrls.forEach((url) => {
            // 查找匹配的批注（通过 image_url 字段）
            const matchedAnnotation = annotations.find(ann => {
              if (!ann || typeof ann !== 'object') return false;
              const annUrl = ann.image_url || ann.url || String(ann);
              // 标准化URL进行比较（去掉可能的查询参数）
              const normalizeUrl = (u) => {
                if (!u) return '';
                const urlStr = String(u);
                const urlObj = new URL(urlStr, window.location.origin);
                return urlObj.pathname;
              };
              return normalizeUrl(annUrl) === normalizeUrl(url) || annUrl === url;
            });
            
            if (matchedAnnotation) {
              // 移除 image_url 字段，只保留批注数据
              const { image_url, url: _, ...annotationDataOnly } = matchedAnnotation;
              annotationData.value[url] = annotationDataOnly;
            }
          });
        } else if (annotations && typeof annotations === 'object') {
          // 如果只有一个批注对象（旧格式兼容），应用到第一张图片
          const { image_url, url: _, ...annotationDataOnly } = annotations;
          if (processedUrls.length > 0) {
            annotationData.value[processedUrls[0]] = annotationDataOnly;
          }
        }
      }
    } else {
      gradingForm.value = {
        score: null,
        feedback: '',
      };
      // 处理图片 URL（确保是数组格式）
      let imageUrls = submission.image_urls;
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
      const processedUrls = imageUrls.map(img => {
        if (typeof img === 'string') return img;
        if (typeof img === 'object' && img !== null) {
          return img.image_url || img.url || String(img);
        }
        return String(img);
      });
      // 清空批注数据
      processedUrls.forEach(url => {
        annotationData.value[url] = { version: 1, elements: [] };
      });
    }
    
    // 完成初始化，当前状态视为“已保存”基准
    await nextTick();
    hasUnsavedChanges.value = false;
    isInitializing.value = false;
  };
  
  // 仅保存
  const handleSaveOnly = async () => {
    if (isReadOnly.value) {
      ElMessage.warning('成绩已发布，无法修改');
      return;
    }
    await saveGrading(false);
  };
  
  // 保存并下一个
  const handleSaveAndNext = async () => {
    if (isReadOnly.value) {
      ElMessage.warning('成绩已发布，无法修改');
      return;
    }
    await saveGrading(true);
  };
  
  // 一键0分（批量批改未提交学生）
  const handleBatchZeroScore = async () => {
    if (isReadOnly.value) {
      ElMessage.warning('成绩已发布，无法修改');
      return;
    }
    if (unsubmittedStudents.value.length === 0) {
      ElMessage.warning('没有未提交的学生');
      return;
    }
    
    try {
      await ElMessageBox.confirm(
        `确定要为 ${unsubmittedStudents.value.length} 名未提交学生打0分吗？`,
        '确认操作',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      );
    } catch {
      return; // 用户取消
    }
    
    batchGrading.value = true;
    let successCount = 0;
    let failCount = 0;
    
    try {
      for (const student of unsubmittedStudents.value) {
        try {
          await gradeUnsubmittedStudent(
            courseId.value,
            homeworkId.value,
            student.student_id,
            {
              score: 0,
              ai_feedback: '未提交作业'
            }
          );
          successCount++;
        } catch (error) {
          logger.error(`为学生 ${student.student_name} 打0分失败:`, error);
          failCount++;
        }
      }
      
      if (successCount > 0) {
        ElMessage.success(`成功为 ${successCount} 名学生打0分${failCount > 0 ? `，${failCount} 名失败` : ''}`);
        // 重新获取数据
        await fetchData();
      } else {
        ElMessage.error('批量打0分失败');
      }
    } catch (error) {
      ElMessage.error('批量打0分操作失败');
    } finally {
      batchGrading.value = false;
    }
  };
  
  // 保存批改
  const saveGrading = async (goToNext = false) => {
    if (isReadOnly.value) {
      ElMessage.warning('成绩已发布，无法修改');
      return;
    }
    if (!currentSubmission.value) return;
    
    // 如果是未提交的学生，使用 grade_unsubmitted_student API
    if (!currentSubmission.value.has_submitted) {
      if (gradingForm.value.score === null || gradingForm.value.score === undefined) {
        ElMessage.warning('请先输入分数');
        return;
      }
      
      saving.value = true;
      try {
        await gradeUnsubmittedStudent(
          courseId.value,
          homeworkId.value,
          currentSubmission.value.student_id,
          {
            score: gradingForm.value.score,
            ai_feedback: gradingForm.value.feedback || '未提交作业'
          }
        );
        
        ElMessage.success('批改保存成功');
        hasUnsavedChanges.value = false;
        // 重新获取数据
        await fetchData();
        return;
      } catch (error) {
        const status = error?.response?.status;
        if (status === 400) {
          ElMessage.error(error?.response?.data?.error || '批改失败，请检查输入');
        } else if (status === 401) {
          ElMessage.error('登录已过期，请重新登录');
          userStore.logout();
          router.push({ name: 'Login' });
        } else {
          ElMessage.error(error?.response?.data?.error || '批改失败，请重试');
        }
      } finally {
        saving.value = false;
      }
      return;
    }
    
    // 表单验证
    if (gradingFormRef.value) {
      try {
        await gradingFormRef.value.validate();
      } catch (error) {
        ElMessage.warning('请先输入分数');
        return;
      }
    } else if (gradingForm.value.score === null || gradingForm.value.score === undefined) {
      ElMessage.warning('请先输入分数');
      return;
    }
    
    saving.value = true;
    try {
      // 处理图片 URL（确保是数组格式）
      let imageUrls = currentSubmission.value.image_urls;
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
      const processedUrls = imageUrls.map(img => {
        if (typeof img === 'string') return img;
        if (typeof img === 'object' && img !== null) {
          return img.image_url || img.url || String(img);
        }
        return String(img);
      });

      // 准备批注数据（将所有图片和PDF的批注合并为一个数组）
      // 每个文件的批注都包含其URL，以便后续正确匹配
      // 支持多张图片、多个PDF，以及图片和PDF混合提交
      const annotations = processedUrls.map((url) => {
        const annotation = annotationData.value[url] || { version: 1, elements: [] };
        // 保存完整的批注数据，包括 image_url 用于匹配
        return {
          ...annotation,
          image_url: url,  // 保存文件URL以便后续正确匹配（支持图片和PDF）
        };
      }).filter(annotation => {
        // 检查是否有实际批注
        // 支持旧格式：{ version: 1, elements: [] }
        // 支持新格式：{ version: 2, pages: { 1: [], 2: [] } }
        if (annotation.version === 2 && annotation.pages) {
          // 新格式：检查是否有任何页面有批注
          return Object.values(annotation.pages).some(pageElements => 
            Array.isArray(pageElements) && pageElements.length > 0
          );
        } else if (annotation.elements) {
          // 旧格式：检查 elements 数组
          return Array.isArray(annotation.elements) && annotation.elements.length > 0;
        }
        return false;
      });
      
      await gradeSubmission(currentSubmission.value.id, {
        score: gradingForm.value.score,
        ai_feedback: gradingForm.value.feedback || null,  // 评语可选，空字符串转为null
        annotation_data: annotations.length > 0 ? annotations : null,  // 如果没有批注，发送null
      });
      
      ElMessage.success('批改保存成功');
      hasUnsavedChanges.value = false;
      
      // 更新本地状态
      const submission = submissions.value.find(s => {
        if (s.id === currentSubmissionId.value) return true;
        if (!s.id && currentSubmissionId.value === `unsubmitted-${s.student_id}`) return true;
        return false;
      });
      if (submission) {
        submission.is_graded = true;
        submission.has_submitted = true; // 批改后标记为已提交
        submission.grading = {
          score: gradingForm.value.score,
          ai_feedback: gradingForm.value.feedback,
          annotation_data: annotations,
          grader_name: userStore.user?.name || '当前用户',
        };
      }
      
      if (goToNext) {
        // 查找下一个待批改的学生
        const nextPending = submissions.value.find(s => 
          !s.is_graded && s.id !== currentSubmissionId.value
        );
        
        if (nextPending) {
          selectStudent(nextPending);
        } else {
          // 全部批改完成
          ElMessage.success('恭喜！所有作业批改完毕');
          goBack();
        }
      }
    } catch (error) {
      const status = error?.response?.status;
      if (status === 400) {
        ElMessage.error(error?.response?.data?.error || '保存失败，请检查输入');
      } else if (status === 401) {
        ElMessage.error('登录已过期，请重新登录');
        userStore.logout();
        router.push({ name: 'Login' });
      } else {
        ElMessage.error(error?.response?.data?.error || '保存失败，请重试');
      }
    } finally {
      saving.value = false;
    }
  };
  
  // 返回
  const goBack = () => {
    // 使用 router.back() 返回到上一个页面
    // 如果浏览器历史记录中没有上一个页面，则返回到课程详情页
    if (window.history.length > 1) {
      router.back();
    } else {
    router.push({ 
      name: 'TeacherCourseDetail', 
      params: { id: courseId.value } 
    });
    }
  };
  </script>
  
  <style scoped>
  .grading-view {
    height: 100vh;
    width: 100vw;
    background: #f5f7fa;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .grading-header {
    background: #ffffff;
    border-bottom: 1px solid #e4e7ed;
    padding: 0 24px;
    height: 50px;
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }
  
  .grading-header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }
  
  .header-back-btn {
    color: #606266;
  }
  
  .header-back-btn:hover {
    color: #409EFF;
    background-color: transparent;
  }
  
  .header-current-student {
    color: #303133;
    font-size: 14px;
    font-weight: 500;
  }
  
  .header-right {
    font-size: 14px;
    color: #606266;
  }
  
  .grading-container {
    flex: 1;
    width: 100%;
    padding: 0;
    box-sizing: border-box;
    background: #f5f7fa;
    display: flex;
    overflow: hidden;
  }
  
  .student-list-panel {
    background: #fff;
    border-right: 1px solid #e4e7ed;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    width: 240px;
    height: 100%;
    overflow: hidden;
  }
  
  .filter-section {
    padding: 16px;
    border-bottom: 1px solid #ebeef5;
  }
  
  .batch-action {
    margin-top: 12px;
    text-align: center;
  }
  
  .student-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }
  
  .student-item {
    padding: 12px;
    margin-bottom: 8px;
    border: 1px solid #ebeef5;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fff;
  }
  
  .student-item:hover {
    background: #f5f7fa;
    border-color: #409eff;
    transform: translateX(4px);
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
  }
  
  .student-item.active {
    background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
    border-color: #409eff;
    box-shadow: 0 2px 12px rgba(64, 158, 255, 0.3);
    font-weight: 500;
  }
  
  .student-info {
    flex: 1;
  }
  
  .student-name {
    font-size: 14px;
    font-weight: 500;
    color: #303133;
    margin-bottom: 4px;
  }
  
  .student-no {
    font-size: 12px;
    color: #909399;
  }
  
  .content-panel {
    background: #f5f7fa;
    overflow-y: auto;
    padding: 20px;
    flex: 1;
    min-width: 0;
    height: 100%;
  }
  
  .submission-content {
    width: 100%;
  }
  
  .text-content-card,
  .image-annotator-card {
    margin-bottom: 20px;
    transition: all 0.3s ease;
    border-radius: 12px;
  }
  
  .text-content-card:hover,
  .image-annotator-card:hover {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transform: translateY(-2px);
  }
  
  .card-header {
    font-size: 14px;
    font-weight: 600;
    color: #303133;
  }
  
  .text-content {
    font-size: 14px;
    line-height: 1.8;
    color: #606266;
    white-space: pre-wrap;
    word-break: break-word;
    padding: 16px;
    background: #fafafa;
    border-radius: 8px;
    border: 1px solid #e4e7ed;
  }
  
  .text-content-empty {
    padding: 20px 0;
  }
  
  .header-hint {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #909399;
  }
  
  .text-reference {
    margin-bottom: 16px;
  }
  
  .text-reference-content {
    font-size: 13px;
    line-height: 1.6;
    color: #606266;
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 150px;
    overflow-y: auto;
    padding: 8px;
    background: #f5f7fa;
    border-radius: 4px;
  }
  
  .grading-panel {
    background: #fff;
    border-left: 1px solid #e4e7ed;
    display: flex;
    flex-direction: column;
    padding: 20px;
    flex-shrink: 0;
    width: 300px;
    height: 100%;
    overflow-y: auto;
  }
  
  .grading-content {
    display: flex;
    flex-direction: column;
    gap: 16px;
    animation: fadeIn 0.3s ease-in;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateX(10px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  .student-info-card,
  .grading-form-card {
    transition: all 0.3s ease;
    border-radius: 12px;
  }
  
  .student-info-card:hover,
  .grading-form-card:hover {
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  }
  
  .student-info-card {
    margin-bottom: 0;
  }
  
  .student-basic-info {
    text-align: center;
    padding: 8px 0;
  }
  
  .student-name-large {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }
  
  .student-no-small {
    font-size: 13px;
    color: #909399;
    margin-bottom: 8px;
  }
  
  .grader-info {
    font-size: 12px;
    color: #909399;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid #ebeef5;
  }
  
  .student-basic-info {
    text-align: center;
  }
  
  .student-name-large {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }
  
  .student-no-small {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }
  
  .grader-info {
    font-size: 12px;
    color: #606266;
    margin-top: 8px;
  }
  
  .grading-form-card {
    margin-bottom: 0;
  }
  
  .action-buttons {
    margin-top: auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .action-buttons .el-button {
    width: 100%;
  }
  
  .shortcut-hint {
    font-size: 12px;
    color: #909399;
    text-align: center;
    margin-top: 8px;
  }

  .score-stats-card {
    margin-top: 12px;
  }

  .stats-summary {
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-row-gap: 4px;
    font-size: 13px;
    margin-bottom: 8px;
  }

  .stats-summary strong {
    color: #303133;
  }

  .stats-chart {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    height: 120px;
    margin-top: 8px;
  }

  .stats-bar-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 11px;
    justify-content: flex-end;
    cursor: pointer;
    transition: transform 0.15s ease;
  }

  .stats-bar-item:hover {
    transform: translateY(-2px);
  }

  .stats-bar-item.active .stats-bar {
    background-color: #f56c6c;
  }

  .stats-bar-item.active .stats-bar-label {
    color: #f56c6c;
    font-weight: 600;
  }

  .stats-bar {
    width: 14px;
    background-color: #409eff;
    border-radius: 2px 2px 0 0;
    transition: height 0.2s ease;
  }

  .stats-bar-count {
    margin-bottom: 4px;
    color: #606266;
  }

  .stats-bar-label {
    margin-top: 2px;
    color: #909399;
    text-align: center;
    word-break: keep-all;
  }

  .stats-chart-empty {
    padding: 20px 0;
    text-align: center;
  }

  .image-stage {
    margin-bottom: 20px;
    background: #f5f7fa;
  }

  .image-stage-item {
    margin-bottom: 20px;
  }

  .file-header {
    margin-bottom: 8px;
    display: flex;
    align-items: center;
  }

  .image-stage-inner {
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    min-height: 400px;
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
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .pdf-tip {
    font-size: 12px;
    color: #909399;
    margin-left: 12px;
  }
  </style>
  