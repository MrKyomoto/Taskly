from app.services.student_service import (
    verify_student_credentials,
    get_student_by_id,
    enroll_student_in_course,
    get_student_courses
)
from flask import jsonify
from flask_jwt_extended import create_access_token

# TODO(有关作业的函数没有写API呢,得思考一下写什么)


def handle_student_login(data):
    # 验证请求参数
    student_no = data.get('student_no')
    password = data.get('password')
    if not student_no or not password:
        return jsonify({"code": 400, "msg": "学号和密码不能为空"}), 400

    # 调用服务层验证
    student = verify_student_credentials(student_no, password)
    if not student:
        return jsonify({"code": 401, "msg": "学号或密码错误"}), 401

    # 生成JWT令牌
    access_token = create_access_token(
        identity={"id": student.id, "role": "student"}
    )
    return jsonify({
        "code": 200,
        "msg": "登录成功",
        "data": {"token": access_token, "student": {"id": student.id, "name": student.name}}
    })


def handle_get_student_profile(student_id):
    student = get_student_by_id(student_id)
    if not student:
        return jsonify({"code": 404, "msg": "学生不存在"}), 404
    return jsonify({
        "code": 200,
        "data": {
            "id": student.id,
            "student_no": student.student_no,
            "name": student.name,
            "phone": student.phone,
            "email": student.email
        }
    })


def handle_enroll_course(student_id, course_code):
    if not course_code:
        return jsonify({"code": 400, "msg": "课程代码不能为空"}), 400

    result, msg = enroll_student_in_course(student_id, course_code)
    if result:
        return jsonify({"code": 200, "msg": "选课成功"})
    return jsonify({"code": 400, "msg": msg}), 400


def handle_get_enrolled_courses(student_id):
    courses = get_student_courses(student_id)
    return jsonify({
        "code": 200,
        "data": {
            "courses": [
                {
                    "id": course.id,
                    "course_code": course.course_code,
                    "course_name": course.course_name,
                    "semester": course.semester,
                    "description": course.description,
                    "status": course.status
                } for course in courses
            ]
        }
    })
def handle_get_enrolled_course_homeworks(student_id):
    # TODO:
    homeworks = 
