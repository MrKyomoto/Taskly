from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.util.file_upload import save_uploaded_file, get_file_url

upload_bp = Blueprint('upload', __name__, url_prefix='/api/uploads')


@upload_bp.route('/images', methods=['POST'])
@jwt_required()
def upload_image():
    """通用图片上传接口（自动区分学生/教师目录）"""
    # 解析身份获取角色和ID
    identity_str = get_jwt_identity()
    try:
        role, user_id_str = identity_str.split(':', 1)
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        return jsonify({"error": "无效的身份信息"}), 401

    # 检查文件是否存在
    if 'file' not in request.files:
        return jsonify({"error": "未找到文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400

    # 调用工具函数保存到用户专属目录
    relative_path, error_resp, status_code = save_uploaded_file(
        file, role, user_id)
    if error_resp:
        return error_resp, status_code

    # 返回图片URL
    return jsonify({
        "image_url": get_file_url(relative_path)
    }), 201
