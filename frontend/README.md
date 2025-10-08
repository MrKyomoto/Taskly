# Frontend
vue3+Element


frontend/
├── public/                 # 静态资源，不会被 Vite 处理
│   └── index.html          # HTML 入口文件
├── src/
│   ├── api/                # API 请求模块，封装对后端接口的调用
│   │   ├── auth.js
│   │   ├── course.js
│   │   └── index.js        # 统一导出和配置 axios 实例
│   ├── assets/             # 静态资源 (图片、全局 CSS 等)
│   │   └── styles/
│   │       └── main.css
│   ├── components/         # 可复用的 UI 组件
│   │   ├── AppLayout.vue   # 应用主布局 (含导航栏、侧边栏)
│   │   └── HomeworkCard.vue# 作业卡片组件
│   ├── views/              # 页面级组件
│   │   ├── Login.vue       # 登录页面
│   │   ├── Dashboard.vue   # 仪表盘/主页
│   │   ├── CourseDetail.vue# 课程详情页
│   │   └── HomeworkView.vue# 作业查看与提交页
│   ├── router/             # 路由配置 (Vue Router)
│   │   └── index.js
│   ├── store/              # 全局状态管理 (Pinia)
│   │   ├── user.js         # 用户信息和认证状态
│   │   └── course.js       # 课程数据状态
│   ├── App.vue             # 根组件
│   └── main.js             # 应用入口文件 (初始化 Vue、Router、Pinia)
│
├── .gitignore
├── package.json            # 项目依赖和脚本配置
├── vite.config.js          # Vite 配置文件 (可配置代理实现跨域)
└── README.md               # 前端项目说明
