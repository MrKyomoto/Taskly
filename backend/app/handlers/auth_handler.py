"""
统一认证处理器
"""
from flask import jsonify
from flask_jwt_extended import create_access_token
from app.services.auth_service import unified_authenticate, check_identifier_exists


def handle_unified_login(data):
    """
    处理统一登录请求
    :param data: 包含 username 和 password 的字典
    :return: Flask Response
    """
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    success, result = unified_authenticate(username, password)
    
    if not success:
        return jsonify({"error": result}), 401

    # 创建JWT令牌（格式："role:id"）
    role = result["role"]
    user_id = result["id"]
    identity_str = f"{role}:{user_id}"
    access_token = create_access_token(identity=identity_str)

    # 根据角色返回不同的用户数据字段
    response_data = {
        "access_token": access_token,
        "role": role,
    }

    # 根据角色添加对应的用户信息字段
    if role == "admin":
        response_data["admin"] = result["user_data"]
    elif role == "teacher" or role == "ta":
        response_data["teacher"] = result["user_data"]
    elif role == "student":
        response_data["student"] = result["user_data"]

    return jsonify(response_data), 200


def handle_check_identifier(data):
    """
    处理检查账号是否存在的请求（用于忘记密码）
    :param data: 包含 identifier 的字典
    :return: Flask Response
    """
    identifier = data.get('identifier')
    if not identifier:
        return jsonify({"error": "账号不能为空"}), 400

    success, result = check_identifier_exists(identifier)
    if success:
        return jsonify(result), 200
    return jsonify({"error": result}), 400

