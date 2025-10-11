from flask import Blueprint, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import StaffCourseRelation
from app.util import parse_identity

upload_bp = Blueprint('uploads', __name__)


@upload_bp.route('/uploads/<path:filename>')  # 使用path转换器支持多级目录
@jwt_required()
def uploaded_file(filename):
    """
    验证图片访问权限：
    - 老师：仅能访问自己所属课程的post目录和所有学生的submit目录
    - 学生：仅能访问自己的submit目录，无权访问post目录
    """
    identity_str = get_jwt_identity()
# NOTE: either student_id or reacher_id is None if we get the jwt identity
    student_id, student_error_response = parse_identity(
        identity_str, expected_role="student")
    teacher_id, teacher_error_response = parse_identity(
        identity_str, expected_role="teacher")
    if student_error_response or teacher_error_response:
        return jsonify({"error": "无权访问"}), 403

    path_parts = filename.split('/')
    if len(path_parts) < 5 or path_parts[0] != "course":
        return jsonify({"error": "无效的文件路径格式"}), 400

    try:
        course_id = int(path_parts[1])  # 提取课程ID
        course_hw_no = int(path_parts[3])      # 提取作业ID
        resource_type = path_parts[4]   # 提取资源类型：post 或 submit
    except (IndexError, ValueError):
        return jsonify({"error": "文件路径参数无效"}), 400

    # 3. 验证资源类型（仅允许post或submit）
    if resource_type not in ["post", "submit"]:
        return jsonify({"error": "不支持的资源类型"}), 400

    # 4. 解析学生提交路径中的student_id（仅submit类型需要）
    submit_student_id = None
    if resource_type == "submit":
        # submit路径格式：course/{c}/hw/{h}/submit/student/{s_id}/...
        if len(path_parts) < 7 or path_parts[5] != "student":
            return jsonify({"error": "学生提交资源路径格式无效"}), 400
        try:
            submit_student_id = int(path_parts[6])  # 提取提交者学生ID
        except (IndexError, ValueError):
            return jsonify({"error": "学生ID格式无效"}), 400

    # 5. 权限校验逻辑
    # 5.1 访问者是老师（teacher_id存在）
    if teacher_id is not None:
        # 验证老师是否属于当前课程（通过StaffCourseRelation关联）
        is_course_teacher = StaffCourseRelation.query.filter_by(
            staff_id=teacher_id,
            course_id=course_id
        ).first() is not None

        if not is_course_teacher:
            return jsonify({"error": "无权访问非所属课程的资源"}), 403

        # 老师可以访问所属课程的post目录和所有学生的submit目录（无需额外校验）
        pass  # 权限通过

    # 5.2 访问者是学生（student_id存在）
    elif student_id is not None:
        # 学生无权访问post目录（老师资源）
        if resource_type == "post":
            return jsonify({"error": "学生无权访问老师发布的资源"}), 403

        # 学生访问submit目录：必须是自己提交的（路径中的student_id与自己一致）
        if resource_type == "submit" and submit_student_id != student_id:
            return jsonify({"error": "无权访问其他学生的提交资源"}), 403

    # 5.3 既不是老师也不是学生（身份无效）
    else:
        return jsonify({"error": "无效的用户身份"}), 403

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
