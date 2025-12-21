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
    reset_student_password_by_student_no,
    check_student_identifier,
    verify_student_contact,
    reset_student_password_with_verification,
    get_course_teachers_for_student,
    get_course_tas_for_student,
)
from app.util.verification_code import (
    generate_verification_code,
    store_verification_code,
    get_verification_code,
    delete_verification_code,
)
from app.util.file_upload import (
    upload_image,
    get_upload_dir
)
from app.models import Homework, StudentCourseRelation

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


def handle_get_course_teachers(student_id, course_id):
    """获取课程的教师列表（学生端）"""
    success, result = get_course_teachers_for_student(student_id, course_id)
    if success:
        response = jsonify({
            "teacher_list": result,
            "count": len(result)
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 200
    response = jsonify({"error": result})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response, 400


def handle_get_course_tas(student_id, course_id):
    """获取课程的助教列表（学生端）"""
    success, result = get_course_tas_for_student(student_id, course_id)
    if success:
        response = jsonify({
            "ta_list": result,
            "count": len(result)
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 200
    response = jsonify({"error": result})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response, 400


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

    try:
        homework = Homework.query.get(homework_id)
        if not homework:
            response = jsonify({"error": f"作业ID {homework_id} 不存在"})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 404
        course_id = homework.course_id

        # 检查学生是否选了这个课程，或者是否是助教
        from app.models import StudentTARelation
        is_enrolled = StudentCourseRelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        ta_relation = StudentTARelation.query.filter_by(
            student_id=student_id,
            course_id=course_id
        ).first()
        
        if not is_enrolled and not ta_relation:
            response = jsonify({"error": "未选修该课程,无法提交作业"})
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 403

        for file in files:
            if file.filename == '':
                error_messages.append("存在空文件名的文件")
                continue

            try:
                # 调用单文件上传工具（支持图片和PDF）
                from app.util.file_upload import upload_file
                file_url = upload_file(
                    file=file,
                    course_id=course_id,
                    course_hw_no=homework.course_hw_no,
                    resource_type="submit",
                    student_id=student_id
                )
                # upload_file返回URL字符串或错误响应(tuple)，需要检查
                if isinstance(file_url, tuple):
                    # 如果是错误响应，跳过
                    error_messages.append(f"文件 {file.filename} 上传失败")
                    continue
                # 如果是字符串URL，添加到成功列表
                if isinstance(file_url, str):
                    success_urls.append(file_url)
                else:
                    error_messages.append(f"文件 {file.filename} 上传失败：未知错误")
            except Exception as e:
                error_messages.append(f"文件 {file.filename} 上传失败: {str(e)}")

    # 构建响应
        if not success_urls:
            # 全部失败
            response = jsonify({
                "error": "所有文件上传失败",
                "details": error_messages
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 400
        else:
            # 部分或全部成功
            response = jsonify({
                "success_count": len(success_urls),
                "image_urls": success_urls,
                "errors": error_messages  # 记录失败的文件信息
            })
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, 201
    except Exception as e:
        response = jsonify({"error": f"上传处理失败:{str(e)}"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 500
