import os
import uuid
from flask import current_app, jsonify
from app.config import ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user_upload_dir(role, user_id):
    """获取用户专属上传目录"""
    # 根上传目录
    root_upload_dir = current_app.config['UPLOAD_FOLDER']
    # 拼接用户目录（role为student/teacher，user_id为用户ID）
    user_dir = os.path.join(root_upload_dir, role, str(user_id))
    # 确保目录存在
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def save_uploaded_file(file, role, user_id):
    """保存上传的文件到用户专属目录并返回文件路径"""
    if not file or not allowed_file(file.filename):
        return None, jsonify({"error": "不支持的文件类型"}), 400

    # 获取用户专属目录
    user_dir = get_user_upload_dir(role, user_id)

    # 生成唯一文件名（避免冲突）
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4()}.{file_ext}"
    filepath = os.path.join(user_dir, filename)

    # 保存文件
    try:
        file.save(filepath)
        # 返回相对路径（用于存储到数据库）
        relative_path = os.path.relpath(
            filepath, current_app.config['UPLOAD_FOLDER'])
        return relative_path, None, None
    except Exception as e:
        return None, jsonify({"error": f"文件保存失败: {str(e)}"}), 500


def get_file_url(relative_path):
    """生成文件访问URL"""
    return f"/uploads/{relative_path}"
