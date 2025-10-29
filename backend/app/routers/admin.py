from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.handlers.admin_handler import (
    handle_admin_login,
    handle_admin_register,  # 可选：仅超级管理员可用
    handle_get_all_teachers,
    handle_get_all_students,
    handle_approve_course,
    handle_get_all_courses,
    handle_delete_user,
    handle_get_admin_profile,
    handle_update_admin_profile,
    handle_update_admin_password
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
