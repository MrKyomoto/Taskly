from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.handlers.admin_handler import (
    handle_admin_login,
    handle_admin_register,  # 可选：仅超级管理员可用
    handle_get_all_teachers,
    handle_get_all_students,
    handle_get_all_staff,
    handle_create_staff,
    handle_reset_user_password,
    handle_approve_course,
    handle_get_all_courses,
    handle_delete_user,
    handle_get_admin_profile,
    handle_update_admin_profile,
    handle_update_admin_password,
    handle_create_student,
    handle_update_student,
    handle_update_staff,
    handle_create_course,
    handle_update_course,
    handle_close_course,
    handle_delete_course,
    handle_add_teacher_to_course,
    handle_add_ta_to_course,
    handle_add_student_to_course
)
from app.util.parse_identity import parse_identity

# 管理员认证路由
admin_auth_bp = Blueprint('admin_auth', __name__,
                          url_prefix='/api/auth/admins')

# 管理员资源路由
admin_bp = Blueprint('admins', __name__, url_prefix='/api/admins')

# 登录接口


@admin_auth_bp.route('/login', methods=['POST'])
def login():
    """管理员登录"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_admin_login(data)

# 注册接口（谨慎开放，建议仅初始化时使用）


@admin_auth_bp.route('/register', methods=['POST'])
@jwt_required()  # 需管理员身份才能创建新管理员
def register():
    """创建新管理员（需现有管理员权限）"""
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_admin_register(data)

# 获取所有教师


@admin_bp.route('/teachers', methods=['GET'])
@jwt_required()
def get_all_teachers():
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response
    return handle_get_all_teachers()

# 获取所有学生


@admin_bp.route('/students', methods=['GET'])
@jwt_required()
def get_all_students():
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response
    return handle_get_all_students()

# 课程审核


@admin_bp.route('/courses/<course_id>/approve', methods=['POST'])
@jwt_required()
def approve_course(course_id):
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    return handle_approve_course(course_id, data)

# 获取所有课程


@admin_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_all_courses():
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response
    return handle_get_all_courses()

# 删除用户（教师/学生）


@admin_bp.route('/users/<user_type>/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_type, user_id):
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    if user_type not in ['teacher', 'student']:
        return jsonify({"error": "用户类型必须为teacher或student"}), 400
    return handle_delete_user(user_type, user_id)

# 获取管理员个人资料


@admin_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_admin_profile():
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response
    return handle_get_admin_profile(admin_id)

# 更新管理员资料


@admin_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_admin_profile():
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    return handle_update_admin_profile(admin_id, data)

# 更新管理员密码


@admin_bp.route('/password', methods=['PATCH'])
@jwt_required()
def update_admin_password():
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    return handle_update_admin_password(admin_id, data)

# 获取所有教职工（包括教师和助教）
@admin_bp.route('/staff', methods=['GET'])
@jwt_required()
def get_all_staff():
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response
    return handle_get_all_staff()

# 创建教职工
@admin_bp.route('/staff', methods=['POST'])
@jwt_required()
def create_staff():
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_create_staff(data)

# 重置用户密码
@admin_bp.route('/users/<user_type>/<user_id>/reset-password', methods=['PATCH'])
@jwt_required()
def reset_user_password(user_type, user_id):
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    if user_type not in ['staff', 'student']:
        return jsonify({"error": "用户类型必须为staff或student"}), 400

    data = request.get_json() or {}
    return handle_reset_user_password(user_type, user_id, data)

# 创建学生
@admin_bp.route('/students', methods=['POST'])
@jwt_required()
def create_student():
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_create_student(data)

# 更新学生
@admin_bp.route('/students/<student_id>', methods=['PATCH'])
@jwt_required()
def update_student(student_id):
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_update_student(student_id, data)

# 更新教职工
@admin_bp.route('/staff/<staff_id>', methods=['PATCH'])
@jwt_required()
def update_staff(staff_id):
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_update_staff(staff_id, data)

# 创建课程
@admin_bp.route('/courses', methods=['POST'])
@jwt_required()
def create_course():
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_create_course(data)

# 更新课程
@admin_bp.route('/courses/<course_id>', methods=['PATCH'])
@jwt_required()
def update_course(course_id):
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_update_course(course_id, data)

# 课程结课
@admin_bp.route('/courses/<course_id>/close', methods=['POST'])
@jwt_required()
def close_course(course_id):
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    return handle_close_course(course_id)

# 删除课程
@admin_bp.route('/courses/<course_id>', methods=['DELETE'])
@jwt_required()
def delete_course(course_id):
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    return handle_delete_course(course_id)

# 管理员添加教师到课程
@admin_bp.route('/courses/<course_id>/add-teacher', methods=['POST'])
@jwt_required()
def add_teacher_to_course(course_id):
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_add_teacher_to_course(course_id, data)

# 管理员添加助教到课程
@admin_bp.route('/courses/<course_id>/add-ta', methods=['POST'])
@jwt_required()
def add_ta_to_course(course_id):
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_add_ta_to_course(course_id, data)

# 管理员添加学生到课程
@admin_bp.route('/courses/<course_id>/add-student', methods=['POST'])
@jwt_required()
def add_student_to_course(course_id):
    identity_str = get_jwt_identity()
    admin_id, error_response = parse_identity(
        identity_str, expected_role="admin")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_add_student_to_course(course_id, data)
