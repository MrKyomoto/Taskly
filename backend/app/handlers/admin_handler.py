from flask import jsonify
from flask_jwt_extended import create_access_token
from app.services.admin_service import (
    authenticate_admin,
    register_admin,
    get_all_teachers,
    get_all_students,
    get_all_staff,
    create_staff,
    reset_user_password,
    approve_course,
    get_all_courses,
    delete_user,
    get_admin_profile,
    update_admin_profile,
    update_admin_password,
    create_student,
    update_student,
    update_staff,
    create_course,
    update_course,
    close_course,
    delete_course,
    add_teacher_to_course,
    add_ta_to_course_admin,
    add_student_to_course
)


def handle_admin_login(data):
    """处理管理员登录"""
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    success, result = authenticate_admin(username, password)
    if not success:
        return jsonify({"error": result}), 401

    # 创建JWT令牌（格式："admin:id"）
    identity_str = f"admin:{result['id']}"
    access_token = create_access_token(identity=identity_str)

    return jsonify({
        "access_token": access_token,
        "admin": {
            "id": result["id"],
            "username": result["username"],
            "name": result["name"],
            "phone": result["phone"]
        }
    }), 200


def handle_admin_register(data):
    """处理管理员注册"""
    success, result = register_admin(data)
    if success:
        return jsonify({
            "message": "管理员创建成功",
            "admin": result
        }), 201
    return jsonify({"error": result}), 400


def handle_get_all_teachers():
    """获取所有教师"""
    success, data = get_all_teachers()
    if success:
        return jsonify({
            "teacher_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_get_all_students():
    """获取所有学生"""
    success, data = get_all_students()
    if success:
        return jsonify({
            "student_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_approve_course(course_id, data):
    """处理课程审核"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    approve_status = data.get('approve', True)
    success, result = approve_course(course_id, approve_status)
    if success:
        return jsonify({"message": result}), 200
    return jsonify({"error": result}), 400


def handle_get_all_courses():
    """获取所有课程"""
    success, data = get_all_courses()
    if success:
        return jsonify({
            "course_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_delete_user(user_type, user_id):
    """处理用户删除"""
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "用户ID必须为数字"}), 400

    success, result = delete_user(user_type, user_id)
    if success:
        return jsonify({"message": result}), 200
    return jsonify({"error": result}), 400


def handle_get_admin_profile(admin_id):
    """获取管理员资料"""
    success, data = get_admin_profile(admin_id)
    if success:
        return jsonify(data), 200
    return jsonify({"error": data}), 400


def handle_update_admin_profile(admin_id, data):
    """更新管理员资料"""
    success, result = update_admin_profile(admin_id, data)
    if success:
        return jsonify(result), 200
    return jsonify({"error": result}), 400


def handle_update_admin_password(admin_id, data):
    """更新管理员密码"""
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({"error": "请提供原密码和新密码"}), 400

    success, result = update_admin_password(admin_id, {
        "old_password": old_password,
        "new_password": new_password
    })
    if success:
        return jsonify({"message": "密码更新成功"}), 200
    return jsonify({"error": result}), 400


def handle_get_all_staff():
    """获取所有教职工（包括教师和助教）"""
    success, data = get_all_staff()
    if success:
        return jsonify({
            "staff_list": data,
            "count": len(data)
        }), 200
    return jsonify({"error": data}), 400


def handle_create_staff(data):
    """创建教职工"""
    success, result = create_staff(data)
    if success:
        return jsonify({
            "message": "教职工创建成功",
            "staff": result
        }), 201
    return jsonify({"error": result}), 400


def handle_reset_user_password(user_type, user_id, data):
    """重置用户密码"""
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({"error": "用户ID必须为数字"}), 400

    default_password = data.get('default_password', '123456')
    success, result = reset_user_password(user_type, user_id, default_password)
    if success:
        return jsonify({"message": result}), 200
    return jsonify({"error": result}), 400


def handle_create_student(data):
    """创建学生"""
    success, result = create_student(data)
    if success:
        return jsonify({
            "message": "学生创建成功",
            "student": result
        }), 201
    return jsonify({"error": result}), 400


def handle_update_student(student_id, data):
    """更新学生信息"""
    try:
        student_id = int(student_id)
    except ValueError:
        return jsonify({"error": "学生ID必须为数字"}), 400

    success, result = update_student(student_id, data)
    if success:
        return jsonify({
            "message": "学生信息更新成功",
            "student": result
        }), 200
    return jsonify({"error": result}), 400


def handle_update_staff(staff_id, data):
    """更新教职工信息"""
    try:
        staff_id = int(staff_id)
    except ValueError:
        return jsonify({"error": "教职工ID必须为数字"}), 400

    success, result = update_staff(staff_id, data)
    if success:
        return jsonify({
            "message": "教职工信息更新成功",
            "staff": result
        }), 200
    return jsonify({"error": result}), 400


def handle_create_course(data):
    """创建课程"""
    success, result = create_course(data)
    if success:
        return jsonify({
            "message": "课程创建成功",
            "course": result
        }), 201
    return jsonify({"error": result}), 400


def handle_update_course(course_id, data):
    """更新课程信息"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    success, result = update_course(course_id, data)
    if success:
        return jsonify({
            "message": "课程信息更新成功",
            "course": result
        }), 200
    return jsonify({"error": result}), 400


def handle_close_course(course_id):
    """课程结课"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    success, result = close_course(course_id)
    if success:
        return jsonify({"message": result}), 200
    return jsonify({"error": result}), 400


def handle_delete_course(course_id):
    """删除课程"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    success, result = delete_course(course_id)
    if success:
        return jsonify({"message": result}), 200
    return jsonify({"error": result}), 400


def handle_add_teacher_to_course(course_id, data):
    """管理员添加教师到课程"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    staff_no = data.get('staff_no')
    if not staff_no:
        return jsonify({"error": "工号不能为空"}), 400

    success, result = add_teacher_to_course(course_id, staff_no)
    if success:
        return jsonify({
            "message": "教师添加成功",
            "teacher": result
        }), 200
    return jsonify({"error": result}), 400


def handle_add_ta_to_course(course_id, data):
    """管理员添加助教到课程"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    student_no = data.get('student_no')
    if not student_no:
        return jsonify({"error": "学号不能为空"}), 400

    success, result = add_ta_to_course_admin(course_id, student_no)
    if success:
        return jsonify({
            "message": "助教添加成功",
            "ta": result
        }), 200
    return jsonify({"error": result}), 400


def handle_add_student_to_course(course_id, data):
    """管理员添加学生到课程"""
    try:
        course_id = int(course_id)
    except ValueError:
        return jsonify({"error": "课程ID必须为数字"}), 400

    student_no = data.get('student_no')
    if not student_no:
        return jsonify({"error": "学号不能为空"}), 400

    success, result = add_student_to_course(course_id, student_no)
    if success:
        return jsonify({
            "message": "学生添加成功",
            "student": result
        }), 200
    return jsonify({"error": result}), 400
