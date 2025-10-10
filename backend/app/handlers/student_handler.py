import os
import shutil
from flask import jsonify
from flask_jwt_extended import create_access_token
from app.services.student_service import (
    authenticate_student,
    register_student,
    get_student,
    get_student_courses,
    enroll_course,
    get_student_course_homeworks,
    submit_homework,
    update_student_profile,
    update_student_password,
    get_student_homework_submission,
)
from app.util.file_upload import (
    upload_image,
    get_user_upload_dir
)

# 认证相关处理函数


def handle_student_login(data):
    """处理学生登录"""
    student_no = data.get('student_no')
    password = data.get('password')

    if not student_no or not password:
        return jsonify({"error": "学号和密码不能为空"}), 400

    success, result = authenticate_student(student_no, password)
    if not success:
        return jsonify({"error": result}), 401

    # 创建JWT令牌
    identity_str = f"student:{result['id']}"
    access_token = create_access_token(
        identity=identity_str,  # student:1（字符串）
    )

    return jsonify({
        "access_token": access_token,
        "student": {
            "id": result["id"],
            "student_no": result["student_no"],
            "name": result["name"],
            "email": result["email"],
            "phone": result["phone"],
        }
    }), 200


def handle_student_register(data):
    """处理学生注册请求"""
    success, result = register_student(data)
    if success:
        return jsonify({
            "message": "注册成功",
            "student": {
                "id": result["id"],
                "student_no": result["student_no"],
                "name": result["name"],
                "email": result["email"],
                "phone": result["phone"],
            }
        }), 201
    return jsonify({"error": result}), 400

# 学生信息相关处理函数


def handle_get_student_profile(student_id):
    """获取学生个人资料"""
    success, data = get_student(student_id)
    if success:
        return jsonify({
            "id": data["id"],
            "student_no": data["student_no"],
            "name": data["name"],
            "email": data["email"],
            "phone": data["phone"],
        }), 200
    return jsonify({"error": data}), 404


def handle_update_student_profile(student_id, update_data):
    """处理学生修改个人资料请求"""
    success, result = update_student_profile(student_id, update_data)
    if success:
        return jsonify({
            "message": "资料更新成功",
            "student": result
        }), 200
    # 区分"学生不存在"和其他错误（404 vs 400）
    if result == "学生不存在":
        return jsonify({"error": result}), 404
    return jsonify({"error": result}), 400


def handle_update_student_password(student_id, password_data):
    """处理学生修改密码请求"""
    old_password = password_data.get("old_password")
    new_password = password_data.get("new_password")

    # 基础参数校验
    if not old_password or not new_password:
        return jsonify({"error": "原密码和新密码不能为空"}), 400

    # 调用服务层逻辑
    success, error_msg = update_student_password(
        student_id, old_password, new_password
    )

    if success:
        return jsonify({"message": "密码修改成功，请重新登录"}), 200
    return jsonify({"error": error_msg}), 400

# NOTE: 课程相关处理函数


def handle_get_student_courses(student_id):
    """获取学生已选课程"""
    success, data = get_student_courses(student_id)
    if success:
        return jsonify({
            "course_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_enroll_course(student_id, course_code):
    """处理学生选课"""
    if not course_code:
        return jsonify({"error": "课程代码不能为空"}), 400

    success, message = enroll_course(student_id, course_code)
    if success:
        return jsonify({"message": message}), 201
    return jsonify({"error": message}), 400


def handle_get_enrolled_course_homeworks(student_id, course_id):
    """获取学生已选课程的作业"""
    success, data = get_student_course_homeworks(
        student_id, course_id)
    if success:
        return jsonify({
            "homework_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_get_student_submission(student_id, course_id, homework_id):
    """处理获取学生作业提交内容的请求"""
    success, result = get_student_homework_submission(
        student_id, course_id, homework_id
    )
    if success:
        return jsonify({
            "message": "获取提交内容成功",
            "submission": result
        }), 200
    # 区分不同错误类型的状态码
    if result in ["未选修该课程，无权限查看", "该课程下无此作业"]:
        return jsonify({"error": result}), 403
    if result == "未提交该作业":
        return jsonify({"error": result}), 404
    return jsonify({"error": result}), 500


def handle_submit_homework(student_id, homework_id, homework_data):
    text_content = homework_data.get('text_content', '')
    image_urls = homework_data.get('image_urls', [])

    if not text_content and not image_urls:
        return jsonify({"error": "提交内容不能为空（至少需要文本或图片）"}), 400

    success, message = submit_homework(
        student_id=student_id,
        homework_id=homework_id,
        text_content=text_content,
        image_urls=image_urls
    )
    if success:
        return jsonify({"message": message}), 201
    return jsonify({"error": message}), 400


def handle_upload_homework_image(student_id, homework_id, files):
    success_urls = []
    error_messages = []

    storage_path = get_user_upload_dir(
        role="student", user_id=student_id, hw_id=homework_id)
    # 如果目录已存在则先清空（确保最新提交覆盖旧文件）
    if os.path.exists(storage_path):
        shutil.rmtree(storage_path)

    # 创建新目录
    os.makedirs(storage_path, exist_ok=True)

    for file in files:
        if file.filename == '':
            error_messages.append("存在空文件名的文件")
            continue

        try:
            # 调用单文件上传工具（假设 upload_image 已适配作业图片路径）
            image_url = upload_image(
                file=file,
                role="student",
                user_id=student_id,
                hw_id=homework_id  # 用于区分作业图片的存储路径
            )
            success_urls.append(image_url)
        except Exception as e:
            error_messages.append(f"文件 {file.filename} 上传失败: {str(e)}")

    # 构建响应
    if not success_urls:
        # 全部失败
        return jsonify({
            "error": "所有文件上传失败",
            "details": error_messages
        }), 400
    else:
        # 部分或全部成功
        return jsonify({
            "success_count": len(success_urls),
            "image_urls": success_urls,
            "errors": error_messages  # 记录失败的文件信息
        }), 201
