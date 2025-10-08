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
    upload_image
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


def handle_upload_homework_image(student_id, homework_id, file):
    try:
        image_url = upload_image(
            file=file,
            role="student",
            user_id=student_id,
            hw_id=homework_id
        )
        return jsonify({"image_url": image_url}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
