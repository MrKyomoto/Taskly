"""
统一认证路由
"""
from flask import Blueprint, request, jsonify
from app.handlers.auth_handler import handle_unified_login, handle_check_identifier

# 统一认证路由蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """统一登录接口"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_unified_login(data)


@auth_bp.route('/check-identifier', methods=['POST'])
def check_identifier():
    """检查账号是否存在（用于忘记密码）"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_check_identifier(data)

