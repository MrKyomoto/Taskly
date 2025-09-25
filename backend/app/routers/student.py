"""
调用链: router -> handler -> service
- router: 路由层,由此层与前端直接交互
- handler: 处理层,router调用handler来处理业务
- service: 服务层,实际的处理业务层,handler只负责调用对应的服务
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.handlers.student_handler import (
    handle_student_login,
    handle_get_student_profile,
    handle_get_student_courses,
    handle_enroll_course,
    handle_get_enrolled_course_homeworks,
)
from app.util import (
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


@student_bp.route('me/homeworks/<homework_id>/submissions', methods=['POST'])
@jwt_required()
def submit_homework(homework_id):
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student")
    if error_response:
        return error_response
    data = request.get_json()
    # TODO: 是否需要在router里先对json进行解析再传入handler : 确实需要

    return handle_submit_homework(student_id, homework_id, homework)


@student_bp.route('me/homeworks/<homework_id>/grading', methods=['GET'])
@jwt_required()
    def get_ 
# from flask import Blueprint, request
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from app.handlers.student_handler import (
#     handle_student_login,
#     handle_get_student_profile,
#     handle_enroll_course,
#     handle_get_enrolled_courses,
#     handle_get_enrolled_course_homeworks,
#     handle_submit_homework
# )
#
# bp = Blueprint('student', __name__, url_prefix='/api/student')
#
# # 学生登录
#
#
# @bp.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     return handle_student_login(data)
#
# # 获取个人信息
#
#
# @bp.route('/profile', methods=['GET'])
# @jwt_required()
# def profile():
#     user_info = get_jwt_identity()  # 从JWT中获取用户信息
#     return handle_get_student_profile(user_info['id'])
#
# # 选课
#
#
# @bp.route('/courses/enroll', methods=['POST'])
# @jwt_required()
# def enroll():
#     user_info = get_jwt_identity()
#     data = request.json
#     return handle_enroll_course(student_id=user_info['id'], course_code=data.get('course_code'))
#
# # 获取已选课程
#
#
# @bp.route('/courses', methods=['GET'])
# @jwt_required()
# def get_courses():
#     user_info = get_jwt_identity()
#     return handle_get_enrolled_courses(student_id=user_info['id'])
#
#
# @bp.route('/courses/<course_id>/homeworks', methods=['GET'])
# @jwt_required()
# def get_course_homeworks(course_id):
#     user_info = get_jwt_identity()
#     return handle_get_enrolled_course_homeworks(student_id=user_info['id'], course_id=course_id)
#
#
# @bp.route('/courses/<course_id>/homeworks/<homework_id>/submit', methods=['POST'])
# @jwt_required()
# def submit_homework(course_id, homework_id):
#     user_info = get_jwt_identity()
#     data = request.json
#     return handle_submit_homework(student_id=user_info['id'], course_id=course_id, homework_id=homework_id, data=data)
