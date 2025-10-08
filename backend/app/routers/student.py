"""
调用链: router -> handler -> service
- router: 路由层,由此层与前端直接交互
- handler: 处理层,router调用handler来处理业务
- service: 服务层,实际的处理业务层,handler只负责调用对应的服务
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.handlers.student_handler import (
    handle_student_login,
    handle_get_student_profile,
    handle_get_student_courses,
    handle_enroll_course,
    handle_get_enrolled_course_homeworks,
    handle_submit_homework,
    handle_upload_homework_image
)
from app.util.parse_identity import (
    parse_identity
)

# 认证相关路由蓝图
auth_bp = Blueprint('student_auth', __name__, url_prefix='/api/auth/students')

# 学生资源路由蓝图
student_bp = Blueprint('students', __name__, url_prefix='/api/students')

# 认证接口


@auth_bp.route('/login', methods=['POST'])
def login():
    """学生登录接口"""
    data = request.get_json()
    return handle_student_login(data)

# 学生个人信息接口


@student_bp.route('/me', methods=['GET'])
@jwt_required()
def get_student_profile():
    """获取当前登录学生的个人资料"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student")
    if error_response:
        return error_response
    return handle_get_student_profile(student_id)

# 学生课程相关接口


@student_bp.route('/me/courses', methods=['GET'])
@jwt_required()
def get_enrolled_courses():
    """获取当前学生已选课程"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student")
    if error_response:
        return error_response

    return handle_get_student_courses(student_id)


@student_bp.route('/me/courses', methods=['POST'])
@jwt_required()
def enroll_course():
    """学生选课(准确的说是加入班级)"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student")
    if error_response:
        return error_response

    data = request.get_json()
    return handle_enroll_course(student_id, data.get('course_code'))


@student_bp.route('me/courses/<course_id>/homeworks', methods=['GET'])
@jwt_required()
def get_enrolled_course_homeworks(course_id):
    """获取某门课程的所有作业"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student")
    if error_response:
        return error_response

    return handle_get_enrolled_course_homeworks(student_id, course_id)


@student_bp.route('me/homeworks/<homework_id>/upload-image', methods=['POST'])
@jwt_required()
def upload_homework_image(homework_id):
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student")
    if error_response:
        return error_response

    if 'file' not in request.files:
        return jsonify({"error": "未找到文件"}), 400
    files = request.files.getlist('file')
    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "未选择有效文件"}), 400

    return handle_upload_homework_image(student_id, homework_id, files)
