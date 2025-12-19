<template>
	<div class="student-home">
		<el-header class="header">
			<div class="header-content">
				<h1 class="header-title">Taskly</h1>
				<div class="header-actions">
					<el-button type="primary" @click="showEnrollDialog = true" :icon="Plus">加入课程</el-button>
					<el-dropdown @command="handleCommand">
						<span class="dropdown-trigger">
							{{ profile?.name || '同学' }}
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
		<div class="student-home-container">
			<aside class="sidebar">
			<div class="sidebar-header">
				<h2>Taskly</h2>
				<p class="student-name">{{ profile?.name ? `${profile.name} 同学` : '同学' }}</p>
			</div>
			<el-menu
				class="sidebar-menu"
				:default-active="activeMenu"
				:unique-opened="true"
				@select="handleMenuSelect"
			>
				<el-sub-menu index="courses">
					<template #title>
						<span>我的课程</span>
					</template>
					<el-menu-item
						v-for="course in courses"
						:key="course.id"
						:index="`course-${course.id}`"
					>
						{{ course.course_name }}
					</el-menu-item>
				</el-sub-menu>
				<el-menu-item index="all">所有作业</el-menu-item>
				<el-menu-item index="pending">待提交</el-menu-item>
				<el-menu-item index="submitted">已提交</el-menu-item>
				<el-menu-item index="completed">已完成</el-menu-item>
				<el-menu-item index="profile">个人资料</el-menu-item>
			</el-menu>
		</aside>

		<main class="content">
			<el-skeleton v-if="loading" animated :count="4" />
			<template v-else>
				<!-- 全局搜索框 -->
				<section class="global-search-section">
					<el-input
						v-model="searchQuery"
						placeholder="搜索课程代码、名称或作业标题..."
						clearable
						class="global-search-input"
						@keyup.enter="handleSearchEnter"
						@input="handleSearchInput"
					>
						<template #prefix>
							<el-icon><Search /></el-icon>
						</template>
					</el-input>
					
					<!-- 搜索结果面板 -->
					<el-card 
						v-if="searchQuery && searchResults.length > 0" 
						class="search-results-card"
						shadow="always"
					>
						<div class="search-results-header">
							<span class="results-count">找到 {{ searchResults.length }} 个结果</span>
						</div>
						
						<!-- 课程结果 -->
						<div v-if="courseResults.length > 0" class="results-group">
							<div class="results-group-title">课程</div>
							<div
								v-for="item in courseResults"
								:key="`course-${item.id}`"
								class="search-result-item"
								@click="goToSearchResult(item)"
							>
								<el-icon class="result-icon"><Reading /></el-icon>
								<div class="result-content">
									<div class="result-title" v-html="highlightText(item.title, searchQuery)"></div>
									<div class="result-meta">课程代码：<span v-html="highlightText(item.code, searchQuery)"></span></div>
								</div>
							</div>
						</div>
						
						<!-- 作业结果 -->
						<div v-if="homeworkResults.length > 0" class="results-group">
							<div class="results-group-title">作业</div>
							<div
								v-for="item in homeworkResults"
								:key="`homework-${item.id}`"
								class="search-result-item"
								@click="goToSearchResult(item)"
							>
								<el-icon class="result-icon"><Document /></el-icon>
								<div class="result-content">
									<div class="result-title" v-html="highlightText(item.title, searchQuery)"></div>
									<div class="result-meta">来自：<span v-html="highlightText(item.courseName, searchQuery)"></span></div>
								</div>
							</div>
						</div>
					</el-card>
					
					<!-- 无结果提示 -->
					<el-card 
						v-if="searchQuery && searchResults.length === 0 && !searching" 
						class="search-results-card"
						shadow="always"
					>
						<el-empty description="未找到匹配的结果" :image-size="60" />
					</el-card>
				</section>
				
				<!-- 顶部概览：欢迎 & 最近评分 -->
				<section class="overview-grid" v-if="!searchQuery">
					<el-card shadow="never" class="welcome-card">
						<div class="card-title">欢迎回来</div>
						<div class="welcome-body">
							<div>
								<p class="welcome-name">{{ profile?.name || '同学' }}</p>
								<p class="welcome-semester">当前学期：{{ currentSemester || '未设置' }}</p>
							</div>
						</div>
					</el-card>

					<el-card shadow="never" class="score-card">
						<div class="card-title">最近评分概览</div>
						<div v-if="scoreSegments.total" class="score-body">
							<div class="pie-wrapper" :style="pieStyle"></div>
							<ul class="score-legend">
								<li v-for="segment in scoreSegments.segments" :key="segment.label">
									<span class="legend-color" :style="{ backgroundColor: segment.color }"></span>
									<span class="legend-label">{{ segment.label }}</span>
									<span class="legend-value">{{ segment.value }}</span>
								</li>
							</ul>
						</div>
						<el-empty v-else description="暂无评分数据" :image-size="60" />
					</el-card>
				</section>
				
				<!-- 课程中心 - 简约看板设计 -->
				<section class="course-center" v-if="!searchQuery">
					<div class="section-header">
						<h2 class="section-title">我的课程</h2>
					</div>
					<el-row v-if="courses.length > 0" :gutter="20">
						<el-col
							v-for="course in courses"
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
								style="cursor: pointer;"
							>
								<!-- 课程封面 -->
								<div
									class="course-cover"
									:style="{ background: getCourseGradient(course.course_code) }"
								>
									<div class="course-cover-inner">
										<h3 class="course-name">{{ course.course_name }}</h3>
										<p class="course-teacher">
											{{ getCourseTeacher(course.id) || '暂无教师' }}
										</p>
									</div>
									<el-badge
										:value="getPendingTasksCount(course.id)"
										:hidden="getPendingTasksCount(course.id) === 0"
										class="pending-badge"
									/>
								</div>
								<div class="course-card-body">
									<div class="course-tags">
										<el-tag v-if="course.semester" type="info" size="small" effect="plain">
											{{ course.semester }}
										</el-tag>
										<el-tag type="warning" size="small" effect="plain">
											待交 {{ getPendingTasksCount(course.id) }}
										</el-tag>
									</div>
									<p class="course-code">课程号：{{ course.course_code }}</p>
								</div>
							</el-card>
						</el-col>
					</el-row>
					<el-empty v-else description="暂无课程，输入课程代码即可开始学习" :image-size="100" />
				</section>

				<section class="time-management-area" v-if="!searchQuery">
					<el-card shadow="never" class="deadline-card">
						<div class="card-title">最近未提交ddl提醒</div>
						<div class="deadline-body">
							<div v-if="nextDeadline">
								<p class="deadline-course">
									{{ nextDeadline.course.course_name }} · {{ nextDeadline.title }}
								</p>
								<p class="deadline-time">距离截止还有 {{ nextDeadline.countdown }}</p>
								<el-tag :type="statusMeta(nextDeadline.status).tag" effect="dark">
									{{ statusMeta(nextDeadline.status).label }}
								</el-tag>
							</div>
							<el-empty v-else description="暂无即将截止的作业" :image-size="60" />
						</div>
					</el-card>
					<el-card shadow="never" class="calendar-card">
						<template #header>
							<div class="calendar-header">
								<span class="card-title">截止日期日历</span>
								<el-button size="small" text @click="clearDateFilter">清空筛选</el-button>
							</div>
						</template>
						<!-- 日期范围筛选 -->
						<div class="date-range-filter">
							<el-date-picker
								v-model="dateRange"
								type="daterange"
								range-separator="至"
								start-placeholder="开始日期"
								end-placeholder="结束日期"
								format="YYYY-MM-DD"
								value-format="YYYY-MM-DD"
								@change="handleDateRangeChange"
								clearable
								style="width: 100%"
							/>
						</div>
						<el-calendar v-model="calendarViewDate">
							<template #date-cell="{ data }">
								<div
									class="calendar-cell"
									:class="calendarCellClass(data)"
									@click="handleDateSelect(data.day)"
								>
									<span class="day-number">{{ data.text }}</span>
									<el-badge
										v-if="deadlineCountByDate[data.day]"
										:value="deadlineCountByDate[data.day]"
										class="deadline-badge"
									/>
								</div>
							</template>
						</el-calendar>
					</el-card>
				</section>

				<el-card shadow="never" class="homework-card" v-if="!searchQuery">
					<template #header>
						<div class="card-header">
							<div class="card-title">作业列表</div>
							<div class="quick-stats-in-header">
								<div class="stat-block">
									<span class="stat-label">待提交作业</span>
									<span class="stat-value">{{ homeworkStats.pending }}</span>
								</div>
								<div class="stat-block">
									<span class="stat-label">本周截止</span>
									<span class="stat-value">{{ homeworkStats.dueThisWeek }}</span>
								</div>
								<div class="stat-block">
									<span class="stat-label">今天未完成</span>
									<span class="stat-value">{{ homeworkStats.todayPending }}</span>
								</div>
							</div>
							<el-tabs v-model="activeCourseTab">
								<el-tab-pane label="全部课程" name="all" />
								<el-tab-pane
									v-for="course in courses"
									:key="course.id"
									:label="course.course_name"
									:name="String(course.id)"
								/>
							</el-tabs>
						</div>
					</template>

					<div v-if="filteredAssignments.length" class="homework-grid">
						<el-card
							v-for="assignment in filteredAssignments"
							:key="assignment.uid"
							class="homework-item"
							shadow="hover"
						>
							<div class="homework-header">
								<el-tag :style="{ backgroundColor: getCourseColor(assignment.course.id) }" effect="dark">
									{{ assignment.course.course_name }}
								</el-tag>
								<el-tag :type="statusMeta(assignment.status).tag" effect="plain">
									{{ statusMeta(assignment.status).label }}
								</el-tag>
							</div>
							<h3 class="homework-title">{{ assignment.title }}</h3>
							<p class="homework-deadline">
								截止：{{ formatDateTime(assignment.deadlineDate) }}
								<span class="countdown" :class="statusMeta(assignment.status).countdownClass">
									{{ assignment.countdown }}
								</span>
							</p>
							<p class="homework-content">{{ assignment.content || '暂无描述' }}</p>
							<div class="homework-footer">
								<div class="homework-meta">
									<span v-if="assignment.attachments?.length" class="attachment">
										<el-icon><Paperclip /></el-icon>
										{{ assignment.attachments.length }} 个附件
									</span>
								</div>
								<el-button
									type="primary"
									size="small"
									:disabled="assignment.status === 'overdue'"
									@click="goToHomework(assignment)"
									class="submit-button"
								>
									查看详情
								</el-button>
							</div>
						</el-card>
					</div>
					<el-empty v-else description="暂无符合筛选条件的作业" />
				</el-card>

				<el-card shadow="never" class="insights-card">
					<el-tabs>
						<el-tab-pane label="数据洞察">
							<div class="insights-content">
								<el-card shadow="never" class="gantt-card">
									<template #header>
										<div class="card-title">作业甘特图</div>
									</template>
									<div v-if="ganttAssignments.length" class="gantt-wrapper">
										<div class="gantt-legend">
											<span v-for="item in ganttLegend" :key="item.status">
												<span class="legend-color" :style="{ backgroundColor: item.color }"></span>
												{{ item.label }}
											</span>
										</div>
										<div class="gantt-chart">
											<div v-for="assignment in ganttAssignments" :key="assignment.uid" class="gantt-row">
												<div class="gantt-label">{{ assignment.title }}</div>
												<div class="gantt-bar-container">
													<div
														class="gantt-bar"
														:class="`status-${assignment.status}`"
														:style="getGanttStyle(assignment)"
														:title="`${assignment.course.course_name} · ${assignment.title}`"
													></div>
												</div>
											</div>
										</div>
									</div>
									<el-empty v-else description="暂无作业可展示" />
								</el-card>

								<el-card shadow="never" class="history-card">
									<template #header>
										<div class="card-title">提交统计与历史</div>
									</template>
									<div class="history-body" v-if="recentSubmissions.length">
										<div class="history-stats">
											<div class="stat-block">
												<span class="stat-label">按时提交率</span>
												<span class="stat-value">{{ onTimeRate }}%</span>
											</div>
											<div class="stat-block">
												<span class="stat-label">总提交数</span>
												<span class="stat-value">{{ recentSubmissions.length }}</span>
											</div>
										</div>
										<el-timeline>
											<el-timeline-item
												v-for="item in recentSubmissions"
												:key="item.uid"
												:timestamp="item.submissionDate ? formatDateTime(item.submissionDate) : '待提交'"
												placement="top"
												:type="statusMeta(item.status).timelineType"
											>
												<p>{{ item.course.course_name }} · {{ item.title }}</p>
												<p>状态：{{ statusMeta(item.status).label }}</p>
												<p v-if="item.submission?.score !== undefined && item.submission?.score !== null">
													评分：{{ item.submission.score }} 分
												</p>
											</el-timeline-item>
										</el-timeline>
									</div>
									<el-empty v-else description="暂无提交记录" />
								</el-card>
							</div>
						</el-tab-pane>
					</el-tabs>
				</el-card>
			</template>
		</main>
		</div>

		<el-drawer v-model="profileDrawerVisible" title="个人资料" size="30%">
			<div v-if="profile" class="profile-details">
				<div v-if="!isEditing" class="profile-view">
					<div class="profile-item">
						<span class="label">姓名：</span>
						<span class="value">{{ profile.name }}</span>
					</div>
					<div class="profile-item">
						<span class="label">学号：</span>
						<span class="value">{{ profile.student_no }}</span>
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

		<!-- 加入课程对话框 -->
		<el-dialog v-model="showEnrollDialog" title="加入课程" width="400px">
			<el-form>
				<el-form-item label="课程号">
					<el-input
						v-model="enrollCourseCode"
						placeholder="请输入课程号"
						@keyup.enter="handleEnrollCourse"
						clearable
					/>
				</el-form-item>
			</el-form>
			<template #footer>
				<el-button @click="showEnrollDialog = false">取消</el-button>
				<el-button type="primary" @click="handleEnrollCourse" :loading="enrolling">确认</el-button>
			</template>
		</el-dialog>

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
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Paperclip, ArrowDown, Plus, Search, Reading, Document } from '@element-plus/icons-vue';
import { useRouter, onBeforeRouteLeave } from 'vue-router';
import { useUserStore } from '@/store/user';
import { validatePassword } from '@/utils/validators';
import {
	fetchCourseHomeworks,
	fetchHomeworkSubmission,
	fetchStudentCourses,
	fetchStudentProfile,
	updateStudentProfile,
	updatePassword,
	enrollCourse,
} from '@/api/student';

const userStore = useUserStore();
const router = useRouter();

const loading = ref(false);
const profile = ref(null);
const courses = ref([]);
const assignments = ref([]);
const searchSource = ref([]); // 扁平化的搜索数据源

const activeCourseTab = ref('all');
const searchQuery = ref('');
const searching = ref(false);
const activeMenu = ref('');
const activeNavFilter = ref('all');
const calendarViewDate = ref(new Date());
const calendarSelectedDate = ref('');
const dateRange = ref(null); // 日期范围筛选
const profileDrawerVisible = ref(false);
const isEditing = ref(false);
const hasChanged = ref(false);
const saving = ref(false);
const editForm = ref({
	name: '',
	emailPrefix: '',
	emailSuffix: 'mail.ustc.edu.cn', // 学生默认
	phoneCode: '+86',
	phoneNumber: '',
});
const editFormRef = ref(null);

// 邮箱后缀选项（不包含@符号，因为UI中已有@分隔符）
// USTC 邮箱放在最前面
const emailSuffixes = ['mail.ustc.edu.cn', 'ustc.edu.cn', 'gmail.com', '163.com', 'qq.com', 'outlook.com', 'sina.com', 'yahoo.com', 'hotmail.com'];

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

// 加入课程相关
const showEnrollDialog = ref(false);
const enrollCourseCode = ref('');
const enrolling = ref(false);

// 密码表单验证规则
const validateNewPassword = (rule, value, callback) => {
	if (!value) {
		callback(new Error('请输入新密码'));
	} else {
		const result = validatePassword(value);
		if (!result.isValid) {
			callback(new Error(result.message));
		} else {
			// 检查新密码是否和原密码相同
			if (passwordForm.value.old_password && value === passwordForm.value.old_password) {
				callback(new Error('新密码不能与原密码相同'));
			} else {
				callback();
			}
		}
	}
};

const validateConfirmPassword = (rule, value, callback) => {
	if (!value) {
		callback(new Error('请确认新密码'));
	} else if (value !== passwordForm.value.new_password) {
		callback(new Error('两次输入的密码不一致'));
	} else {
		callback();
	}
};

const passwordRules = {
	old_password: [
		{ required: true, message: '请输入原密码', trigger: 'blur' },
	],
	new_password: [
		{ required: true, validator: validateNewPassword, trigger: 'blur' },
	],
	confirm_password: [
		{ required: true, validator: validateConfirmPassword, trigger: 'blur' },
	],
};

const courseColorMap = reactive(new Map());

const coursePalette = ['#5B8FF9', '#61DDAA', '#65789B', '#F6BD16', '#7262fd', '#78D3F8'];

const fetchData = async () => {
	loading.value = true;
	try {
		const [profileRes, coursesRes] = await Promise.all([
			fetchStudentProfile(),
			fetchStudentCourses(),
		]);

		profile.value = profileRes.data;
		courses.value = coursesRes.data?.course_list || [];

		courses.value.forEach((course, index) => {
			if (!courseColorMap.has(course.id)) {
				courseColorMap.set(course.id, coursePalette[index % coursePalette.length]);
			}
		});

		// 构建搜索数据源（课程）
		searchSource.value = courses.value.map(course => ({
			type: 'course',
			title: course.course_name,
			code: course.course_code,
			id: course.id,
			courseId: course.id,
		}));

		const homeworkPromises = courses.value.map(async (course) => {
			try {
				const hwRes = await fetchCourseHomeworks(course.id);
				const list = hwRes.data?.homework_list || [];
				
				// 将作业添加到搜索数据源
				list.forEach(hw => {
					searchSource.value.push({
						type: 'homework',
						title: hw.title,
						courseName: course.course_name,
						id: hw.id,
						courseId: course.id,
					});
				});
				
				// 使用后端返回的提交状态，不再主动获取提交记录
				const enriched = list.map((hw) => {
					// 后端已经在 hw.submission 中返回了提交状态
					// 如果已提交，submission 包含基本信息（包含 score）；如果未提交，submission 为 null
					const submission = hw.submission
						? {
								id: hw.submission.id,
								is_graded: hw.submission.is_graded,
								submit_time: hw.submission.submit_time,
								score: hw.submission.score,
						  }
						: null;
					return normalizeAssignment(hw, course, submission);
				});
				return enriched;
			} catch (error) {
				ElMessage.error(error?.response?.data?.error || '获取作业失败');
				return [];
			}
		});

		const homeworkPerCourse = await Promise.all(homeworkPromises);
		assignments.value = homeworkPerCourse.flat().sort((a, b) => {
			if (!a.deadlineDate || !b.deadlineDate) return 0;
			return a.deadlineDate - b.deadlineDate;
		});
	} catch (error) {
		const message = error?.response?.data?.error || '获取学生信息失败';
		ElMessage.error(message);
	} finally {
		loading.value = false;
	}
};

const normalizeAssignment = (hw, course, submission) => {
	const deadlineDate = hw.deadline ? new Date(hw.deadline) : null;
	const createDate = hw.create_time ? new Date(hw.create_time) : null;
	const now = new Date();

	const submissionDate = submission?.submit_time ? new Date(submission.submit_time.replace(/-/g, '/')) : null;

	const attachments = parseAttachments(hw.image_urls);

	const status = deriveStatus({
		isOverdue: hw.is_overdue,
		deadlineDate,
		submission,
		now,
	});

	return {
		uid: `${course.id}-${hw.id}`,
		id: hw.id,
		title: hw.title,
		content: hw.content,
		deadlineDate,
		deadlineKey: deadlineDate ? formatDateKey(deadlineDate) : '',
		startDate: createDate || (deadlineDate ? new Date(deadlineDate.getTime() - 2 * 24 * 60 * 60 * 1000) : now),
		attachments,
		submission,
		submissionDate,
		status,
		course,
		// 如果已完成，不显示"已逾期"，而是显示"已完成"
		countdown: computeCountdown(deadlineDate, status, submission),
	};
};

const parseAttachments = (value) => {
	if (!value) return [];
	try {
		const parsed = JSON.parse(value);
		return Array.isArray(parsed) ? parsed : [];
	} catch (error) {
		return [];
	}
};

const deriveStatus = ({ isOverdue, deadlineDate, submission, now }) => {
	// 优先检查提交状态：已完成的作业一定不是已逾期
	if (submission) {
		// 如果已过ddl且已提交，显示为已完成
		const isOverdueNow = deadlineDate && deadlineDate < now;
		if (submission.is_graded || isOverdueNow) {
			return 'completed';
		} else {
			return 'submitted';
		}
	}
	// 只有在没有提交的情况下，才检查是否逾期
	// 已逾期的作业包括超过ddl仍然是待提交的作业
	if (isOverdue || (deadlineDate && deadlineDate < now)) {
		return 'overdue';
	}
	if (!deadlineDate) {
		return 'pending';
	}
	const diff = deadlineDate - now;
	const hours = diff / (1000 * 60 * 60);
	if (hours <= 48 && hours > 0) {
		return 'due-soon';
	}
	return 'pending';
};

const computeCountdown = (deadlineDate, status, submission) => {
	if (!deadlineDate) return '暂无截止时间';
	const now = new Date();
	const diff = deadlineDate - now;
	
	// 如果已完成（已提交且已过ddl，或已批改），显示"已完成"而不是"已逾期"
	if (status === 'completed' || (submission && diff <= 0)) {
		return '已完成';
	}
	
	if (diff <= 0) {
		return '已逾期';
	}
	const days = Math.floor(diff / (1000 * 60 * 60 * 24));
	const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
	if (days > 0) {
		return `${days} 天 ${hours} 小时`;
	}
	const minutes = Math.floor((diff / (1000 * 60)) % 60);
	return `${hours} 小时 ${minutes} 分`;
};

const formatDateKey = (date) => {
	if (!date) return '';
	const year = date.getFullYear();
	const month = `${date.getMonth() + 1}`.padStart(2, '0');
	const day = `${date.getDate()}`.padStart(2, '0');
	return `${year}-${month}-${day}`;
};

const formatDateTime = (date) => {
	if (!date) return '—';
	const year = date.getFullYear();
	const month = `${date.getMonth() + 1}`.padStart(2, '0');
	const day = `${date.getDate()}`.padStart(2, '0');
	const hours = `${date.getHours()}`.padStart(2, '0');
	const minutes = `${date.getMinutes()}`.padStart(2, '0');
	return `${year}-${month}-${day} ${hours}:${minutes}`;
};

const statusMeta = (status) => {
	const map = {
		pending: { label: '未提交', tag: 'info', countdownClass: 'neutral', timelineType: 'primary', color: '#909399' },
		'due-soon': { label: '临近截止', tag: 'warning', countdownClass: 'warning', timelineType: 'warning', color: '#E6A23C' },
		overdue: { label: '已逾期', tag: 'danger', countdownClass: 'danger', timelineType: 'danger', color: '#F56C6C' },
		submitted: { label: '已提交', tag: 'success', countdownClass: 'success', timelineType: 'success', color: '#67C23A' },
		completed: { label: '已完成', tag: 'success', countdownClass: 'success', timelineType: 'success', color: '#409EFF' },
	};
	return map[status] || map.pending;
};

const filteredAssignments = computed(() => {
	return assignments.value.filter((assignment) => {
		if (!matchesCourse(assignment)) return false;
		if (!matchesDate(assignment)) return false;
		if (!matchesNavFilter(assignment)) return false;
		return true;
	});
});

const matchesCourse = (assignment) => {
	if (activeCourseTab.value === 'all') return true;
	return String(assignment.course.id) === activeCourseTab.value;
};

const matchesDate = (assignment) => {
	// 如果选择了单个日期，按单个日期筛选
	if (calendarSelectedDate.value) {
		return assignment.deadlineKey === calendarSelectedDate.value;
	}
	// 如果选择了日期范围，按日期范围筛选
	if (dateRange.value && dateRange.value.length === 2) {
		const [startDate, endDate] = dateRange.value;
		if (!assignment.deadlineDate) return false;
		const deadlineDateStr = formatDateKey(assignment.deadlineDate);
		return deadlineDateStr >= startDate && deadlineDateStr <= endDate;
	}
	return true;
};

const matchesNavFilter = (assignment) => {
	switch (activeNavFilter.value) {
		case 'pending':
			return assignment.status === 'pending' || assignment.status === 'due-soon';
		case 'submitted':
			return assignment.status === 'submitted' || assignment.status === 'completed';
		case 'completed':
			return assignment.status === 'completed';
		default:
			return true;
	}
};

const deadlineCountByDate = computed(() => {
	return assignments.value.reduce((acc, assignment) => {
		// 只统计未提交的作业
		if (assignment.deadlineKey && !assignment.submission) {
			acc[assignment.deadlineKey] = (acc[assignment.deadlineKey] || 0) + 1;
		}
		return acc;
	}, {});
});

const calendarCellClass = (data) => {
	const classes = [];
	if (calendarSelectedDate.value === data.day) {
		classes.push('is-selected');
	}
	if (deadlineCountByDate.value[data.day]) {
		classes.push('has-deadline');
	}
	return classes.join(' ');
};

const handleMenuSelect = (index) => {
	activeMenu.value = index;
	if (index === 'profile') {
		profileDrawerVisible.value = true;
		return;
	}
	if (index === 'all') {
		// 跳转到所有作业页面
		router.push({ name: 'AllHomeworksView' });
		return;
	}
	if (index === 'pending') {
		// 跳转到待提交作业页面
		router.push({ name: 'PendingHomeworksView' });
		return;
	}
	if (index === 'submitted') {
		// 跳转到已提交作业页面
		router.push({ name: 'SubmittedHomeworksView' });
		return;
	}
	if (index === 'completed') {
		// 跳转到已完成作业页面
		router.push({ name: 'CompletedHomeworksView' });
		return;
	}
	if (index.startsWith('course-')) {
		const [, courseId] = index.split('-');
		// 跳转到课程详情页，与主页点击行为一致
		goToCourseDetail(parseInt(courseId));
	}
};

const handleDateSelect = (day) => {
	// 检查该日期是否有待提交的作业
	const hasPendingOnDate = deadlineCountByDate.value[day] && deadlineCountByDate.value[day] > 0;
	
	if (hasPendingOnDate) {
		// 如果有待提交的作业，跳转到该日期的待提交作业页面
		router.push({ name: 'DatePendingHomeworksView', params: { date: day } });
	} else {
		// 如果没有待提交的作业，使用原来的单个日期筛选逻辑
		if (calendarSelectedDate.value === day) {
			calendarSelectedDate.value = '';
		} else {
			calendarSelectedDate.value = day;
		}
	}
};

const clearDateFilter = () => {
	calendarSelectedDate.value = '';
	dateRange.value = null;
};

// 日期范围改变处理
const handleDateRangeChange = () => {
	// 当选择日期范围时，清空单个日期选择
	if (dateRange.value && dateRange.value.length === 2) {
		calendarSelectedDate.value = '';
	}
};

const getCourseColor = (courseId) => courseColorMap.get(courseId) || '#409EFF';

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

// 获取课程的待提交作业数量
const getPendingTasksCount = (courseId) => {
	return assignments.value.filter(a => 
		a.course.id === courseId && 
		(a.status === 'pending' || a.status === 'due-soon' || a.status === 'overdue')
	).length;
};

// 获取课程的教师名称
const getCourseTeacher = (courseId) => {
	// 从课程数据中获取教师信息（如果后端返回了教师信息）
	const course = courses.value.find(c => c.id === courseId);
	// 如果课程数据中有教师信息，返回教师名称
	// 否则返回 null（显示"暂无教师"）
	return course?.teacher_name || course?.teacher || null;
};

// 跳转到课程详情
const goToCourseDetail = (courseId) => {
	router.push({ name: 'CourseDetail', params: { id: courseId } });
};

// 搜索相关逻辑
const searchResults = computed(() => {
	if (!searchQuery.value || !searchQuery.value.trim()) {
		return [];
	}
	
	const query = searchQuery.value.trim().toLowerCase();
	return searchSource.value.filter(item => {
		if (item.type === 'course') {
			// 匹配课程名称或课程代码
			return item.title.toLowerCase().includes(query) || 
			       item.code.toLowerCase().includes(query);
		} else if (item.type === 'homework') {
			// 匹配作业标题或课程名称
			return item.title.toLowerCase().includes(query) ||
			       item.courseName.toLowerCase().includes(query);
		}
		return false;
	});
});

const courseResults = computed(() => {
	return searchResults.value.filter(item => item.type === 'course');
});

const homeworkResults = computed(() => {
	return searchResults.value.filter(item => item.type === 'homework');
});

// 高亮显示匹配文本
const highlightText = (text, query) => {
	if (!query || !text) return text;
	const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
	const regex = new RegExp(`(${escapedQuery})`, 'gi');
	return text.replace(regex, '<span class="highlight">$1</span>');
};

// 防抖处理
let searchDebounceTimer = null;
const handleSearchInput = () => {
	searching.value = true;
	if (searchDebounceTimer) {
		clearTimeout(searchDebounceTimer);
	}
	searchDebounceTimer = setTimeout(() => {
		searching.value = false;
	}, 300);
};

// 处理 Enter 键
const handleSearchEnter = () => {
	if (searchResults.value.length === 1) {
		// 如果只有一个结果，直接跳转
		goToSearchResult(searchResults.value[0]);
	} else if (searchResults.value.length > 1) {
		// 如果有多个结果，跳转到第一个
		goToSearchResult(searchResults.value[0]);
	}
};

// 跳转到搜索结果
const goToSearchResult = (item) => {
	if (item.type === 'course') {
		router.push({ name: 'CourseDetail', params: { id: item.id } });
	} else if (item.type === 'homework') {
		router.push({ name: 'HomeworkView', params: { id: item.id } });
	}
	// 清空搜索框
	searchQuery.value = '';
};

watch(activeCourseTab, (newValue) => {
	activeNavFilter.value = 'all';
	activeMenu.value = newValue === 'all' ? 'all' : `course-${newValue}`;
});

const homeworkStats = computed(() => {
	const pending = assignments.value.filter((a) => a.status === 'pending' || a.status === 'due-soon');
	const dueThisWeek = pending.filter((a) => {
		if (!a.deadlineDate) return false;
		const now = new Date();
		const diff = (a.deadlineDate - now) / (1000 * 60 * 60 * 24);
		return diff >= 0 && diff <= 7;
	});
	const todayKey = formatDateKey(new Date());
	const todayPending = pending.filter((a) => a.deadlineKey === todayKey);
	return {
		pending: pending.length,
		dueThisWeek: dueThisWeek.length,
		todayPending: todayPending.length,
	};
});

const nextDeadline = computed(() => {
	const candidates = assignments.value.filter((a) => !['submitted', 'completed'].includes(a.status) && a.deadlineDate && a.deadlineDate > new Date());
	if (!candidates.length) return null;
	return candidates.sort((a, b) => a.deadlineDate - b.deadlineDate)[0];
});

const ganttAssignments = computed(() => assignments.value.filter((a) => a.deadlineDate));

const timelineBounds = computed(() => {
	if (!ganttAssignments.value.length) return null;
	const start = Math.min(...ganttAssignments.value.map((a) => a.startDate?.getTime() || Date.now()));
	const end = Math.max(...ganttAssignments.value.map((a) => a.deadlineDate?.getTime() || Date.now()));
	if (start === end) {
		return {
			start,
			end: end + 24 * 60 * 60 * 1000,
		};
	}
	return { start, end };
});

const getGanttStyle = (assignment) => {
	const bounds = timelineBounds.value;
	if (!bounds) return {};
	const total = bounds.end - bounds.start;
	if (total <= 0) return { width: '100%' };
	const start = (assignment.startDate?.getTime() || bounds.start) - bounds.start;
	const end = (assignment.deadlineDate?.getTime() || bounds.end) - bounds.start;
	const span = Math.max(end - start, total * 0.04);
	const leftPercent = Math.max(0, (start / total) * 100);
	const widthPercent = Math.min(100 - leftPercent, Math.max((span / total) * 100, 4));
	return {
		left: `${leftPercent}%`,
		width: `${widthPercent}%`,
	};
};

const ganttLegend = computed(() => [
	{ status: 'pending', label: '未提交', color: statusMeta('pending').color },
	{ status: 'due-soon', label: '临近截止', color: statusMeta('due-soon').color },
	{ status: 'overdue', label: '已逾期', color: statusMeta('overdue').color },
	{ status: 'submitted', label: '已提交', color: statusMeta('submitted').color },
	{ status: 'completed', label: '已完成', color: statusMeta('completed').color },
]);

const recentSubmissions = computed(() => {
	return assignments.value
		.filter((a) => a.submission)
		.sort((a, b) => (b.submissionDate || 0) - (a.submissionDate || 0))
		.slice(0, 5);
});

const onTimeRate = computed(() => {
	if (!recentSubmissions.value.length) return 0;
	const onTime = recentSubmissions.value.filter((a) => {
		if (!a.submissionDate || !a.deadlineDate) return false;
		return a.submissionDate <= a.deadlineDate;
	});
	return Math.round((onTime.length / recentSubmissions.value.length) * 100);
});

const scoreSegments = computed(() => {
	// 最近有提交的记录
	const recent = recentSubmissions.value;
	if (!recent.length) {
		return { segments: [], total: 0 };
	}

	// 先把「有分数」和「未评分」分开
	const graded = recent.filter(
		(a) => a.submission && a.submission.score !== undefined && a.submission.score !== null,
	);
	const ungradedCount = recent.length - graded.length;

	const segments = [
		{ label: '90-100 分', color: '#67C23A', value: 0 },
		{ label: '80-89 分', color: '#E6A23C', value: 0 },
		{ label: '0-79 分', color: '#F56C6C', value: 0 },
		{ label: '未评分', color: '#909399', value: ungradedCount },
	];

	graded.forEach((assignment) => {
		const score = assignment.submission?.score ?? 0;
		if (score >= 90) {
			segments[0].value += 1;
		} else if (score >= 80) {
			segments[1].value += 1;
		} else {
			segments[2].value += 1;
		}
	});

	const total = segments.reduce((sum, segment) => sum + segment.value, 0);
	return {
		segments,
		total,
	};
});

const pieStyle = computed(() => {
	if (!scoreSegments.value.total) return {};
	const total = scoreSegments.value.total;
	let accumulated = 0;
	const gradients = scoreSegments.value.segments
		.filter((segment) => segment.value > 0)
		.map((segment) => {
			const start = (accumulated / total) * 360;
			accumulated += segment.value;
			const end = (accumulated / total) * 360;
			return `${segment.color} ${start}deg ${end}deg`;
		});
	return {
		background: `conic-gradient(${gradients.join(', ')})`,
	};
});

const currentSemester = computed(() => {
	if (!courses.value.length) return '';
	const semesterCount = courses.value.reduce((acc, course) => {
		if (course.semester) {
			acc[course.semester] = (acc[course.semester] || 0) + 1;
		}
		return acc;
	}, {});
	const [mostFrequent] = Object.entries(semesterCount).sort((a, b) => b[1] - a[1])[0] || [];
	return mostFrequent || '';
});

const goToHomework = (assignment) => {
	router.push({ name: 'HomeworkView', params: { id: assignment.id } });
};

// 加入课程
const handleEnrollCourse = async () => {
	if (!enrollCourseCode.value || !enrollCourseCode.value.trim()) {
		ElMessage.warning('请输入课程号');
		return;
	}
	
	try {
		enrolling.value = true;
		await enrollCourse({ course_code: enrollCourseCode.value.trim() });
		ElMessage.success('加入课程成功');
		showEnrollDialog.value = false;
		enrollCourseCode.value = '';
		// 刷新课程列表
		await fetchData();
	} catch (error) {
		const status = error?.response?.status;
		if (status === 400) {
			ElMessage.error(error?.response?.data?.error || '课程代码无效');
		} else if (status === 401) {
			ElMessage.error('登录已过期，请重新登录');
			userStore.logout();
			router.push({ name: 'Login' });
		} else {
			ElMessage.error(error?.response?.data?.error || '加入课程失败');
		}
	} finally {
		enrolling.value = false;
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

// 解析邮箱和电话
const parseEmail = (email) => {
	if (!email || !email.includes('@')) {
		return { prefix: '', suffix: 'mail.ustc.edu.cn' };
	}
	const parts = email.split('@');
	return { prefix: parts[0] || '', suffix: parts[1] || 'mail.ustc.edu.cn' };
};

const parsePhone = (phone) => {
	if (!phone) {
		return { code: '+86', number: '' };
	}
	// 尝试匹配常见区号
	if (phone.startsWith('+86')) {
		return { code: '+86', number: phone.substring(3) };
	} else if (phone.startsWith('+1')) {
		return { code: '+1', number: phone.substring(2) };
	} else if (phone.startsWith('+44')) {
		return { code: '+44', number: phone.substring(3) };
	} else if (phone.startsWith('+81')) {
		return { code: '+81', number: phone.substring(3) };
	} else if (phone.startsWith('+82')) {
		return { code: '+82', number: phone.substring(3) };
	} else if (phone.startsWith('+49')) {
		return { code: '+49', number: phone.substring(3) };
	} else if (phone.startsWith('+33')) {
		return { code: '+33', number: phone.substring(3) };
	} else if (phone.startsWith('+61')) {
		return { code: '+61', number: phone.substring(3) };
	} else if (phone.startsWith('+65')) {
		return { code: '+65', number: phone.substring(3) };
	}
	// 默认处理：如果以+开头，尝试提取前3-4位作为区号
	if (phone.startsWith('+')) {
		const match = phone.match(/^(\+\d{1,4})(.+)$/);
		if (match) {
			return { code: match[1], number: match[2] };
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
			emailSuffix: emailParts.suffix || 'mail.ustc.edu.cn',
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
		emailSuffix: 'mail.ustc.edu.cn',
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
		
		await updateStudentProfile({
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
		await updatePassword({
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

// 检查是否有未保存的修改（通用函数）
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
				// 用户确认离开，重置编辑状态
				isEditing.value = false;
				hasChanged.value = false;
				resolve(true);
			}).catch(() => {
				// 用户取消
				resolve(false);
			});
		} else {
			resolve(true);
		}
	});
};

// 监听 drawer 关闭，检查是否有未保存的修改
watch(profileDrawerVisible, async (newVal, oldVal) => {
	// 当 drawer 从打开变为关闭时
	if (oldVal === true && newVal === false) {
		const shouldClose = await checkUnsavedChanges();
		if (!shouldClose) {
			// 用户取消，阻止关闭 drawer
			profileDrawerVisible.value = true;
		}
	}
});

// 路由守卫：检查是否有未保存的修改
onBeforeRouteLeave(async (to, from, next) => {
	const shouldLeave = await checkUnsavedChanges();
	if (shouldLeave) {
		next();
	} else {
		next(false);
	}
});

onMounted(async () => {
	if (!userStore.token) {
		userStore.initialize();
	}
	await fetchData();
});
</script>

<style scoped>
.student-home {
	display: flex;
	flex-direction: column;
	min-height: 100vh;
	background: #f5f7fa;
}

.header {
	background: #ffffff;
	border-bottom: 1px solid #e4e7ed;
	padding: 0 24px;
	height: 60px;
	display: flex;
	align-items: center;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-content {
	width: 100%;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.header-actions {
	display: flex;
	align-items: center;
	gap: 16px;
}

.course-center {
	margin-bottom: 30px;
}

.section-header {
	margin-bottom: 20px;
}

.section-title {
	font-size: 20px;
	font-weight: 600;
	color: #303133;
	margin: 0;
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
	justify-content: space-between;
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

.course-teacher {
	font-size: 13px;
	margin: 4px 0 0 0;
	opacity: 0.9;
}

.pending-badge {
	position: relative;
	z-index: 1;
}

.course-card-body {
	margin-top: 10px;
}

.course-tags {
	display: flex;
	align-items: center;
	gap: 8px;
	margin-bottom: 6px;
}

.course-code {
	font-size: 13px;
	color: #606266;
	margin: 0;
}

.header-title {
	margin: 0;
	font-size: 20px;
	font-weight: 600;
	color: #303133;
}

.dropdown-trigger {
	display: flex;
	align-items: center;
	gap: 8px;
	cursor: pointer;
	color: #606266;
	font-size: 14px;
	padding: 8px 12px;
	border-radius: 4px;
	transition: background-color 0.3s;
}

.dropdown-trigger:hover {
	background-color: #f5f7fa;
}

.student-home-container {
	display: flex;
	gap: 16px;
	padding: 16px;
	flex: 1;
	box-sizing: border-box;
}

.sidebar {
	width: 240px;
	background: #ffffff;
	border-radius: 12px;
	padding: 16px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
	display: flex;
	flex-direction: column;
}

.sidebar-header {
	margin-bottom: 16px;
}

.sidebar-header h2 {
	margin: 0;
	font-size: 20px;
	font-weight: 600;
}

.student-name {
	margin: 8px 0 0;
	color: #909399;
}

.sidebar-menu {
	flex: 1;
	border-right: none;
}

.content {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.time-management-area {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 16px;
}

.overview-grid {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
	gap: 16px;
}

.card-title {
	font-weight: 600;
	font-size: 16px;
}

.welcome-card .welcome-body {
	display: flex;
	justify-content: space-between;
	gap: 16px;
	margin-top: 16px;
}

.welcome-name {
	margin: 0;
	font-size: 24px;
	font-weight: 600;
}

.welcome-semester {
	margin: 8px 0 0;
	color: #909399;
}

.quick-stats {
	display: flex;
	gap: 12px;
}

.quick-stats-in-header {
	display: flex;
	gap: 12px;
	align-items: center;
}

.quick-stats-in-header .stat-block {
	padding: 4px 8px;
	min-width: 70px;
}

.quick-stats-in-header .stat-label {
	font-size: 10px;
}

.quick-stats-in-header .stat-value {
	font-size: 16px;
}

.stat-block {
	background: #f0f2f5;
	border-radius: 8px;
	padding: 12px;
	min-width: 90px;
	text-align: center;
}

.stat-label {
	display: block;
	color: #909399;
	font-size: 12px;
}

.stat-value {
	font-size: 20px;
	font-weight: 600;
}

.deadline-body {
	margin-top: 16px;
}

.deadline-course {
	font-weight: 600;
}

.deadline-time {
	margin: 8px 0;
	color: #606266;
}

.score-card .score-body {
	display: flex;
	gap: 16px;
	align-items: center;
	margin-top: 16px;
}

.pie-wrapper {
	width: 120px;
	height: 120px;
	border-radius: 50%;
	box-shadow: inset 0 0 0 12px #ffffff;
}

.score-legend {
	list-style: none;
	padding: 0;
	margin: 0;
}

.score-legend li {
	display: flex;
	align-items: center;
	gap: 8px;
	margin-bottom: 8px;
}

.legend-color {
	width: 12px;
	height: 12px;
	border-radius: 2px;
	display: inline-block;
}

.legend-label {
	color: #606266;
	flex: 1;
}

.legend-value {
	font-weight: 600;
}

.homework-card .card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	flex-wrap: wrap;
	gap: 16px;
}

.homework-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
	gap: 16px;
}

.homework-item {
	border-radius: 12px;
	transition: transform 0.2s ease;
	position: relative;
}

.homework-item .submit-button {
	opacity: 0;
	transition: opacity 0.2s ease;
}

.homework-item:hover {
	transform: translateY(-4px);
}

.homework-item:hover .submit-button {
	opacity: 1;
}

.homework-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12px;
}

.homework-title {
	margin: 0 0 8px;
	font-size: 18px;
}

.homework-deadline {
	margin: 0 0 12px;
	color: #606266;
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
	align-items: center;
}

.countdown {
	font-weight: 600;
}

.countdown.warning {
	color: #e6a23c;
}

.countdown.danger {
	color: #f56c6c;
}

.countdown.success {
	color: #67c23a;
}

.homework-content {
	min-height: 48px;
	color: #606266;
}

.homework-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-top: 16px;
}

.homework-meta {
	display: flex;
	flex-direction: column;
	gap: 4px;
	color: #909399;
}

.attachment {
	display: flex;
	align-items: center;
	gap: 4px;
}

.insights-card .insights-content {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 16px;
}

.gantt-wrapper {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.gantt-legend {
	display: flex;
	gap: 12px;
	flex-wrap: wrap;
	color: #606266;
}

.gantt-legend .legend-color {
	width: 12px;
	height: 12px;
	border-radius: 2px;
	display: inline-block;
	margin-right: 6px;
}

.gantt-chart {
	display: flex;
	flex-direction: column;
	gap: 12px;
}

.gantt-row {
	display: flex;
	align-items: center;
	gap: 12px;
}

.gantt-label {
	width: 160px;
	font-weight: 500;
	color: #606266;
}

.gantt-bar-container {
	flex: 1;
	height: 12px;
	background: #f0f2f5;
	border-radius: 6px;
	position: relative;
}

.gantt-bar {
	position: absolute;
	top: 0;
	bottom: 0;
	border-radius: 6px;
}

.gantt-bar.status-pending {
	background: #909399;
}

.gantt-bar.status-due-soon {
	background: #e6a23c;
}

.gantt-bar.status-overdue {
	background: #f56c6c;
}

.gantt-bar.status-submitted {
	background: #67c23a;
}

.gantt-bar.status-completed {
	background: #409eff;
}

.history-body {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.history-stats {
	display: flex;
	gap: 16px;
}

.calendar-card {
	flex: 1;
}

.calendar-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.date-range-filter {
	margin-bottom: 16px;
	padding: 0 4px;
}

.calendar-cell {
	position: relative;
	padding: 6px;
	border-radius: 6px;
	cursor: pointer;
	transition: background 0.2s ease;
}

.calendar-cell.has-deadline {
	background: rgba(64, 158, 255, 0.08);
}

.calendar-cell.is-selected {
	background: #409eff;
	color: #ffffff;
}

.calendar-cell:hover {
	background: rgba(64, 158, 255, 0.15);
}

.day-number {
	font-weight: 500;
}

.deadline-badge {
	position: absolute;
	bottom: 4px;
	right: 4px;
}

.profile-details {
	display: flex;
	flex-direction: column;
	gap: 20px;
}

.profile-view {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.profile-item {
	display: flex;
	align-items: center;
	padding: 12px 0;
	border-bottom: 1px solid #f0f2f5;
}

.profile-item:last-child {
	border-bottom: none;
}

.profile-item .label {
	color: #909399;
	width: 80px;
	flex-shrink: 0;
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
	color: #606266;
	font-weight: 500;
}

.phone-input-group {
	display: flex;
	align-items: center;
}

@media (max-width: 1200px) {
	.student-home {
		flex-direction: column;
	}

	.sidebar {
		width: 100%;
		flex-direction: row;
	}

	.time-management-area {
		grid-template-columns: 1fr;
	}
}

@media (max-width: 768px) {
	.quick-stats {
		flex-direction: column;
	}

	.homework-grid {
		grid-template-columns: 1fr;
	}

	.gantt-label {
		width: 120px;
	}

	.insights-card .insights-content {
		grid-template-columns: 1fr;
	}
}

/* 全局搜索区域 */
.global-search-section {
	margin-bottom: 24px;
	position: relative;
}

.global-search-input {
	width: 100%;
	max-width: 600px;
	margin: 0 auto 16px;
	display: block;
}

.search-results-card {
	position: absolute;
	top: 100%;
	left: 50%;
	transform: translateX(-50%);
	z-index: 1000;
	margin-top: 8px;
	width: 100%;
	max-width: 600px;
	max-height: 500px;
	overflow-y: auto;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.search-results-header {
	padding-bottom: 12px;
	border-bottom: 1px solid #ebeef5;
	margin-bottom: 12px;
}

.results-count {
	font-size: 14px;
	color: #909399;
}

.results-group {
	margin-bottom: 16px;
}

.results-group:last-child {
	margin-bottom: 0;
}

.results-group-title {
	font-size: 14px;
	font-weight: 600;
	color: #303133;
	margin-bottom: 8px;
	padding-left: 8px;
}

.search-result-item {
	display: flex;
	align-items: flex-start;
	padding: 12px;
	margin-bottom: 8px;
	border-radius: 6px;
	cursor: pointer;
	transition: background-color 0.2s;
}

.search-result-item:hover {
	background-color: #f5f7fa;
}

.result-icon {
	font-size: 20px;
	color: #409eff;
	margin-right: 12px;
	margin-top: 2px;
	flex-shrink: 0;
}

.result-content {
	flex: 1;
	min-width: 0;
}

.result-title {
	font-size: 15px;
	font-weight: 500;
	color: #303133;
	margin-bottom: 4px;
	line-height: 1.5;
}

.result-meta {
	font-size: 13px;
	color: #909399;
}

.result-meta span {
	color: #606266;
}

.highlight {
	background-color: #fff3cd;
	color: #856404;
	font-weight: 600;
	padding: 0 2px;
	border-radius: 2px;
}
</style>
