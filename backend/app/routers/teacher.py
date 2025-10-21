from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.handlers.teacher_handler import (
    handle_teacher_login,
    handle_teacher_register,
    handle_get_teacher_profile,
    handle_get_teacher_courses,
    handle_create_course,
    handle_update_course,
    handle_create_homework,
    handle_get_course_homeworks,
    handle_get_student_submissions,
    handle_grade_submission,
    handle_update_teacher_profile,
    handle_update_teacher_password,
    handle_update_homework,
    handle_delete_homework,
    handle_get_course_students,
)
from app.util.parse_identity import parse_identity

# 认证相关路由蓝图
teacher_auth_bp = Blueprint('teacher_auth', __name__, url_prefix='/api/auth/teachers')

# 教师资源路由蓝图
teacher_bp = Blueprint('teachers', __name__, url_prefix='/api/teachers')

# 认证接口


@teacher_auth_bp.route('/login', methods=['POST'])
def login():
    """教师登录接口"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_teacher_login(data)


@teacher_auth_bp.route('/register', methods=['POST'])
def register():
    """教师注册接口"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_teacher_register(data)

# 教师个人信息接口


@teacher_bp.route('/me', methods=['GET'])
@jwt_required()
def get_teacher_profile():
    """获取当前登录教师的个人资料"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response
    return handle_get_teacher_profile(teacher_id)


@teacher_bp.route('/me', methods=['PATCH'])
@jwt_required()
def update_teacher_profile():
    """修改当前登录教师的个人资料"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    update_data = request.get_json()
    if not update_data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_update_teacher_profile(teacher_id, update_data)


@teacher_bp.route('/me/password', methods=['PATCH'])
@jwt_required()
def update_password():
    """修改当前登录教师的密码"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    password_data = request.get_json()
    if not password_data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_update_teacher_password(teacher_id, password_data)

# 教师课程相关接口


@teacher_bp.route('/me/courses', methods=['GET'])
@jwt_required()
def get_teacher_courses():
    """获取当前教师教授的课程"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    return handle_get_teacher_courses(teacher_id)


@teacher_bp.route('/me/courses', methods=['POST'])
@jwt_required()
def create_course():
    """创建新课程"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    course_data = request.get_json()
    if not course_data:
        return jsonify({"error": "课程数据不能为空"}), 400

    return handle_create_course(teacher_id, course_data)


@teacher_bp.route('/me/courses/<course_id>', methods=['PATCH'])
@jwt_required()
def update_course(course_id):
    """更新课程信息"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    update_data = request.get_json()
    if not update_data:
        return jsonify({"error": "更新数据不能为空"}), 400

    return handle_update_course(teacher_id, course_id, update_data)

# 作业相关接口


@teacher_bp.route('/me/courses/<course_id>/homeworks', methods=['GET'])
@jwt_required()
def get_course_homeworks(course_id):
    """获取课程下的所有作业"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    return handle_get_course_homeworks(teacher_id, course_id)


@teacher_bp.route('/me/courses/<course_id>/homeworks', methods=['POST'])
@jwt_required()
def create_homework(course_id):
    """创建课程作业"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    homework_data = request.get_json()
    if not homework_data:
        return jsonify({"error": "作业数据不能为空"}), 400

    return handle_create_homework(teacher_id, course_id, homework_data)

# 批改相关接口


@teacher_bp.route('/me/courses/<course_id>/homeworks/<homework_id>/submissions', methods=['GET'])
@jwt_required()
def get_student_submissions(course_id, homework_id):
    """获取学生作业提交列表"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    return handle_get_student_submissions(teacher_id, course_id, homework_id)


@teacher_bp.route('/me/submissions/<submission_id>/grade', methods=['POST'])
@jwt_required()
def grade_submission(submission_id):
    """批改学生作业"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    grade_data = request.get_json()
    if not grade_data:
        return jsonify({"error": "评分数据不能为空"}), 400

    return handle_grade_submission(teacher_id, submission_id, grade_data)

# 编辑作业


@teacher_bp.route('/courses/<course_id>/homeworks/<homework_id>', methods=['PUT'])
@jwt_required()
def update_homework(course_id, homework_id):
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")
    if error_response:
        return error_response

    homework_data = request.get_json()
    if not homework_data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_update_homework(staff_id, course_id, homework_id, homework_data)

# 删除作业


@teacher_bp.route('/courses/<course_id>/homeworks/<homework_id>', methods=['DELETE'])
@jwt_required()
def delete_homework(course_id, homework_id):
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")
    if error_response:
        return error_response

    return handle_delete_homework(staff_id, course_id, homework_id)

# 查看选课学生列表


@teacher_bp.route('/courses/<course_id>/students', methods=['GET'])
@jwt_required()
def get_course_students(course_id):
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")
    if error_response:
        return error_response

    return handle_get_course_students(staff_id, course_id)
