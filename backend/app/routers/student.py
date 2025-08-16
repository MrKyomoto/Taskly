"""
调用链: router -> handler -> service
- router: 路由层,由此层与前端直接交互
- handler: 处理层,router调用handler来处理业务
- service: 服务层,实际的处理业务层,handler只负责调用对应的服务
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.handlers.student_handler import (
    student_login,
    get_student_profile,
    enroll_course,
    get_enrolled_courses
)

bp = Blueprint('student', __name__, url_prefix='/api/student')

# 学生登录


@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    return student_login(data)

# 获取个人信息


@bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_info = get_jwt_identity()  # 从JWT中获取用户信息
    return get_student_profile(user_info['id'])

# 选课


@bp.route('/courses/enroll', methods=['POST'])
@jwt_required()
def enroll():
    user_info = get_jwt_identity()
    data = request.json
    return enroll_course(student_id=user_info['id'], course_code=data.get('course_code'))

# 获取已选课程


@bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    user_info = get_jwt_identity()
    return get_enrolled_courses(student_id=user_info['id'])


@bp.route('/courses/<course_id>/homeworks',methods=['GET'])
@jwt_required()
def get_course_homeworks():
    todo!()
