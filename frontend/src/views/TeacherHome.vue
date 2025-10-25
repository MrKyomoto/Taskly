<template>
  <div class="teacher-home">
    <!-- 左侧导航区 -->
    <div class="left-panel">
      <div class="user-profile">
        <el-avatar :size="60" icon="el-icon-user-solid"></el-avatar>
        <div class="user-info">
          <h4>{{ teacherName }}</h4>
          <p>教师</p>
        </div>
      </div>
      <el-menu default-active="1" class="course-menu">
        <el-sub-menu index="1">
          <template #title>
            <i class="el-icon-collection"></i>
            <span>我的课程</span>
          </template>
          <el-menu-item 
            v-for="course in courses" 
            :key="course.id" 
            :index="`1-${course.id}`"
            @click="selectCourse(course.id)"
          >
            {{ course.course_name }}
          </el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="2">
          <template #title>
            <i class="el-icon-setting"></i>
            <span>更多工具</span>
          </template>
          <el-menu-item index="2-1" title="题库管理"><i class="el-icon-files"></i></el-menu-item>
          <el-menu-item index="2-2" title="学生分组"><i class="el-icon-user-solid"></i></el-menu-item>
        </el-sub-menu>
      </el-menu>
    </div>

    <!-- 中间核心作业管理区 -->
    <div class="main-content">
      <header class="main-header">
        <h1>{{ selectedCourseName }}</h1>
        <div class="actions">
          <el-button type="primary" icon="el-icon-plus" @click="createHomework">快速创建</el-button>
          <el-button icon="el-icon-document-copy" @click="reuseTemplate">模板复用</el-button>
          <el-badge :value="3" class="notification-badge">
            <i class="el-icon-bell" style="font-size: 24px;"></i>
          </el-badge>
        </div>
      </header>

      <!-- 顶部三大快捷模块 -->
      <el-row :gutter="20" class="quick-stats">
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-title">待批改作业</div>
            <div class="stat-value">125 <span class="stat-unit">份</span></div>
            <el-button type="text">一键批改 &rarr;</el-button>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-title">今日截止作业</div>
            <div class="stat-value">3 <span class="stat-unit">项</span></div>
            <el-button type="text">查看详情 &rarr;</el-button>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-title">班级作业完成率</div>
            <div class="stat-value">88 <span class="stat-unit">%</span></div>
            <el-button type="text">学情分析 &rarr;</el-button>
          </el-card>
        </el-col>
      </el-row>

      <!-- 作业列表 -->
      <div class="homework-list">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="全部作业" name="all"></el-tab-pane>
          <el-tab-pane label="已发布" name="published"></el-tab-pane>
          <el-tab-pane label="草稿箱" name="draft"></el-tab-pane>
        </el-tabs>
        <el-table :data="homeworks" v-loading="loading" element-loading-text="加载中...">
          <el-table-column prop="title" label="作业标题"></el-table-column>
          <el-table-column prop="deadline" label="截止时间"></el-table-column>
          <el-table-column prop="submission_status" label="提交情况"></el-table-column>
          <el-table-column label="操作">
            <template #default>
              <el-button type="text" size="small">批改</el-button>
              <el-button type="text" size="small">编辑</el-button>
              <el-button type="text" size="small" style="color: #F56C6C;">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 右侧数据可视化区 -->
    <div class="right-panel">
      <el-card class="chart-card">
        <template #header>
          <span>班级完成率</span>
        </template>
        <div ref="completionChart" class="chart"></div>
      </el-card>
      <el-card class="chart-card">
        <template #header>
          <span>成绩趋势</span>
        </template>
        <div ref="gradeChart" class="chart"></div>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, nextTick } from 'vue';
import * as echarts from 'echarts';
// 从新的 API 文件中导入函数
import { getTeacherProfile, getTeacherCourses, getCourseHomeworks } from '@/api/teacher.js';

export default {
  name: 'TeacherHome',
  setup() {
    const teacherName = ref('教师');
    const courses = ref([]);
    const selectedCourseId = ref(null);
    const homeworks = ref([]);
    const loading = ref(true);
    const activeTab = ref('all');

    const completionChart = ref(null);
    const gradeChart = ref(null);

    let completionChartInstance = null;
    let gradeChartInstance = null;

    const selectedCourseName = computed(() => {
      const course = courses.value.find(c => c.id === selectedCourseId.value);
      return course ? course.course_name : '请选择课程';
    });

    const fetchInitialData = async () => {
      try {
        loading.value = true;
        // 获取教师信息
        const profileResponse = await getTeacherProfile();
        teacherName.value = profileResponse.data.name;
        
        // 获取课程列表
        const courseResponse = await getTeacherCourses();
        courses.value = courseResponse.data;
        if (courses.value.length > 0) {
          selectedCourseId.value = courses.value[0].id;
          await fetchHomeworks(selectedCourseId.value);
        }
        initCharts();
      } catch (error) {
        console.error("数据加载失败:", error);
        // 可以在此处添加用户友好的错误提示，例如使用 ElMessage
      } finally {
        loading.value = false;
      }
    };

    const fetchHomeworks = async (courseId) => {
        loading.value = true;
        try {
            const response = await getCourseHomeworks(courseId);
            // 格式化截止日期
            homeworks.value = response.data.map(hw => ({
                ...hw,
                deadline: new Date(hw.deadline).toLocaleString()
            }));
        } catch (error) {
            console.error(`获取课程 ${courseId} 的作业失败:`, error);
            homeworks.value = []; // 清空作业列表以防显示旧数据
        } finally {
            loading.value = false;
        }
    };

    const selectCourse = (courseId) => {
        selectedCourseId.value = courseId;
        fetchHomeworks(courseId);
    };

    const createHomework = () => {
      console.log('快速创建作业');
    };

    const reuseTemplate = () => {
      console.log('从模板复用作业');
    };

    const initCharts = () => {
      nextTick(() => {
        // 班级完成率 - 环形图
        completionChartInstance = echarts.init(completionChart.value);
        completionChartInstance.setOption({
          tooltip: { trigger: 'item' },
          series: [{
            name: '完成率',
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: { show: false, position: 'center' },
            emphasis: { label: { show: true, fontSize: '20', fontWeight: 'bold' } },
            labelLine: { show: false },
            data: [
              { value: 88, name: '已完成' },
              { value: 12, name: '未完成' }
            ]
          }]
        });

        // 成绩趋势 - 柱状图
        gradeChartInstance = echarts.init(gradeChart.value);
        gradeChartInstance.setOption({
          xAxis: { type: 'category', data: ['作业1', '作业2', '作业3', '作业4'] },
          yAxis: { type: 'value' },
          tooltip: { trigger: 'axis' },
          series: [{
            data: [82, 93, 90, 85],
            type: 'bar',
            itemStyle: { color: '#409EFF' }
          }]
        });
      });
    };

    onMounted(() => {
      fetchInitialData();
    });

    return {
      teacherName,
      courses,
      selectedCourseId,
      selectedCourseName,
      homeworks,
      loading,
      activeTab,
      completionChart,
      gradeChart,
      selectCourse,
      createHomework,
      reuseTemplate,
    };
  }
};
</script>

<style scoped>
.teacher-home {
  display: flex;
  height: 100vh;
  background-color: #f5f7fa;
}

/* 左侧面板 */
.left-panel {
  width: 240px;
  background-color: #fff;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
}
.user-profile {
  display: flex;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e6e6e6;
}
.user-info {
  margin-left: 15px;
}
.user-info h4 {
  margin: 0;
  font-size: 16px;
}
.user-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}
.course-menu {
  border-right: none;
  flex-grow: 1;
}
.course-menu .el-sub-menu .el-icon, .course-menu .el-menu-item .el-icon {
  font-size: 18px;
  vertical-align: middle;
  width: 24px;
  text-align: center;
}
.el-sub-menu [class^=el-icon] {
    vertical-align: middle;
}

/* 主内容区 */
.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.main-header h1 {
  margin: 0;
  font-size: 24px;
}
.main-header .actions {
  display: flex;
  align-items: center;
  gap: 15px;
}
.notification-badge {
  cursor: pointer;
}

/* 快捷统计 */
.quick-stats {
  margin-bottom: 20px;
}
.stat-card {
  text-align: center;
}
.stat-title {
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
}
.stat-unit {
  font-size: 14px;
  font-weight: normal;
  margin-left: 5px;
}
.stat-card .el-button {
  padding: 0;
  margin-top: 10px;
}

/* 作业列表 */
.homework-list {
  background-color: #fff;
  padding: 20px;
  border-radius: 4px;
}

/* 右侧面板 */
.right-panel {
  width: 300px;
  padding: 20px;
  padding-left: 0;
}
.chart-card {
  margin-bottom: 20px;
}
.chart {
  height: 200px;
}
</style>
