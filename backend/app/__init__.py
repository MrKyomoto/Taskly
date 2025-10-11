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
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.util.parse_identity import parse_identity


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

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)

    @app.route('/uploads/<path:filename>')  # 使用path转换器支持多级目录
    @jwt_required()
    def uploaded_file(filename):
        identity_str = get_jwt_identity()
        # NOTE: either student_id or reacher_id is None if we get the jwt identity
        student_id, student_error_response = parse_identity(
            identity_str, expected_role="student")
        teacher_id, teacher_error_response = parse_identity(
            identity_str, expected_role="teacher")
        if student_error_response or teacher_error_response:
            return jsonify({"error": "无权访问"}), 403

        path_parts = filename.split('/')
        if len(path_parts) < 3:
            return jsonify({"error": "无效的文件路径"}), 400

        stored_role = path_parts[0]  # NOTE: student or teacher
        stored_user_id = path_parts[1]

        if student_id and stored_role == "student":
            if stored_user_id != str(student_id):
                return jsonify({"error": "无权访问"}), 403
        elif teacher_id and stored_role == "teacher":
            if stored_user_id != str(teacher_id):
                return jsonify({"error": "无权访问"}), 403
        else:
            return jsonify({"error": "无权访问"}), 403

        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app
