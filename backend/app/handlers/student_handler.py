import os
import shutil
from flask import jsonify
from flask_jwt_extended import create_access_token
from app.services.student_service import (
    authenticate_student,
    get_student,
    get_student_courses,
    enroll_student_in_course,
    get_student_course_homeworks
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

    student = authenticate_student(student_no, password)
    if not student:
        return jsonify({"error": "学号或密码错误"}), 401

    # 创建JWT令牌
    identity_str = f"student:{student['id']}"
    access_token = create_access_token(
        identity=identity_str,  # student:1（字符串）
    )

    return jsonify({
        "access_token": access_token,
        "student": {
            "id": student["id"],
            "name": student["name"],
            "student_no": student["student_no"]
        }
    }), 200

# 学生信息相关处理函数


def handle_get_student_profile(student_id):
    """获取学生个人资料"""
    student = get_student(student_id)
    if not student:
        return jsonify({"error": "学生不存在"}), 404

    # 返回不包含敏感信息的学生资料
    return jsonify({
        "id": student["id"],
        "student_no": student["student_no"],
        "name": student["name"],
        "email": student["email"],
        "phone": student["phone"]
    }), 200

# 课程相关处理函数


def handle_get_student_courses(student_id):
    """获取学生已选课程"""
    courses = get_student_courses(student_id)
    return jsonify({
        "courses": courses,
        "count": len(courses)
    }), 200


def handle_enroll_course(student_id, course_code):
    """处理学生选课"""
    if not course_code:
        return jsonify({"error": "课程代码不能为空"}), 400

    success, message = enroll_student_in_course(student_id, course_code)
    if success:
        return jsonify({"message": message}), 201
    return jsonify({"error": message}), 400


def handle_get_enrolled_course_homeworks(student_id, course_id):
    """获取学生已选课程的作业"""
    homeworks = get_student_course_homeworks(student_id, course_id)
    return jsonify({

    })


def handle_submit_homework(student_id, homework_id, homework):
    # TODO
    return jsonify({

    })


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
