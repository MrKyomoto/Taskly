<template>
	<div class="student-home">
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
				<section class="time-management-area">
					<el-card shadow="never" class="deadline-card">
						<div class="card-title">最近截止提醒</div>
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

				<section class="overview-grid">
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

				<el-card shadow="never" class="homework-card">
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
									<span v-if="assignment.submission">
										最近提交：{{ formatDateTime(assignment.submissionDate) }}
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
												:timestamp="formatDateTime(item.submissionDate)"
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

		<el-drawer v-model="profileDrawerVisible" title="个人资料" size="30%">
			<div v-if="profile" class="profile-details">
				<p><span>姓名：</span>{{ profile.name }}</p>
				<p><span>学号：</span>{{ profile.student_no }}</p>
				<p><span>邮箱：</span>{{ profile.email || '未填写' }}</p>
				<p><span>电话：</span>{{ profile.phone || '未填写' }}</p>
			</div>
			<el-empty v-else description="尚未获取资料" />
		</el-drawer>
	</div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { Paperclip } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/user';
import {
	fetchCourseHomeworks,
	fetchHomeworkSubmission,
	fetchStudentCourses,
	fetchStudentProfile,
} from '@/api/student';

const userStore = useUserStore();
const router = useRouter();

const loading = ref(false);
const profile = ref(null);
const courses = ref([]);
const assignments = ref([]);

const activeCourseTab = ref('all');
const activeMenu = ref('all');
const activeNavFilter = ref('all');
const calendarViewDate = ref(new Date());
const calendarSelectedDate = ref('');
const profileDrawerVisible = ref(false);

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

		const homeworkPromises = courses.value.map(async (course) => {
			try {
				const hwRes = await fetchCourseHomeworks(course.id);
				const list = hwRes.data?.homework_list || [];
				const enriched = await Promise.all(
					list.map(async (hw) => {
						let submission = null;
						try {
							const subRes = await fetchHomeworkSubmission(course.id, hw.id);
							submission = subRes.data?.submission || null;
									} catch (error) {
										const status = error?.response?.status;
										if (status && status !== 404) {
											ElMessage.error(error?.response?.data?.error || '获取提交情况失败');
										}
						}

						return normalizeAssignment(hw, course, submission);
					})
				);
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
		countdown: computeCountdown(deadlineDate),
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
	if (submission) {
		return submission.is_graded ? 'completed' : 'submitted';
	}
	if (isOverdue) {
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

const computeCountdown = (deadlineDate) => {
	if (!deadlineDate) return '暂无截止时间';
	const now = new Date();
	const diff = deadlineDate - now;
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
	if (!calendarSelectedDate.value) return true;
	return assignment.deadlineKey === calendarSelectedDate.value;
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
		if (assignment.deadlineKey) {
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
		activeNavFilter.value = 'all';
		activeCourseTab.value = 'all';
		return;
	}
	if (['pending', 'submitted', 'completed'].includes(index)) {
		activeNavFilter.value = index;
		return;
	}
	if (index.startsWith('course-')) {
		const [, courseId] = index.split('-');
		activeCourseTab.value = courseId;
		activeNavFilter.value = 'all';
	}
};

const handleDateSelect = (day) => {
	if (calendarSelectedDate.value === day) {
		calendarSelectedDate.value = '';
	} else {
		calendarSelectedDate.value = day;
	}
};

const clearDateFilter = () => {
	calendarSelectedDate.value = '';
};

const getCourseColor = (courseId) => courseColorMap.get(courseId) || '#409EFF';

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
	const segments = [
		{ label: '90-100 分', color: '#67C23A', value: 0 },
		{ label: '80-89 分', color: '#E6A23C', value: 0 },
		{ label: '60-79 分', color: '#F56C6C', value: 0 },
		{ label: '未评分', color: '#909399', value: 0 },
	];

	recentSubmissions.value.forEach((assignment) => {
		const score = assignment.submission?.score;
		if (score === undefined || score === null) {
			segments[3].value += 1;
			return;
		}
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
	gap: 16px;
	min-height: 100vh;
	padding: 16px;
	background: #f5f7fa;
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
	gap: 12px;
}

.profile-details span {
	color: #909399;
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
</style>
