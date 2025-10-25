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
    handle_student_register,
    handle_get_student_profile,
    handle_get_student_courses,
    handle_enroll_course,
    handle_get_enrolled_course_homeworks,
    handle_submit_homework,
    handle_upload_homework_image,
    handle_update_student_profile,
    handle_update_student_password,
    handle_get_student_submission,
)
from app.util.parse_identity import (
    parse_identity
)

# 认证相关路由蓝图
student_auth_bp = Blueprint('student_auth', __name__, url_prefix='/api/auth/students')

# 学生资源路由蓝图
student_bp = Blueprint('students', __name__, url_prefix='/api/students')

# 认证接口


@student_auth_bp.route('/login', methods=['POST'])
def login():
    """学生登录接口"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_student_login(data)


@student_auth_bp.route('/register', methods=['POST'])
def register():
    """学生注册接口"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_student_register(data)

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


@student_bp.route('/me', methods=['PATCH'])
@jwt_required()
def update_student_profile_route():
    """修改当前登录学生的个人资料"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student")
    if error_response:
        return error_response

    update_data = request.get_json()
    if not update_data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_update_student_profile(student_id, update_data)


@student_bp.route('/me/password', methods=['PATCH'])
@jwt_required()
def update_password():
    """修改当前登录学生的密码"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student"
    )
    if error_response:
        return error_response

    password_data = request.get_json()
    if not password_data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_update_student_password(student_id, password_data)
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


@student_bp.route('/me/courses/<course_id>/homeworks', methods=['GET'])
@jwt_required()
def get_enrolled_course_homeworks(course_id):
    """获取某门课程的所有作业"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student")
    if error_response:
        return error_response

    return handle_get_enrolled_course_homeworks(student_id, course_id)


@student_bp.route('/me/courses/<course_id>/homeworks/<homework_id>/submission', methods=['GET'])
@jwt_required()
def get_homework_submission(course_id, homework_id):
    """查看当前学生在某课程中某作业的提交内容"""
    # 解析身份信息
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student"
    )
    if error_response:
        return error_response

    # 参数校验（确保ID为数字）
    try:
        course_id = int(course_id)
        homework_id = int(homework_id)
    except ValueError:
        return jsonify({"error": "课程ID和作业ID必须为数字"}), 400

    return handle_get_student_submission(student_id, course_id, homework_id)


@student_bp.route('/me/homeworks/<homework_id>/upload-image', methods=['POST'])
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


@student_bp.route('/me/homeworks/<homework_id>/submission', methods=['POST'])
@jwt_required()
def submit_homework(homework_id):
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student")
    if error_response:
        return error_response
    homework_data = request.get_json()
    if not homework_data:
        return jsonify({"error": "提交数据不能为空"}), 400

    return handle_submit_homework(student_id=student_id, homework_id=homework_id, homework_data=homework_data)
