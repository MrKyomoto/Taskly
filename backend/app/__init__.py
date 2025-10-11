"""
应用工厂函数，负责创建和配置 Flask 应用：
- 加载配置（Config 类）
- 初始化扩展（数据库、JWT、CORS 等）
- 注册路由蓝图（routers 中的模块）
"""
from flask import Flask, send_from_directory, jsonify
from flask_migrate import Migrate
from app.config import Config
from app.extensions import db, jwt
from app.routers.student import student_bp, auth_bp
from app.routers.access_image_router import upload_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    Migrate(app, db)
    with app.app_context():
        from app.models import (
            Student, Staff, Admin, Course,  # 基础模型
            StudentCourseRelation, StaffCourseRelation,  # 多对多关联表
            Homework, HomeworkSubmission, HomeworkGrading,  # 作业相关模型
            StaffRole, CourseStatus, HomeworkType  # 枚举类可选，不导入也不影响建表
        )

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(upload_bp)

    return app
