# Intro
1. Backend
- before dev, you should activate python virtual environment (provided that you have created a venv (remember that you should come into the project root dir before you create the venv so that the venv will generate in the root dir))
`venv\bin\activate`
- then install the requirements needed (listed in requirements.txt)
`pip install -r requirements.txt`
  - mirror source is: https://pypi.tuna.tsinghua.edu.cn/simple
  - `pip install -r requirements.txt -i <mirror source>`


backend/
├── app/
│   ├── __init__.py         # 应用工厂函数 create_app，初始化 Flask 应用和扩展
│   ├── models.py           # 【核心】数据库模型定义 (使用 SQLAlchemy)
│   ├── routers/            # 路由蓝图 (Blueprints)，按模块划分 API
│   │   ├── auth.py         # 认证相关路由 (登录、注册、获取用户信息)
│   │   ├── course.py       # 课程管理路由
│   │   ├── homework.py     # 作业管理路由
│   │   └── submission.py   # 作业提交与批改路由
│   ├── services/           # 业务逻辑层，处理具体业务，被路由调用
│   │   ├── auth_service.py
│   │   ├── course_service.py
│   │   └── homework_service.py
│   ├── schemas.py          # (可选，推荐) 数据校验与序列化 (使用 Marshmallow 或 Pydantic)
│   ├── extensions.py       # 统一管理 Flask 扩展实例 (如 db, migrate, jwt)
│   ├── config.py           # 配置文件 (开发、生产环境配置)
│   └── utils/              # 通用工具函数 (如文件上传、密码哈希等)
│
├── migrations/             # 数据库迁移脚本 (由 Flask-Migrate 自动管理)
├── tests/                  # 单元测试和集成测试
├── run.py                  # 应用启动脚本
└── requirements.txt        # Python 依赖包列表

2. Frontend
vue3+element

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
