from flask import jsonify
from flask_jwt_extended import create_access_token
from app.services.teacher_service import (
    authenticate_teacher,
    register_teacher,
    get_teacher,
    update_teacher_profile,
    update_teacher_password,
    get_teacher_courses,
    create_course,
    update_course,
    create_homework,
    get_course_homeworks,
    get_student_submissions,
    grade_submission,
    update_homework_service,
    delete_homework_service,
    get_course_students_service
)
from app.models import StaffCourseRelation
from app.util.auth import is_staff_in_course


def handle_teacher_login(data):
    """处理教师登录"""
    staff_no = data.get('staff_no')
    password = data.get('password')

    if not staff_no or not password:
        return jsonify({"error": "工号和密码不能为空"}), 400

    success, result = authenticate_teacher(staff_no, password)
    if not success:
        return jsonify({"error": result}), 401

    # 创建JWT令牌
    identity_str = f"teacher:{result['id']}"
    access_token = create_access_token(identity=identity_str)

    return jsonify({
        "access_token": access_token,
        "teacher": {
            "id": result["id"],
            "staff_no": result["staff_no"],
            "name": result["name"],
            "email": result["email"],
            "phone": result["phone"],
        }
    }), 200


def handle_teacher_register(data):
    """处理教师注册请求"""
    success, result = register_teacher(data)
    if success:
        return jsonify({
            "message": "注册成功",
            "teacher": {
                "id": result["id"],
                "staff_no": result["staff_no"],
                "name": result["name"],
                "email": result["email"],
                "phone": result["phone"],
            }
        }), 201
    return jsonify({"error": result}), 400


def handle_get_teacher_profile(teacher_id):
    """获取教师个人资料"""
    success, data = get_teacher(teacher_id)
    if success:
        return jsonify({
            "id": data["id"],
            "staff_no": data["staff_no"],
            "name": data["name"],
            "email": data["email"],
            "phone": data["phone"],
        }), 200
    return jsonify({"error": data}), 404


def handle_update_teacher_profile(teacher_id, update_data):
    """处理教师修改个人资料请求"""
    success, result = update_teacher_profile(teacher_id, update_data)
    if success:
        return jsonify({
            "message": "资料更新成功",
            "teacher": result
        }), 200
    if result == "教师不存在":
        return jsonify({"error": result}), 404
    return jsonify({"error": result}), 400


def handle_update_teacher_password(teacher_id, password_data):
    """处理教师修改密码请求"""
    old_password = password_data.get("old_password")
    new_password = password_data.get("new_password")

    if not old_password or not new_password:
        return jsonify({"error": "原密码和新密码不能为空"}), 400

    success, error_msg = update_teacher_password(
        teacher_id, old_password, new_password)
    if success:
        return jsonify({"message": "密码修改成功，请重新登录"}), 200
    return jsonify({"error": error_msg}), 400


def handle_get_teacher_courses(teacher_id):
    """获取教师教授的课程"""
    success, data = get_teacher_courses(teacher_id)
    if success:
        return jsonify({
            "course_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_create_course(teacher_id, course_data):
    """处理创建课程"""
    success, result = create_course(teacher_id, course_data)
    if success:
        return jsonify({
            "message": "课程创建成功",
            "course": result
        }), 201
    return jsonify({"error": result}), 400


def handle_update_course(teacher_id, course_id, update_data):
    """处理更新课程"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    # 验证教师是否有权限修改该课程
    relation = StaffCourseRelation.query.filter_by(
        staff_id=teacher_id,
        course_id=course_id
    ).first()
    if not relation:
        return jsonify({"error": "无权限修改该课程"}), 403

    success, result = update_course(course_id, update_data)
    if success:
        return jsonify({
            "message": "课程更新成功",
            "course": result
        }), 200
    return jsonify({"error": result}), 400


def handle_create_homework(teacher_id, course_id, homework_data):
    """处理创建作业"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    # 验证权限
    relation = StaffCourseRelation.query.filter_by(
        staff_id=teacher_id,
        course_id=course_id
    ).first()
    if not relation:
        return jsonify({"error": "无权限为该课程创建作业"}), 403

    success, result = create_homework(course_id, teacher_id, homework_data)
    if success:
        return jsonify({
            "message": "作业创建成功",
            "homework": result
        }), 201
    return jsonify({"error": result}), 400


def handle_get_course_homeworks(teacher_id, course_id):
    """获取课程作业列表"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    # 验证权限
    relation = StaffCourseRelation.query.filter_by(
        staff_id=teacher_id,
        course_id=course_id
    ).first()
    if not relation:
        return jsonify({"error": "无权限查看该课程作业"}), 403

    success, data = get_course_homeworks(course_id)
    if success:
        return jsonify({
            "homework_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_get_student_submissions(teacher_id, course_id, homework_id):
    """获取学生作业提交列表"""
    try:
        course_id = int(course_id)
        homework_id = int(homework_id)
    except ValueError:
        return jsonify({"error": "课程ID和作业ID必须为数字"}), 400

    # 验证权限
    relation = StaffCourseRelation.query.filter_by(
        staff_id=teacher_id,
        course_id=course_id
    ).first()
    if not relation:
        return jsonify({"error": "无权限查看该课程提交记录"}), 403

    success, data = get_student_submissions(course_id, homework_id)
    if success:
        return jsonify({
            "submission_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_grade_submission(teacher_id, submission_id, grade_data):
    """处理作业批改"""
    try:
        submission_id = int(submission_id)
    except ValueError:
        return jsonify({"error": "提交ID必须为数字"}), 400

    score = grade_data.get('score')
    annotation = grade_data.get('annotation_data')

    if score is None:
        return jsonify({"error": "评分不能为空"}), 400

    success, result = grade_submission(
        submission_id=submission_id,
        grader_id=teacher_id,
        score=score,
        annotation_data=annotation
    )
    if success:
        return jsonify({
            "message": "批改成功",
            "grading": result
        }), 200
    return jsonify({"error": result}), 400

# 处理作业更新


def handle_update_homework(staff_id, course_id, homework_id, homework_data):
    # 权限验证
    if not is_staff_in_course(staff_id, course_id):
        return jsonify({"error": "无此课程权限"}), 403

    # 调用服务层
    success, result = update_homework_service(
        homework_id, course_id, homework_data)
    if success:
        return jsonify({"message": "作业更新成功"}), 200
    return jsonify({"error": result}), 400

# 处理作业删除


def handle_delete_homework(staff_id, course_id, homework_id):
    # 权限验证
    if not is_staff_in_course(staff_id, course_id):
        return jsonify({"error": "无此课程权限"}), 403

    # 调用服务层
    success, result = delete_homework_service(homework_id, course_id)
    if success:
        return jsonify({"message": "作业删除成功"}), 200
    return jsonify({"error": result}), 400

# 处理选课学生查询


def handle_get_course_students(staff_id, course_id):
    # 权限验证
    if not is_staff_in_course(staff_id, course_id):
        return jsonify({"error": "无此课程权限"}), 403

    # 调用服务层
    success, result = get_course_students_service(course_id)
    if success:
        return jsonify({
            "student_list": result,
            "count": len(result)
        }), 200
    return jsonify({"error": result}), 400
