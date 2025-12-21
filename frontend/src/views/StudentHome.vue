<template>
	<div class="student-home fade-in" :style="{ backgroundColor: personalizationStore.backgroundColor }">
		<el-header class="header" :style="headerStyle">
			<div class="header-content">
				<h1 class="header-title">Taskly</h1>
				<div class="header-actions">
					<!-- 助教切换按钮 -->
					<el-button 
						v-if="userStore.user?.role === 'ta'" 
						type="warning" 
						@click="handleSwitchRole"
						:icon="UserFilled"
					>
						切换到教师端
					</el-button>
					<el-button type="primary" @click="showEnrollDialog = true" :icon="Plus">加入课程</el-button>
					<el-button :icon="Setting" @click="showPersonalization = true" circle />
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
			<aside class="sidebar" :style="sidebarStyle" v-if="personalizationStore.modules.sidebar.visible">
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
						v-for="course in displayedNavCourses"
						:key="course.id"
						:index="`course-${course.id}`"
					>
						{{ course.course_name }}
					</el-menu-item>
					<el-menu-item 
						v-if="currentSemesterCourses.length > maxNavCoursesDisplay"
						index="view-all-courses"
						@click="router.push({ name: 'AllHomeworksView' })"
					>
						查看更多课程...
					</el-menu-item>
					<el-menu-item 
						v-if="isHistorySemesterMode"
						index="back-to-current-semester"
						@click="router.push({ name: 'StudentHome' })"
					>
						返回当前学期
					</el-menu-item>
					<el-menu-item 
						v-if="!isHistorySemesterMode && historySemesters.length > 0"
						index="history-semesters"
						@click="showHistorySemesterDialog = true"
					>
						查看历史学期课程
					</el-menu-item>
				</el-sub-menu>
				<el-menu-item index="all">所有作业</el-menu-item>
				<el-menu-item index="pending">待提交</el-menu-item>
				<el-menu-item index="submitted">已提交</el-menu-item>
				<el-menu-item index="completed">已完成</el-menu-item>
				<el-menu-item index="profile">个人资料</el-menu-item>
			</el-menu>
		</aside>

		<main class="content" :style="contentStyle">
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
							<span class="results-count">
								找到 {{ searchResults.length }} 个结果
								<span v-if="searchResults.length >= 50" class="results-limit-hint">（已限制显示前50个）</span>
							</span>
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
								<p class="welcome-semester">
									{{ isHistorySemesterMode ? `历史学期：${viewingSemester}` : `当前学期：${currentSemester || '未设置'}` }}
								</p>
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
						<div class="section-header-right">
							<span class="course-count" v-if="currentSemesterCourses.length > 0">共 {{ currentSemesterCourses.length }} 门课程</span>
							<el-button 
								v-if="isHistorySemesterMode" 
								type="primary" 
								text 
								@click="router.push({ name: 'StudentHome' })"
								style="margin-left: 12px;"
							>
								返回当前学期
							</el-button>
							<el-button 
								v-else-if="historySemesters.length > 0" 
								type="primary" 
								text 
								@click="showHistorySemesterDialog = true"
								style="margin-left: 12px;"
							>
								查看历史学期课程
							</el-button>
					</div>
					</div>
					<el-row v-if="displayedCourses.length > 0" :gutter="20">
						<el-col
							v-for="course in displayedCourses"
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
					<div v-if="courses.length > maxCoursesDisplay" class="course-more-actions">
						<el-button 
							v-if="!showAllCourses" 
							type="primary" 
							text 
							@click="showAllCourses = true"
						>
							查看更多课程 ({{ courses.length - maxCoursesDisplay }})
							<el-icon><ArrowDown /></el-icon>
						</el-button>
						<el-button 
							v-else 
							type="primary" 
							text 
							@click="showAllCourses = false"
						>
							收起
							<el-icon><ArrowUp /></el-icon>
						</el-button>
					</div>
					<el-empty v-if="courses.length === 0" description="暂无课程，输入课程代码即可开始学习" :image-size="100" />
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
									<div class="calendar-date-info">
									<span class="day-number">{{ data.text }}</span>
										<span class="month-day">{{ formatMonthDay(data.day) }}</span>
									</div>
									<!-- 显示该日期的作业列表 -->
									<div v-if="getAssignmentsForDate(data.day).length > 0" class="calendar-assignments">
										<div
											v-for="(assignment, idx) in getAssignmentsForDate(data.day)"
											:key="assignment.uid"
											class="calendar-assignment-item"
											:class="{ 'is-submitted': assignment.submission }"
											@click.stop="goToHomework(assignment)"
										>
											<span class="assignment-title">{{ assignment.title }}</span>
											<el-icon v-if="assignment.submission" class="assignment-status-icon"><Check /></el-icon>
										</div>
									</div>
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
							<div class="tabs-with-count">
							<el-tabs v-model="activeCourseTab">
									<el-tab-pane name="all">
										<template #label>
											<span>全部课程</span>
											<el-button 
												v-if="isHistorySemesterMode"
												type="primary" 
												text 
												size="small"
												style="margin-left: 8px;"
												@click.stop="router.push({ name: 'StudentHome' })"
											>
												返回当前学期
											</el-button>
										</template>
									</el-tab-pane>
								<el-tab-pane
										v-for="course in currentSemesterCourses"
									:key="course.id"
									:label="course.course_name"
									:name="String(course.id)"
								/>
							</el-tabs>
								<span class="homework-count" v-if="validAssignments.length > 0">共 {{ validAssignments.length }} 项</span>
							</div>
						</div>
					</template>

					<div v-if="displayedAssignments.length" class="homework-grid-wrapper">
						<transition-group name="fade-slide" tag="div" class="homework-grid">
						<el-card
								v-for="assignment in displayedAssignments"
							:key="assignment.uid"
								class="homework-item card-hover"
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
						</transition-group>
					</div>
					<div v-if="validAssignments.length > maxHomeworksDisplay" class="homework-more-actions">
						<el-button 
							v-if="!showAllHomeworks" 
							type="primary" 
							text 
							@click="showAllHomeworks = true"
						>
							查看更多作业 ({{ validAssignments.length - maxHomeworksDisplay }})
							<el-icon><ArrowDown /></el-icon>
						</el-button>
						<el-button 
							v-else 
							type="primary" 
							text 
							@click="showAllHomeworks = false"
						>
							收起
							<el-icon><ArrowUp /></el-icon>
						</el-button>
					<el-button 
						type="primary" 
						text 
						@click="isHistorySemesterMode ? router.push({ name: 'HistorySemesterAllHomeworksView', params: { semester: viewingSemester } }) : router.push({ name: 'AllHomeworksView' })"
						style="margin-left: 12px;"
					>
						查看全部作业
						<el-icon><Right /></el-icon>
					</el-button>
					</div>
					<el-empty v-if="filteredAssignments.length === 0" description="暂无符合筛选条件的作业" />
				</el-card>

				<el-card shadow="never" class="insights-card" v-if="!searchQuery">
					<el-tabs>
						<el-tab-pane label="数据洞察">
							<div class="insights-content">
								<el-card shadow="never" class="gantt-card">
									<template #header>
										<div class="gantt-header">
											<div class="gantt-title-wrapper">
												<span class="card-title">作业时间轴</span>
												<el-tooltip content="横条表示作业截止时间，红色竖线是今天，点击横条查看详情" placement="top">
													<el-icon class="gantt-help-icon"><QuestionFilled /></el-icon>
												</el-tooltip>
											</div>
											<div class="gantt-controls">
												<el-select
													v-model="ganttCourseFilter"
													placeholder="筛选课程"
													clearable
													size="small"
													style="width: 150px; margin-right: 8px;"
												>
													<el-option label="全部课程" value="all" />
													<el-option
														v-for="course in courses"
														:key="course.id"
														:label="course.course_name"
														:value="course.id"
													/>
												</el-select>
												<el-select
													v-model="ganttStatusFilter"
													placeholder="筛选状态"
													clearable
													size="small"
													style="width: 120px; margin-right: 8px;"
												>
													<el-option label="全部状态" value="all" />
													<el-option
														v-for="item in ganttLegend"
														:key="item.status"
														:label="item.label"
														:value="item.status"
													/>
												</el-select>
												<el-button-group size="small">
													<el-button @click="zoomGantt('week')" :type="ganttZoom === 'week' ? 'primary' : ''">本周</el-button>
													<el-button @click="zoomGantt('month')" :type="ganttZoom === 'month' ? 'primary' : ''">本月</el-button>
													<el-button @click="zoomGantt('all')" :type="ganttZoom === 'all' ? 'primary' : ''">全部</el-button>
												</el-button-group>
											</div>
										</div>
									</template>
									<div v-if="filteredGanttAssignments.length" class="gantt-wrapper">
										<!-- 说明文字 -->
										<div class="gantt-intro">
											<span class="intro-text">横条表示作业截止时间，红色竖线是今天，点击横条可查看详情</span>
										</div>
										<!-- 图例 -->
										<div class="gantt-legend">
											<span class="legend-title">状态说明：</span>
											<span v-for="item in ganttLegend" :key="item.status" class="legend-item">
												<span class="legend-color" :style="{ backgroundColor: item.color }"></span>
												<span class="legend-text">{{ item.label }}</span>
											</span>
										</div>
										<!-- 时间轴刻度 -->
										<div class="gantt-timeline-header">
											<div class="timeline-label">时间</div>
											<div
												v-for="tick in timelineTicks"
												:key="tick.date"
												class="timeline-tick"
												:style="{ left: `${tick.position}%` }"
											>
												<div class="tick-line"></div>
												<div class="tick-label">{{ tick.label }}</div>
											</div>
											<!-- 今天指示线 -->
											<div
												v-if="isTodayInRange"
												class="timeline-today-marker"
												:style="{ left: `${todayPosition}%` }"
											>
												<div class="today-line"></div>
												<div class="today-label">今天</div>
											</div>
										</div>
										<div class="gantt-chart">
											<div
												v-for="assignment in filteredGanttAssignments"
												:key="assignment.uid"
												class="gantt-row"
												@click="goToHomework(assignment)"
											>
												<div class="gantt-label">
													<div class="gantt-label-title">{{ assignment.title }}</div>
													<div class="gantt-label-course">{{ assignment.course.course_name }}</div>
													<div class="gantt-label-deadline">截止：{{ formatDateTime(assignment.deadlineDate) }}</div>
												</div>
												<div class="gantt-bar-container">
													<div
														class="gantt-bar"
														:class="`status-${assignment.status}`"
														:style="getGanttStyle(assignment)"
													>
														<div class="gantt-bar-content">
															<span class="gantt-bar-deadline">{{ formatGanttDate(assignment.deadlineDate) }}</span>
														</div>
													</div>
													<!-- 当前时间指示线 -->
													<div
														v-if="isTodayInRange"
														class="gantt-today-line"
														:style="{ left: `${todayPosition}%` }"
													></div>
												</div>
											</div>
										</div>
										<div class="gantt-footer">
											<div class="gantt-stats">
												<span>共显示 {{ filteredGanttAssignments.length }} 个作业</span>
												<span v-if="ganttCourseFilter !== 'all' || ganttStatusFilter !== 'all'" class="filter-hint">
													（已筛选）
												</span>
											</div>
										</div>
									</div>
									<el-empty v-else description="暂无作业可展示" />
								</el-card>

								<el-card shadow="never" class="history-card">
									<template #header>
										<div class="card-title">提交统计与历史</div>
									</template>
									<div class="history-body" v-if="allSubmissions.length">
										<div class="history-stats">
											<div class="stat-block">
												<span class="stat-label">按时提交率</span>
												<span class="stat-value">{{ onTimeRate }}%</span>
											</div>
											<div class="stat-block">
												<span class="stat-label">总提交数</span>
												<span class="stat-value">{{ allSubmissions.length }}</span>
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
										<div v-if="allSubmissions.length > recentSubmissions.length" class="more-submissions-hint">
											<el-button type="primary" text @click="goToAllHomeworks('submitted')">
												查看更多提交记录 (共 {{ allSubmissions.length }} 条)
											</el-button>
										</div>
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

		<!-- 个性化设置面板 -->
		<PersonalizationPanel v-model="showPersonalization" />

		<!-- 历史学期选择对话框 -->
		<el-dialog v-model="showHistorySemesterDialog" title="选择历史学期" width="500px">
			<div class="history-semester-dialog">
				<p class="dialog-tip">请选择要查看的历史学期：</p>
				<el-select
					v-model="selectedHistorySemester"
					placeholder="按时间顺序选择学期（最近 → 最远）"
					clearable
					style="width: 100%;"
					size="large"
				>
					<el-option
						v-for="semester in historySemesters"
						:key="semester"
						:label="semester"
						:value="semester"
					/>
				</el-select>
				<div v-if="selectedHistorySemester && filteredHistoryCourses.length > 0" class="history-courses-preview">
					<p class="preview-title">该学期的课程：</p>
					<div class="history-courses-list">
						<el-card
							v-for="course in displayedHistoryCourses"
							:key="course.id"
							class="history-course-card"
							shadow="hover"
							@click="goToHistoryCourseDetail(course)"
						>
							<div class="history-course-info">
								<h4>{{ course.course_name }}</h4>
								<p class="course-code">课程号：{{ course.course_code }}</p>
								<el-tag type="info" size="small">{{ course.semester }}</el-tag>
							</div>
						</el-card>
					</div>
					<div v-if="filteredHistoryCourses.length > maxHistoryCoursesDisplay" class="history-courses-footer">
						<el-button 
							type="primary" 
							text 
							@click="showAllHistoryCourses = !showAllHistoryCourses"
						>
							{{ showAllHistoryCourses ? '收起' : `查看更多 (共 ${filteredHistoryCourses.length} 门课程)` }}
						</el-button>
					</div>
				</div>
				<el-empty v-else-if="selectedHistorySemester && filteredHistoryCourses.length === 0" description="该学期暂无课程" :image-size="80" />
			</div>
			<template #footer>
				<el-button @click="showHistorySemesterDialog = false">关闭</el-button>
				<el-button 
					type="primary" 
					@click="goToHistorySemesterHome"
					:disabled="!selectedHistorySemester"
				>
					查看该学期主页
				</el-button>
			</template>
		</el-dialog>

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
import { Paperclip, ArrowDown, ArrowUp, Plus, Search, Reading, Document, Setting, Right, QuestionFilled, Check, UserFilled } from '@element-plus/icons-vue';
import { useRouter, useRoute, onBeforeRouteLeave } from 'vue-router';
import { useUserStore } from '@/store/user';
import { usePersonalizationStore } from '@/store/personalization';
import PersonalizationPanel from '@/components/PersonalizationPanel.vue';
import { formatDateTime as formatDateUtil, formatRelativeTime, formatCountdown } from '@/utils/date-formatter';
import { validatePassword } from '@/utils/validators';
import { getCurrentSemester, isCurrentSemester } from '@/utils/semester';
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
const personalizationStore = usePersonalizationStore();
const router = useRouter();
const route = useRoute();

const loading = ref(false);
const showPersonalization = ref(false);
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
const showHistorySemesterDialog = ref(false); // 历史学期选择对话框
const selectedHistorySemester = ref(''); // 选中的历史学期
const showAllHistoryCourses = ref(false); // 是否显示所有历史课程
const maxHistoryCoursesDisplay = ref(10); // 历史课程默认显示数量
const maxNavCoursesDisplay = ref(20); // 导航栏课程默认显示数量
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

// 个性化样式
const headerStyle = computed(() => {
  const module = personalizationStore.modules.header;
  return {
    backgroundColor: module.backgroundColor,
    color: module.textColor,
  };
});

const sidebarStyle = computed(() => {
  const module = personalizationStore.modules.sidebar;
  return {
    backgroundColor: module.backgroundColor,
    color: module.textColor,
  };
});

const contentStyle = computed(() => {
  const module = personalizationStore.modules.content;
  return {
    backgroundColor: module.backgroundColor,
    color: module.textColor,
  };
});

// 卡片样式
const cardStyle = computed(() => {
  const module = personalizationStore.modules.card;
  return {
    backgroundColor: module.backgroundColor,
    color: module.textColor,
    borderColor: module.borderColor,
  };
});

// 加入课程相关
const showEnrollDialog = ref(false);
const enrollCourseCode = ref('');
const enrolling = ref(false);

// 课程和作业显示控制
const maxCoursesDisplay = 12; // 默认显示12个课程
const showAllCourses = ref(false);
const maxHomeworksDisplay = 15; // 默认显示15个作业
const showAllHomeworks = ref(false);

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
		// 获取所有课程，不要在这里过滤（过滤逻辑在计算属性中处理）
		courses.value = coursesRes.data?.course_list || [];
		
		// 清空之前的作业数据，确保切换学期时不会显示其他学期的作业
		assignments.value = [];

		courses.value.forEach((course, index) => {
			if (!courseColorMap.has(course.id)) {
				courseColorMap.set(course.id, coursePalette[index % coursePalette.length]);
			}
		});

		// 根据 viewingSemester 过滤要获取作业的课程（只获取当前查看学期的课程作业）
		const coursesToFetch = viewingSemester.value 
			? courses.value.filter(course => course.semester === viewingSemester.value)
			: courses.value;

		// 构建搜索数据源（包含所有课程，用于搜索功能）
		searchSource.value = courses.value.map(course => ({
			type: 'course',
			title: course.course_name,
			code: course.course_code,
			id: course.id,
			courseId: course.id,
		}));

		const homeworkPromises = coursesToFetch.map(async (course) => {
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
	// 统一处理日期字符串格式，确保正确解析
	const parseDate = (dateValue) => {
		if (!dateValue) return null;
		
		// 如果已经是 Date 对象且有效
		if (dateValue instanceof Date) {
			return isNaN(dateValue.getTime()) ? null : dateValue;
		}
		
		// 如果是字符串，尝试多种格式解析
		if (typeof dateValue === 'string') {
			// 先尝试替换 - 为 /（处理 YYYY-MM-DD 格式）
			let dateStr = dateValue.replace(/-/g, '/');
			// 移除可能的时间部分中的 T 和 Z
			dateStr = dateStr.replace(/T/g, ' ').replace(/Z/g, '');
			const date = new Date(dateStr);
			if (!isNaN(date.getTime())) {
				return date;
			}
			
			// 如果失败，尝试直接解析
			const date2 = new Date(dateValue);
			if (!isNaN(date2.getTime())) {
				return date2;
			}
			
			console.warn('无法解析日期:', dateValue, '作业:', hw.title);
			return null;
		}
		
		// 其他类型，尝试直接转换
		const date = new Date(dateValue);
		return isNaN(date.getTime()) ? null : date;
	};
	
	const deadlineDate = parseDate(hw.deadline);
	const createDate = parseDate(hw.create_time);
	const now = new Date();

	const submissionDate = submission?.submit_time ? parseDate(submission.submit_time) : null;
	
	// 调试信息：检查日期解析
	if (hw.deadline && (!deadlineDate || isNaN(deadlineDate.getTime()))) {
		console.error('日期解析失败:', {
			title: hw.title,
			原始deadline: hw.deadline,
			deadline类型: typeof hw.deadline,
			解析后: deadlineDate,
		});
	}

	const attachments = parseAttachments(hw.image_urls);

	// 验证日期有效性
	if (deadlineDate && isNaN(deadlineDate.getTime())) {
		console.error('无效的截止日期:', hw.title, '原始值:', hw.deadline, '解析后:', deadlineDate);
	}

	const status = deriveStatus({
		isOverdue: hw.is_overdue,
		deadlineDate: deadlineDate && !isNaN(deadlineDate.getTime()) ? deadlineDate : null,
		submission,
		submissionDate: submissionDate && !isNaN(submissionDate.getTime()) ? submissionDate : null,
		now,
	});

	return {
		uid: `${course.id}-${hw.id}`,
		id: hw.id,
		title: hw.title,
		content: hw.content,
		max_score: hw.max_score || 100, // 作业满分，默认为100
		deadlineDate: deadlineDate && !isNaN(deadlineDate.getTime()) ? deadlineDate : null,
		deadlineKey: deadlineDate && !isNaN(deadlineDate.getTime()) ? formatDateKey(deadlineDate) : '',
		startDate: createDate && !isNaN(createDate.getTime()) ? createDate : (deadlineDate && !isNaN(deadlineDate.getTime()) ? new Date(deadlineDate.getTime() - 2 * 24 * 60 * 60 * 1000) : now),
		attachments,
		submission,
		submissionDate: submissionDate && !isNaN(submissionDate.getTime()) ? submissionDate : null,
		status,
		course,
		// 如果已完成，不显示"已逾期"，而是显示"已完成"
		countdown: computeCountdown(deadlineDate && !isNaN(deadlineDate.getTime()) ? deadlineDate : null, status, submission),
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

const deriveStatus = ({ isOverdue, deadlineDate, submission, submissionDate, now }) => {
	// 与AllHomeworksView.vue中的getStatusTag逻辑保持一致
		const isOverdueNow = deadlineDate && deadlineDate < now;
	
	// 检查是否在ddl前提交：如果提交时间在ddl之后或没有提交时间，视为未在ddl前提交
	const submittedBeforeDeadline = submissionDate && deadlineDate && submissionDate <= deadlineDate;
	
	// 如果已过ddl且没有在ddl前提交，即使有批改记录（老师批改0分），也应该显示"已逾期"
	if (isOverdueNow && !submittedBeforeDeadline) {
		return 'overdue';
	}
	
	// 如果有提交记录（在ddl前提交的）
	if (submission && submittedBeforeDeadline) {
		// 如果已批改，显示为已完成
		if (submission.is_graded) {
			return 'completed';
		} else {
			return 'submitted';
		}
	}
	
	// 如果没有提交，再检查是否逾期
	if (isOverdueNow) {
		return 'overdue';
	}
	
	// 没有截止日期，显示为待提交
	if (!deadlineDate) {
		return 'pending';
	}
	
	// 有截止日期且未过期，根据时间判断
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

// 格式化月日显示（如：12.14）
const formatMonthDay = (dateString) => {
	if (!dateString) return '';
	const date = new Date(dateString);
	const month = date.getMonth() + 1;
	const day = date.getDate();
	return `${month}.${day}`;
};

const formatDateTime = (date) => {
	if (!date) return '—';
	const d = date instanceof Date ? date : new Date(date);
	if (isNaN(d.getTime())) return '—';
	return formatDateUtil(d, 'YYYY-MM-DD HH:mm');
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

// 显示的课程列表（根据是否展开，只显示当前学期课程）
const displayedCourses = computed(() => {
	const currentCourses = currentSemesterCourses.value;
	if (showAllCourses.value || currentCourses.length <= maxCoursesDisplay) {
		return currentCourses;
	}
	return currentCourses.slice(0, maxCoursesDisplay);
});

// 未过期的作业列表（只显示截止日期在未来的作业，和甘特图逻辑一致）
// 在历史学期模式下，显示所有作业（包括已过期的）
const validAssignments = computed(() => {
	// 如果是历史学期模式，显示所有作业
	if (isHistorySemesterMode.value) {
		return assignments.value;
	}
	
	// 当前学期模式：只显示截止日期在未来的作业
	const now = new Date();
	const filtered = assignments.value.filter((a) => {
		// 必须有截止日期
		if (!a.deadlineDate) return false;
		
		// 确保 deadlineDate 是 Date 对象
		let deadline = a.deadlineDate;
		if (!(deadline instanceof Date)) {
			deadline = new Date(deadline);
		}
		
		// 检查日期是否有效
		if (isNaN(deadline.getTime())) {
			console.warn('无效的截止日期:', a.title, a.deadlineDate);
			return false;
		}
		
		// 只显示截止日期在未来的作业（比较到毫秒级别）
		const isFuture = deadline.getTime() > now.getTime();
		
		// 调试信息（针对12.31的作业）
		if (a.deadlineDate && a.deadlineDate.toString().includes('2025-12-31')) {
			console.log('12.31作业检查:', {
				title: a.title,
				deadlineDate: a.deadlineDate,
				deadlineTime: deadline.getTime(),
				nowTime: now.getTime(),
				isFuture: isFuture,
				submission: a.submission ? '有提交' : '无提交',
				status: a.status,
			});
		}
		
		return isFuture;
	});
	
	console.log('validAssignments 总数:', filtered.length, '总作业数:', assignments.value.length);
	return filtered;
});

// 显示的作业列表（根据是否展开）
const displayedAssignments = computed(() => {
	if (showAllHomeworks.value || validAssignments.value.length <= maxHomeworksDisplay) {
		return validAssignments.value;
	}
	return validAssignments.value.slice(0, maxHomeworksDisplay);
});

const matchesCourse = (assignment) => {
	if (activeCourseTab.value === 'all') {
		// 只显示当前查看学期的作业（当前学期或历史学期）
		return assignment.course.semester === viewingSemester.value;
	}
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

// 统计所有作业（包括已提交的）按日期分组（只统计当前查看学期的作业）
const allAssignmentsByDate = computed(() => {
	return assignments.value
		.filter(assignment => assignment.course.semester === viewingSemester.value)
		.reduce((acc, assignment) => {
			// 统计所有有截止日期的作业（包括已提交的）
			if (assignment.deadlineKey) {
				acc[assignment.deadlineKey] = (acc[assignment.deadlineKey] || 0) + 1;
			}
			return acc;
		}, {});
});

// 只统计未提交的作业（用于显示徽章）（只统计当前查看学期的作业）
const deadlineCountByDate = computed(() => {
	return assignments.value
		.filter(assignment => assignment.course.semester === viewingSemester.value)
		.reduce((acc, assignment) => {
		// 只统计未提交的作业
		if (assignment.deadlineKey && !assignment.submission) {
			acc[assignment.deadlineKey] = (acc[assignment.deadlineKey] || 0) + 1;
		}
		return acc;
	}, {});
});

const calendarCellClass = (data) => {
	const classes = [];
	
	// 将 data.day 转换为日期键格式
	let dayKey = '';
	if (typeof data.day === 'string') {
		dayKey = data.day;
	} else if (data.day instanceof Date) {
		dayKey = formatDateKey(data.day);
	} else {
		const date = new Date(data.day);
		if (!isNaN(date.getTime())) {
			dayKey = formatDateKey(date);
		}
	}
	
	// 单个日期选择高亮
	if (calendarSelectedDate.value === dayKey) {
		classes.push('is-selected');
	}
	
	// 日期范围高亮
	if (dateRange.value && dateRange.value.length === 2) {
		const [startDate, endDate] = dateRange.value;
		if (dayKey >= startDate && dayKey <= endDate) {
			classes.push('is-in-range');
			// 如果是范围的边界，添加特殊样式
			if (dayKey === startDate || dayKey === endDate) {
				classes.push('is-range-boundary');
			}
		}
	}
	
	// 有作业的日期
	if (allAssignmentsByDate.value[dayKey]) {
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
		// 跳转到所有作业页面（根据当前学期模式选择路由）
		if (isHistorySemesterMode.value) {
			router.push({ name: 'HistorySemesterAllHomeworksView', params: { semester: viewingSemester.value } });
		} else {
		router.push({ name: 'AllHomeworksView' });
		}
		return;
	}
	if (index === 'pending') {
		// 跳转到待提交作业页面
		if (isHistorySemesterMode.value) {
			router.push({ name: 'HistorySemesterPendingHomeworksView', params: { semester: viewingSemester.value } });
		} else {
		router.push({ name: 'PendingHomeworksView' });
		}
		return;
	}
	if (index === 'submitted') {
		// 跳转到已提交作业页面
		if (isHistorySemesterMode.value) {
			router.push({ name: 'HistorySemesterSubmittedHomeworksView', params: { semester: viewingSemester.value } });
		} else {
		router.push({ name: 'SubmittedHomeworksView' });
		}
		return;
	}
	if (index === 'completed') {
		// 跳转到已完成作业页面
		if (isHistorySemesterMode.value) {
			router.push({ name: 'HistorySemesterCompletedHomeworksView', params: { semester: viewingSemester.value } });
		} else {
		router.push({ name: 'CompletedHomeworksView' });
		}
		return;
	}
	if (index.startsWith('course-')) {
		const [, courseId] = index.split('-');
		// 跳转到课程详情页，与主页点击行为一致
		goToCourseDetail(parseInt(courseId));
	}
};

// 获取指定日期的所有作业（包括已提交的）
const getAssignmentsForDate = (day) => {
	// day 可能是日期字符串或 Date 对象，需要转换为格式化的日期键
	let dayKey = '';
	if (typeof day === 'string') {
		dayKey = day;
	} else if (day instanceof Date) {
		dayKey = formatDateKey(day);
	} else {
		// 尝试解析
		const date = new Date(day);
		if (!isNaN(date.getTime())) {
			dayKey = formatDateKey(date);
		}
	}
	return assignments.value.filter((a) => a.deadlineKey === dayKey);
};

const handleDateSelect = (day) => {
	// 将 day 转换为日期键格式
	let dayKey = '';
	if (typeof day === 'string') {
		dayKey = day;
	} else if (day instanceof Date) {
		dayKey = formatDateKey(day);
	} else {
		const date = new Date(day);
		if (!isNaN(date.getTime())) {
			dayKey = formatDateKey(date);
		}
	}
	
	// 检查该日期是否有任何作业（包括已提交的）
	const assignmentsForDay = getAssignmentsForDate(dayKey);
	
	if (assignmentsForDay.length > 0) {
		// 如果有作业，跳转到该日期的作业页面
		router.push({ name: 'DatePendingHomeworksView', params: { date: dayKey } });
		}
	// 如果没有作业，点击就无事发生（不执行任何操作）
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

// 获取课程的待提交作业数量（只统计真正未提交的作业）
const getPendingTasksCount = (courseId) => {
	const now = new Date();
	return assignments.value.filter(a => {
		// 必须是该课程的作业
		if (a.course.id !== courseId) return false;
		// 必须没有提交记录
		if (a.submission) return false;
		// 必须有截止日期且截止日期在未来（未过期）
		if (!a.deadlineDate || a.deadlineDate <= now) return false;
		// 状态必须是未提交或临近截止
		return a.status === 'pending' || a.status === 'due-soon';
	}).length;
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

// 跳转到历史学期主页
const goToHistorySemesterHome = () => {
	if (!selectedHistorySemester.value) return;
	// 跳转到历史学期主页
	router.push({ 
		name: 'HistorySemesterHome', 
		params: { semester: selectedHistorySemester.value }
	});
	showHistorySemesterDialog.value = false;
	selectedHistorySemester.value = '';
};

// 跳转到历史学期课程详情（保留用于对话框中的课程卡片点击）
const goToHistoryCourseDetail = (course) => {
	// 跳转到课程详情页面，并传递学期信息
	router.push({ 
		name: 'CourseDetail', 
		params: { id: course.id },
		query: { semester: course.semester }
	});
	showHistorySemesterDialog.value = false;
};

// 搜索相关逻辑
const searchResults = computed(() => {
	if (!searchQuery.value || !searchQuery.value.trim()) {
		return [];
	}
	
	const query = searchQuery.value.trim().toLowerCase();
	const allResults = searchSource.value.filter(item => {
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
	
	// 限制搜索结果数量，避免渲染过多
	const maxSearchResults = 50;
	return allResults.slice(0, maxSearchResults);
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
	const now = new Date();
	// 只筛选：未提交、未完成、有截止日期、截止日期在未来、且没有提交记录
	const candidates = assignments.value.filter((a) => {
		// 必须没有提交记录
		if (a.submission) return false;
		// 状态必须是未提交或临近截止
		if (!['pending', 'due-soon'].includes(a.status)) return false;
		// 必须有截止日期且截止日期在未来
		if (!a.deadlineDate || a.deadlineDate <= now) return false;
		return true;
	});
	if (!candidates.length) return null;
	return candidates.sort((a, b) => a.deadlineDate - b.deadlineDate)[0];
});

// 甘特图相关状态
const ganttCourseFilter = ref('all');
const ganttStatusFilter = ref('all');
const ganttZoom = ref('all'); // 'week', 'month', 'all'

// 甘特图只显示未到截止日期的作业
const ganttAssignments = computed(() => {
	const now = new Date();
	return assignments.value.filter((a) => {
		// 必须有截止日期
		if (!a.deadlineDate) return false;

		// 确保 deadlineDate 是 Date 对象
		let deadline = a.deadlineDate;
		if (!(deadline instanceof Date)) {
			deadline = new Date(deadline);
		}
		
		// 检查日期是否有效
		if (isNaN(deadline.getTime())) return false;
		
		// 只显示截止日期在未来的作业（比较到毫秒级别）
		return deadline.getTime() > now.getTime();
	});
});

// 根据缩放级别计算时间范围
const ganttTimeRange = computed(() => {
	if (!ganttAssignments.value.length) return null;
	
	const now = new Date();
	let start, end;
	
	if (ganttZoom.value === 'week') {
		// 显示未来一周
		start = now;
		end = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
	} else if (ganttZoom.value === 'month') {
		// 显示未来一个月
		start = now;
		end = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
	} else {
		// 显示全部
		start = Math.min(...ganttAssignments.value.map((a) => a.startDate?.getTime() || Date.now()));
		end = Math.max(...ganttAssignments.value.map((a) => a.deadlineDate?.getTime() || Date.now()));
	}
	
	if (start === end) {
		end = end + 24 * 60 * 60 * 1000;
	}
	
	return { start, end };
});

const timelineBounds = computed(() => ganttTimeRange.value);

// 筛选后的甘特图作业
const filteredGanttAssignments = computed(() => {
	let filtered = ganttAssignments.value;
	
	// 按课程筛选
	if (ganttCourseFilter.value && ganttCourseFilter.value !== 'all') {
		filtered = filtered.filter(a => String(a.course.id) === String(ganttCourseFilter.value));
	}
	
	// 按状态筛选
	if (ganttStatusFilter.value && ganttStatusFilter.value !== 'all') {
		filtered = filtered.filter(a => a.status === ganttStatusFilter.value);
	}
	
	// 按时间范围筛选（如果设置了缩放）
	if (ganttTimeRange.value) {
		filtered = filtered.filter(a => {
			const assignmentEnd = a.deadlineDate?.getTime();
			const assignmentStart = a.startDate?.getTime();
			const rangeStart = ganttTimeRange.value.start;
			const rangeEnd = ganttTimeRange.value.end;
			
			// 作业与时间范围有交集
			return assignmentEnd >= rangeStart && assignmentStart <= rangeEnd;
		});
	}
	
	return filtered.sort((a, b) => {
		if (!a.deadlineDate || !b.deadlineDate) return 0;
		return a.deadlineDate - b.deadlineDate;
	});
});

// 时间轴刻度
const timelineTicks = computed(() => {
	const bounds = timelineBounds.value;
	if (!bounds) return [];
	
	const ticks = [];
	const total = bounds.end - bounds.start;
	const days = Math.ceil(total / (24 * 60 * 60 * 1000));
	
	// 根据时间范围决定刻度间隔
	let interval = 1; // 默认每天一个刻度
	if (days > 60) {
		interval = 7; // 超过60天，每周一个刻度
	} else if (days > 14) {
		interval = 3; // 超过14天，每3天一个刻度
	}
	
	const startDate = new Date(bounds.start);
	const endDate = new Date(bounds.end);
	
	for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + interval)) {
		// 确保日期有效
		if (isNaN(d.getTime())) continue;
		const position = ((d.getTime() - bounds.start) / total) * 100;
		if (position >= 0 && position <= 100) {
			ticks.push({
				date: d.toISOString(),
				position,
				label: formatGanttDate(d),
			});
		}
	}
	
	return ticks;
});

// 今天的位置
const todayPosition = computed(() => {
	const bounds = timelineBounds.value;
	if (!bounds) return 0;
	const now = new Date().getTime();
	if (now < bounds.start || now > bounds.end) return -1;
	return ((now - bounds.start) / (bounds.end - bounds.start)) * 100;
});

const isTodayInRange = computed(() => {
	const bounds = timelineBounds.value;
	if (!bounds) return false;
	const now = new Date().getTime();
	return now >= bounds.start && now <= bounds.end;
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

// 格式化甘特图日期
const formatGanttDate = (date) => {
	if (!date) return '';
	const d = date instanceof Date ? date : new Date(date);
	if (isNaN(d.getTime())) return '';
	return formatDateUtil(d, 'MM-DD');
};

// 缩放控制
const zoomGantt = (zoom) => {
	ganttZoom.value = zoom;
};

// 跳转到作业详情
const goToHomework = (assignment) => {
	router.push({ name: 'HomeworkView', params: { id: assignment.id } });
};

// 跳转到所有作业页面（带筛选）
const goToAllHomeworks = (filter = 'all') => {
	if (isHistorySemesterMode.value) {
		router.push({ 
			name: 'HistorySemesterAllHomeworksView', 
			params: { semester: viewingSemester.value },
			query: { filter } 
		});
	} else {
		router.push({ name: 'AllHomeworksView', query: { filter } });
	}
};

const ganttLegend = computed(() => [
	{ status: 'pending', label: '未提交', color: statusMeta('pending').color },
	{ status: 'due-soon', label: '临近截止', color: statusMeta('due-soon').color },
	{ status: 'overdue', label: '已逾期', color: statusMeta('overdue').color },
	{ status: 'submitted', label: '已提交', color: statusMeta('submitted').color },
	{ status: 'completed', label: '已完成', color: statusMeta('completed').color },
]);

// 所有有提交记录的作业
const allSubmissions = computed(() => {
	return assignments.value
		.filter((a) => {
			// 只统计当前查看学期的作业
			if (a.course.semester !== viewingSemester.value) return false;
			return a.submission;
		})
		.sort((a, b) => (b.submissionDate || 0) - (a.submissionDate || 0));
});

// 最近提交的作业（用于时间轴显示，限制数量）
const recentSubmissions = computed(() => {
	return allSubmissions.value.slice(0, 10); // 显示最近10条
});

const onTimeRate = computed(() => {
	// 计算所有有截止日期的作业（不管是否已提交）（只统计当前查看学期的作业）
	const allWithDeadline = assignments.value.filter((a) => {
		// 只统计当前查看学期的作业
		if (a.course.semester !== viewingSemester.value) return false;
		// 必须有截止日期且是有效的Date对象
		if (!a.deadlineDate) return false;
		const deadline = a.deadlineDate instanceof Date ? a.deadlineDate : new Date(a.deadlineDate);
		return !isNaN(deadline.getTime());
	});
	
	if (!allWithDeadline.length) return 0;
	
	// 按时提交：提交时间 <= 截止时间
	const onTime = [];
	const notOnTime = [];
	const noSubmission = [];
	
	allWithDeadline.forEach((a) => {
		// 确保截止日期是有效的 Date 对象
		let deadlineDate = a.deadlineDate;
		if (!(deadlineDate instanceof Date)) {
			if (typeof deadlineDate === 'string') {
				deadlineDate = new Date(deadlineDate.replace(/-/g, '/'));
			} else {
				deadlineDate = new Date(deadlineDate);
			}
		}
		
		if (isNaN(deadlineDate.getTime())) {
			return; // 跳过无效的截止日期
		}
		
		// 如果没有提交记录，不计入按时提交，但计入分母
		if (!a.submission || !a.submissionDate) {
			noSubmission.push({
				title: a.title,
				deadline: deadlineDate.toISOString(),
			});
			return;
		}
		
		// 确保提交日期是有效的 Date 对象
		let submissionDate = a.submissionDate;
		if (!(submissionDate instanceof Date)) {
			if (typeof submissionDate === 'string') {
				submissionDate = new Date(submissionDate.replace(/-/g, '/'));
			} else {
				submissionDate = new Date(submissionDate);
			}
		}
		
		// 检查日期是否有效
		if (isNaN(submissionDate.getTime())) {
			return; // 跳过无效的提交日期
		}
		
		// 提交时间必须 <= 截止时间（使用时间戳比较）
		const isOnTime = submissionDate.getTime() <= deadlineDate.getTime();
		
		if (isOnTime) {
			onTime.push({
				title: a.title,
				submission: submissionDate.toISOString(),
				deadline: deadlineDate.toISOString(),
			});
		} else {
			notOnTime.push({
				title: a.title,
				submission: submissionDate.toISOString(),
				deadline: deadlineDate.toISOString(),
				diffHours: (submissionDate.getTime() - deadlineDate.getTime()) / (1000 * 60 * 60),
			});
		}
	});
	
	const rate = allWithDeadline.length > 0 ? Math.round((onTime.length / allWithDeadline.length) * 100) : 0;
	
	// 调试信息（始终显示，方便排查问题）
	console.log('=== 按时提交率计算详情 ===');
	console.log('总作业数:', assignments.value.length);
	console.log('有截止日期的作业数:', allWithDeadline.length);
	console.log('按时提交的作业:', onTime);
	console.log('未按时提交的作业:', notOnTime);
	console.log('未提交的作业:', noSubmission);
	console.log('按时提交数:', onTime.length);
	console.log('按时提交率:', rate + '%');
	console.log('计算方式:', `${onTime.length} / ${allWithDeadline.length} = ${(onTime.length / allWithDeadline.length * 100).toFixed(2)}%`);
	console.log('========================');
	
	return rate;
});

const scoreSegments = computed(() => {
	// 最近有提交的记录（用于分数统计，使用所有提交）
	const recent = allSubmissions.value;
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
		const rawScore = assignment.submission?.score ?? 0;
		// 获取作业的满分，默认为100
		const maxScore = assignment.max_score || assignment.maxScore || 100;
		
		// 将分数转换为百分制
		const scoreInPercent = maxScore > 0 ? (rawScore / maxScore) * 100 : 0;
		
		// 根据百分制分数进行分类
		if (scoreInPercent >= 90) {
			segments[0].value += 1;
		} else if (scoreInPercent >= 80) {
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

// 可用学期列表（从课程中提取）
const availableSemesters = computed(() => {
	const semesters = new Set();
	courses.value.forEach(course => {
		if (course.semester) {
			semesters.add(course.semester);
		}
	});
	return Array.from(semesters).sort().reverse(); // 按时间倒序
});

// 当前学期（根据当前时间自动判断，缓存结果避免重复计算）
const currentSemesterInfo = getCurrentSemester();
const currentSemester = computed(() => currentSemesterInfo.semester);

// 当前查看的学期（如果是历史学期页面，使用路由参数；否则使用当前学期）
const viewingSemester = computed(() => {
  // 检查路由参数中是否有学期信息
  if (route.name === 'HistorySemesterHome' && route.params.semester) {
    return route.params.semester;
		}
  return currentSemester.value;
});

// 是否为历史学期模式
const isHistorySemesterMode = computed(() => {
  return route.name === 'HistorySemesterHome' && route.params.semester;
});

// 历史学期列表（去掉当前学期，其余从近到远）
const historySemesters = computed(() => {
	// 过滤掉当前学期，确保历史学期不包含当前学期
	const history = availableSemesters.value.filter(semester => semester !== currentSemester.value);
	// 调试信息：帮助确认是否有历史学期
	if (process.env.NODE_ENV === 'development') {
		console.log('学期信息:', {
			所有学期: availableSemesters.value,
			当前学期: currentSemester.value,
			历史学期: history,
			历史学期数量: history.length,
		});
	}
	return history;
});

// 当前学期课程（在历史学期模式下，显示该历史学期的课程）
const currentSemesterCourses = computed(() => {
	if (!viewingSemester.value) return courses.value;
	return courses.value.filter(course => course.semester === viewingSemester.value);
});

// 历史学期课程（根据选中的历史学期筛选）
const filteredHistoryCourses = computed(() => {
	if (!selectedHistorySemester.value) return [];
	return courses.value.filter(course => course.semester === selectedHistorySemester.value);
});

// 显示的历史课程列表（根据是否展开）
const displayedHistoryCourses = computed(() => {
	if (showAllHistoryCourses.value || filteredHistoryCourses.value.length <= maxHistoryCoursesDisplay.value) {
		return filteredHistoryCourses.value;
	}
	return filteredHistoryCourses.value.slice(0, maxHistoryCoursesDisplay.value);
});

// 导航栏显示的课程列表（限制数量）
const displayedNavCourses = computed(() => {
	if (currentSemesterCourses.value.length <= maxNavCoursesDisplay.value) {
		return currentSemesterCourses.value;
	}
	return currentSemesterCourses.value.slice(0, maxNavCoursesDisplay.value);
});

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

// 助教切换角色
const handleSwitchRole = () => {
	userStore.switchTARole();
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
	// 加载当前用户的个性化设置
	personalizationStore.loadUserSettings();
	await fetchData();
});

// 监听 viewingSemester 变化，当切换到历史学期时重新获取数据
watch(viewingSemester, async (newSemester, oldSemester) => {
	// 如果学期发生变化，重新获取数据
	if (newSemester !== oldSemester) {
		await fetchData();
	}
}, { immediate: false });

// 监听路由变化，当切换到历史学期页面时重新获取数据
watch(() => route.name, async (newRouteName) => {
	if (newRouteName === 'HistorySemesterHome' || newRouteName === 'StudentHome') {
		await fetchData();
	}
}, { immediate: false });
</script>

<style scoped>
/* 应用个性化卡片样式 */
:deep(.el-card) {
	background-color: v-bind('cardStyle.backgroundColor') !important;
	color: v-bind('cardStyle.color') !important;
	border-color: v-bind('cardStyle.borderColor') !important;
}
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
	margin-left: 4px;
	padding-left: 12px;
	display: flex;
	justify-content: space-between;
	align-items: center;
	position: relative;
}

.section-header-right {
	display: flex;
	align-items: center;
	gap: 12px;
}

.section-header::before {
	content: '';
	position: absolute;
	left: 0;
	top: 50%;
	transform: translateY(-50%);
	width: 4px;
	height: 20px;
	background: linear-gradient(135deg, #409EFF, #67C23A);
	border-radius: 2px;
}

.section-title {
	font-size: 20px;
	font-weight: 600;
	color: #303133;
	margin: 0;
}

.course-count {
	font-size: 14px;
	color: #909399;
	margin-right: 8px;
	padding: 4px 12px;
	background-color: #f5f7fa;
	border-radius: 12px;
	display: inline-flex;
	align-items: center;
}

.history-semester-dialog {
	padding: 20px 0;
}

.dialog-tip {
	margin-bottom: 16px;
	color: #606266;
	font-size: 14px;
}

.history-courses-preview {
	margin-top: 24px;
}

.preview-title {
	margin-bottom: 12px;
	font-weight: 600;
	color: #303133;
}

.history-courses-list {
	display: flex;
	flex-direction: column;
	gap: 12px;
	max-height: 400px;
	overflow-y: auto;
}

.history-course-card {
	cursor: pointer;
	transition: transform 0.2s, box-shadow 0.2s;
}

.history-course-card:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.history-course-info h4 {
	margin: 0 0 8px 0;
	font-size: 16px;
	color: #303133;
}

.history-course-info .course-code {
	margin: 8px 0;
	color: #909399;
	font-size: 13px;
}

.history-courses-footer {
	margin-top: 16px;
	text-align: center;
	padding-top: 16px;
	border-top: 1px solid #ebeef5;
}

.results-limit-hint {
	color: #909399;
	font-size: 12px;
	margin-left: 8px;
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

.tabs-with-count {
	display: flex;
	align-items: center;
	gap: 16px;
	flex: 1;
}

.homework-count {
	font-size: 14px;
	color: #909399;
	margin-left: auto;
	white-space: nowrap;
}

.homework-grid-wrapper {
	width: 100%;
}

.homework-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
	grid-auto-flow: row;
	gap: 16px;
	width: 100%;
	align-items: stretch;
}

.course-more-actions,
.homework-more-actions {
	display: flex;
	justify-content: center;
	align-items: center;
	margin-top: 20px;
	padding: 16px;
}

.homework-item {
	border-radius: 12px;
	transition: transform 0.2s ease;
	position: relative;
	display: flex;
	flex-direction: column;
	height: 100%;
}

.homework-item :deep(.el-card__body) {
	display: flex;
	flex-direction: column;
	flex: 1;
	padding: 16px;
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
	flex: 1;
}

.homework-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-top: auto;
	padding-top: 16px;
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

.gantt-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	flex-wrap: wrap;
	gap: 12px;
}

.gantt-title-wrapper {
	display: flex;
	align-items: center;
	gap: 8px;
}

.gantt-controls {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: 8px;
}

.gantt-wrapper {
	display: flex;
	flex-direction: column;
	gap: 16px;
}

.gantt-help-icon {
	margin-left: 8px;
	color: #909399;
	cursor: help;
	font-size: 16px;
}

.gantt-intro {
	padding: 10px 16px;
	background: linear-gradient(135deg, #f0f7ff 0%, #f5f9ff 100%);
	border-radius: 8px;
	margin-bottom: 16px;
	border: 1px solid #e1ecff;
}

.intro-text {
	font-size: 13px;
	color: #606266;
	line-height: 1.6;
}

.gantt-legend {
	display: flex;
	align-items: center;
	gap: 12px;
	flex-wrap: wrap;
	color: #606266;
	padding: 12px 0;
	border-bottom: 2px solid #ebeef5;
	margin-bottom: 8px;
}

.legend-title {
	font-weight: 600;
	color: #303133;
	font-size: 14px;
}

.legend-item {
	display: flex;
	align-items: center;
	gap: 6px;
}

.gantt-legend .legend-color {
	width: 16px;
	height: 16px;
	border-radius: 4px;
	display: inline-block;
	flex-shrink: 0;
}

.legend-text {
	font-size: 13px;
}

/* 时间轴刻度 */
.gantt-timeline-header {
	position: relative;
	height: 60px;
	margin: 12px 0;
	border-bottom: 2px solid #e4e7ed;
	background: #fafbfc;
	border-radius: 4px;
	padding: 8px 0;
}

.timeline-label {
	position: absolute;
	right: 8px;
	bottom: 8px;
	font-size: 12px;
	color: #909399;
	font-weight: 500;
	padding: 2px 8px;
	background: rgba(255, 255, 255, 0.9);
	border-radius: 3px;
	z-index: 2;
}

.timeline-today-marker {
	position: absolute;
	top: 0;
	height: 100%;
	z-index: 15;
	pointer-events: none;
}

.today-line {
	position: absolute;
	top: 0;
	bottom: 0;
	left: 0;
	width: 2px;
	background: #f56c6c;
	box-shadow: 0 0 4px rgba(245, 108, 108, 0.5);
}

.today-label {
	position: absolute;
	top: -20px;
	left: 50%;
	transform: translateX(-50%);
	background: #f56c6c;
	color: #fff;
	padding: 2px 8px;
	border-radius: 4px;
	font-size: 11px;
	font-weight: 600;
	white-space: nowrap;
}

.timeline-tick {
	position: absolute;
	top: 0;
	height: 100%;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.tick-line {
	width: 2px;
	height: 20px;
	background: #409eff;
	margin-bottom: 4px;
}

.tick-label {
	font-size: 11px;
	color: #909399;
	white-space: nowrap;
	transform: translateX(-50%);
}

.gantt-chart {
	display: flex;
	flex-direction: column;
	gap: 16px;
	min-height: 200px;
	padding: 8px 0;
}

.gantt-row {
	display: flex;
	align-items: center;
	gap: 16px;
	padding: 8px 0;
	cursor: pointer;
	transition: all 0.2s ease;
	border-radius: 6px;
}

.gantt-row:hover {
	background: #f5f7fa;
	transform: translateX(4px);
}

.gantt-label {
	width: 220px;
	flex-shrink: 0;
	display: flex;
	flex-direction: column;
	gap: 4px;
	padding-right: 12px;
}

.gantt-label-title {
	font-weight: 600;
	color: #303133;
	font-size: 14px;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.gantt-label-course {
	font-size: 12px;
	color: #909399;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}

.gantt-label-deadline {
	font-size: 11px;
	color: #C0C4CC;
	margin-top: 2px;
}

.gantt-bar-container {
	flex: 1;
	height: 32px;
	background: #f0f2f5;
	border-radius: 8px;
	position: relative;
	overflow: visible;
}

.gantt-bar {
	position: absolute;
	top: 4px;
	bottom: 4px;
	border-radius: 6px;
	cursor: pointer;
	transition: all 0.3s ease;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	overflow: hidden;
	min-width: 60px;
}

.gantt-bar:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
	z-index: 10;
}

.gantt-bar-content {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: flex-start;
	padding: 4px 8px;
	height: 100%;
	color: #fff;
	font-size: 11px;
	line-height: 1.4;
	overflow: hidden;
}

.gantt-bar-title {
	font-weight: 600;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	width: 100%;
}

.gantt-bar-deadline {
	font-size: 10px;
	opacity: 0.9;
}

/* 今天指示线 */
.gantt-today-line {
	position: absolute;
	top: 0;
	bottom: 0;
	width: 2px;
	background: #f56c6c;
	z-index: 5;
	pointer-events: none;
}

.gantt-today-line::before {
	content: '';
	position: absolute;
	top: -4px;
	left: -4px;
	width: 10px;
	height: 10px;
	background: #f56c6c;
	border-radius: 50%;
}

.gantt-bar.status-pending {
	background: linear-gradient(135deg, #909399 0%, #a6a9ad 100%);
}

.gantt-bar.status-due-soon {
	background: linear-gradient(135deg, #e6a23c 0%, #f0a020 100%);
}

.gantt-bar.status-overdue {
	background: linear-gradient(135deg, #f56c6c 0%, #f78989 100%);
}

.gantt-bar.status-submitted {
	background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.gantt-bar.status-completed {
	background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.gantt-footer {
	margin-top: 12px;
	padding-top: 12px;
	border-top: 1px solid #ebeef5;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.gantt-stats {
	font-size: 13px;
	color: #606266;
	display: flex;
	align-items: center;
	gap: 8px;
}

.filter-hint {
	color: #909399;
	font-size: 12px;
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

.more-submissions-hint {
	margin-top: 16px;
	text-align: center;
	padding-top: 16px;
	border-top: 1px solid #ebeef5;
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
	transition: background 0.2s ease, color 0.2s ease;
	min-height: 60px;
	display: flex;
	flex-direction: column;
	justify-content: space-between;
}

.calendar-date-info {
	display: flex;
	flex-direction: column;
	align-items: flex-start;
	gap: 2px;
}

.day-number {
	font-weight: 500;
	font-size: 14px;
}

.month-day {
	font-size: 11px;
	color: #909399;
	opacity: 0.8;
}

.calendar-cell.has-deadline {
	background: rgba(64, 158, 255, 0.08);
}

.calendar-assignments {
	margin-top: 4px;
	display: flex;
	flex-direction: column;
	gap: 2px;
	max-height: 80px;
	overflow-y: auto;
	overflow-x: hidden;
	/* 自定义滚动条样式 */
	scrollbar-width: thin;
	scrollbar-color: rgba(64, 158, 255, 0.3) transparent;
}

.calendar-assignments::-webkit-scrollbar {
	width: 4px;
}

.calendar-assignments::-webkit-scrollbar-track {
	background: transparent;
}

.calendar-assignments::-webkit-scrollbar-thumb {
	background: rgba(64, 158, 255, 0.3);
	border-radius: 2px;
}

.calendar-assignments::-webkit-scrollbar-thumb:hover {
	background: rgba(64, 158, 255, 0.5);
}

.calendar-assignment-item {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 2px 4px;
	font-size: 10px;
	border-radius: 3px;
	background: rgba(64, 158, 255, 0.1);
	cursor: pointer;
	transition: background 0.2s;
}

.calendar-assignment-item:hover {
	background: rgba(64, 158, 255, 0.2);
}

.calendar-assignment-item.is-submitted {
	background: rgba(103, 194, 58, 0.1);
}

.calendar-assignment-item.is-submitted:hover {
	background: rgba(103, 194, 58, 0.2);
}

.assignment-title {
	flex: 1;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	color: #606266;
}

.calendar-assignment-item.is-submitted .assignment-title {
	color: #67C23A;
}

.assignment-status {
	color: #67C23A;
	font-weight: bold;
	font-size: 12px;
	margin-left: 4px;
}

.calendar-assignment-more {
	font-size: 9px;
	color: #909399;
	padding: 2px 4px;
	text-align: center;
}

.calendar-cell.is-selected {
	background: #409eff;
	color: #ffffff;
}

.calendar-cell.is-selected .month-day {
	color: rgba(255, 255, 255, 0.9);
}

.calendar-cell.is-in-range {
	background: rgba(64, 158, 255, 0.15);
}

.calendar-cell.is-range-boundary {
	background: #409eff;
	color: #ffffff;
	font-weight: 600;
}

.calendar-cell.is-range-boundary .month-day {
	color: rgba(255, 255, 255, 0.9);
}

.calendar-cell:hover {
	background: rgba(64, 158, 255, 0.2);
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

	.gantt-header {
		flex-direction: column;
		align-items: flex-start;
	}

	.gantt-controls {
		width: 100%;
		flex-wrap: wrap;
	}

	.gantt-label {
		width: 120px;
	}

	.gantt-bar-container {
		height: 28px;
	}

	.gantt-bar-content {
		font-size: 10px;
		padding: 2px 6px;
	}

	.gantt-timeline-header {
		height: 40px;
	}

	.tick-label {
		font-size: 10px;
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
	transform: translateX(-50%) !important;
	z-index: 1000;
	margin-top: 8px;
	width: 100%;
	max-width: 600px;
	max-height: 500px;
	overflow-y: auto;
	box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	will-change: auto;
}

.search-results-card:hover {
	transform: translateX(-50%) !important;
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
	position: relative;
}

.search-result-item:hover {
	background-color: #f5f7fa;
	transform: none;
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
