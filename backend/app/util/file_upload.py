import os
import uuid
from flask import current_app, jsonify
from app.config import ALLOWED_EXTENSIONS


def get_upload_dir(
    course_id,
    course_hw_no,
    resource_type: str,  # NOTE: post / submit
    student_id: int = None  # 仅在resource_type为submit的时候需要
) -> str:
    """
    生成作业相关文件的存储路径
    :param course_id: 课程ID
    :param course_hw_no: 作业ID（Homework.course_hw_no，在课程内唯一）
    :param resource_type: "post" 或 "submit"
    :param student_id: 学生ID（submit时必填）
    :return: 完整存储路径
    """
    base_dir = current_app.config['UPLOAD_FOLDER']

    # 基础路径：course/{course_id}/hw/{hw_id}/
    base_path = os.path.join(
        base_dir,
        "course",
        str(course_id),
        "hw",
        str(course_hw_no)
    )

    # 根据资源类型拼接子路径
    if resource_type == "post":
        # 老师发布的资源：post/
        return os.path.join(base_path, "post")
    elif resource_type == "submit":
        # 学生提交的资源：submit/student/{student_id}/
        if student_id is None:
            raise ValueError("提交资源（submit）必须指定student_id")
        return os.path.join(base_path, "submit", "student", str(student_id))
    else:
        raise ValueError(f"不支持的资源类型：{resource_type}，仅支持'post'或'submit'")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(
    file,
    course_id,
    course_hw_no,
    resource_type: str,  # NOTE: post / submit
    student_id: int = None  # 仅在resource_type为submit的时候需要
):
    """保存上传的文件到用户专属目录并返回文件路径"""
    if not file or not allowed_file(file.filename):
        return None, jsonify({"error": "不支持的文件类型"}), 400

    storage_dir = get_upload_dir(
        course_id=course_id,
        course_hw_no=course_hw_no,
        resource_type=resource_type,
        student_id=student_id
    )
    os.makedirs(storage_dir, exist_ok=True)  # 确保目录存在
    # 生成唯一文件名（避免冲突）
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4()}.{file_ext}"
    filepath = os.path.join(storage_dir, filename)

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


def upload_image(
        file,
        course_id: int,
        course_hw_no: int,
        resource_type: str,
        student_id: int = None,
) -> str:
    """
    上传图片并返回可访问的URL
    :param file: 上传的文件对象
    :param course_id: 课程ID
    :param course_hw_no: 作业ID
    :param resource_type: "post" 或 "submit"
    :param student_id: 学生ID（submit时必填）
    :return: 图片的可访问URL
    """
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400

    # 调用工具函数保存到用户专属目录
    relative_path, error_resp, status_code = save_uploaded_file(
        file, course_id=course_id, course_hw_no=course_hw_no, resource_type=resource_type, student_id=student_id)
    if error_resp:
        return error_resp, status_code

    # 返回图片URL
    return get_file_url(relative_path)
