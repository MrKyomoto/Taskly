from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.handlers.teacher_handler import (
    handle_teacher_login,
    handle_teacher_register,
    handle_get_teacher_profile,
    handle_get_teacher_courses,
    handle_create_course,
    handle_update_course,
    handle_create_homework,
    handle_get_course_homeworks,
    handle_get_student_submissions,
    handle_grade_submission,
    handle_update_teacher_profile,
    handle_update_teacher_password,
    handle_update_homework,
    handle_delete_homework,
    handle_get_course_students,
    handle_export_course_grades,
    handle_publish_homework_grades,
)
from app.util.parse_identity import parse_identity
from app.services.teacher_service import (
    check_teacher_identifier,
    verify_teacher_contact,
    reset_teacher_password_with_verification,
)
from app.util.verification_code import (
    generate_verification_code,
    store_verification_code,
    get_verification_code,
    delete_verification_code,
)

# 认证相关路由蓝图
teacher_auth_bp = Blueprint('teacher_auth', __name__, url_prefix='/api/auth/teachers')

# 教师资源路由蓝图
teacher_bp = Blueprint('teachers', __name__, url_prefix='/api/teachers')

# 认证接口


@teacher_auth_bp.route('/login', methods=['POST'])
def login():
    """教师登录接口"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_teacher_login(data)


@teacher_auth_bp.route('/register', methods=['POST'])
def register():
    """教师注册接口"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_teacher_register(data)


@teacher_auth_bp.route('/check-identifier', methods=['POST'])
def check_identifier():
    """检查工号是否存在"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    
    identifier = data.get('identifier')
    if not identifier:
        return jsonify({"error": "工号不能为空"}), 400
    
    from app.services.teacher_service import check_teacher_identifier
    success, result = check_teacher_identifier(identifier)
    if success:
        return jsonify(result), 200
    return jsonify({"error": result}), 400


@teacher_auth_bp.route('/send-verification-code', methods=['POST'])
def send_verification_code():
    """发送验证码"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    
    user_id = data.get('user_id')
    contact = data.get('contact')
    method = data.get('method')  # 'email' or 'phone'
    
    if not user_id or not contact or not method:
        return jsonify({"error": "参数不完整"}), 400
    
    from app.services.teacher_service import verify_teacher_contact
    from app.util.verification_code import generate_verification_code, store_verification_code
    
    # 验证联系方式是否匹配
    success, error_msg = verify_teacher_contact(user_id, contact, method)
    if not success:
        return jsonify({"error": error_msg}), 400
    
    # 生成验证码
    code = generate_verification_code()
    
    # 存储验证码
    store_verification_code(user_id, 'teacher', contact, method, code)
    
    # TODO: 实际发送验证码到邮箱或电话
    print(f"验证码已生成: {code} (发送到 {contact})")
    
    return jsonify({"message": "验证码已发送"}), 200


@teacher_auth_bp.route('/reset-password-with-verification', methods=['POST'])
def reset_password_with_verification():
    """通过验证码重置密码"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    
    user_id = data.get('user_id')
    verification_code = data.get('verification_code')
    new_password = data.get('new_password')
    
    if not user_id or not verification_code or not new_password:
        return jsonify({"error": "参数不完整"}), 400
    
    from app.util.verification_code import get_verification_code, delete_verification_code
    from app.services.teacher_service import reset_teacher_password_with_verification
    
    # 尝试从email和phone两种方式获取验证码
    stored_code_email, _ = get_verification_code(user_id, 'teacher', 'email')
    stored_code_phone, _ = get_verification_code(user_id, 'teacher', 'phone')
    
    stored_code = stored_code_email or stored_code_phone
    method = 'email' if stored_code_email else 'phone'
    
    if not stored_code:
        return jsonify({"error": "验证码已过期或不存在"}), 400
    
    # 验证并重置密码
    success, error_msg = reset_teacher_password_with_verification(
        user_id, verification_code, new_password, stored_code
    )
    
    if success:
        # 删除验证码
        delete_verification_code(user_id, 'teacher', method)
        return jsonify({"message": "密码重置成功，请使用新密码登录"}), 200
    return jsonify({"error": error_msg}), 400

# 教师个人信息接口


@teacher_bp.route('/me', methods=['GET'])
@jwt_required()
def get_teacher_profile():
    """获取当前登录教师的个人资料"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response
    return handle_get_teacher_profile(teacher_id)


@teacher_bp.route('/me', methods=['PATCH'])
@jwt_required()
def update_teacher_profile():
    """修改当前登录教师的个人资料"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    update_data = request.get_json()
    if not update_data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_update_teacher_profile(teacher_id, update_data)


@teacher_bp.route('/me/password', methods=['PATCH'])
@jwt_required()
def update_password():
    """修改当前登录教师的密码"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    password_data = request.get_json()
    if not password_data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_update_teacher_password(teacher_id, password_data)

# 教师课程相关接口


@teacher_bp.route('/me/courses', methods=['GET'])
@jwt_required()
def get_teacher_courses():
    """获取当前教师或助教负责的课程"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="staff")  # 支持 teacher 和 ta
    if error_response:
        return error_response

    return handle_get_teacher_courses(teacher_id)


@teacher_bp.route('/me/courses', methods=['POST'])
@jwt_required()
def create_course():
    """创建新课程"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    course_data = request.get_json()
    if not course_data:
        return jsonify({"error": "课程数据不能为空"}), 400

    return handle_create_course(teacher_id, course_data)


@teacher_bp.route('/me/courses/<course_id>', methods=['PATCH'])
@jwt_required()
def update_course(course_id):
    """更新课程信息"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    update_data = request.get_json()
    if not update_data:
        return jsonify({"error": "更新数据不能为空"}), 400

    return handle_update_course(teacher_id, course_id, update_data)

# 作业相关接口


@teacher_bp.route('/me/courses/<course_id>/homeworks', methods=['GET'])
@jwt_required()
def get_course_homeworks(course_id):
    """获取课程下的所有作业"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    return handle_get_course_homeworks(teacher_id, course_id)


@teacher_bp.route('/me/courses/<course_id>/homeworks', methods=['POST'])
@jwt_required()
def create_homework(course_id):
    """创建课程作业（支持教师和助教）"""
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")  # 改为 staff，支持 teacher 和 ta
    if error_response:
        return error_response

    homework_data = request.get_json()
    if not homework_data:
        return jsonify({"error": "作业数据不能为空"}), 400

    return handle_create_homework(staff_id, course_id, homework_data)

# 批改相关接口


@teacher_bp.route('/me/courses/<course_id>/homeworks/<homework_id>/submissions', methods=['GET'])
@jwt_required()
def get_student_submissions(course_id, homework_id):
    """获取学生作业提交列表（支持教师和助教）"""
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")  # 改为 staff，支持 teacher 和 ta
    if error_response:
        return error_response

    return handle_get_student_submissions(staff_id, course_id, homework_id)


@teacher_bp.route('/me/submissions/<submission_id>/grade', methods=['POST'])
@jwt_required()
def grade_submission(submission_id):
    """批改学生作业（支持教师和助教）"""
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")  # 改为 staff，支持 teacher 和 ta
    if error_response:
        return error_response

    grade_data = request.get_json()
    if not grade_data:
        return jsonify({"error": "评分数据不能为空"}), 400

    return handle_grade_submission(staff_id, submission_id, grade_data)


@teacher_bp.route('/me/courses/<course_id>/homeworks/<homework_id>/students/<student_id>/grade-zero', methods=['POST'])
@jwt_required()
def grade_unsubmitted_student(course_id, homework_id, student_id):
    """为未提交学生打0分"""
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")
    if error_response:
        return error_response

    grade_data = request.get_json() or {}
    
    try:
        course_id = int(course_id)
        homework_id = int(homework_id)
        student_id = int(student_id)
    except ValueError:
        return jsonify({"error": "ID必须为数字"}), 400

    from app.handlers.teacher_handler import handle_grade_unsubmitted_student
    return handle_grade_unsubmitted_student(staff_id, course_id, homework_id, student_id, grade_data)

# 编辑作业


@teacher_bp.route('/me/courses/<course_id>/homeworks/<homework_id>', methods=['PATCH', 'PUT'])
@jwt_required()
def update_homework(course_id, homework_id):
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")
    if error_response:
        return error_response

    homework_data = request.get_json()
    if not homework_data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_update_homework(staff_id, course_id, homework_id, homework_data)

# 删除作业


@teacher_bp.route('/me/courses/<course_id>/homeworks/<homework_id>', methods=['DELETE'])
@jwt_required()
def delete_homework(course_id, homework_id):
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")
    if error_response:
        return error_response

    return handle_delete_homework(staff_id, course_id, homework_id)

# 查看选课学生列表


@teacher_bp.route('/courses/<course_id>/students', methods=['GET'])
@jwt_required()
def get_course_students(course_id):
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")
    if error_response:
        return error_response

    return handle_get_course_students(staff_id, course_id)


@teacher_bp.route('/me/courses/<course_id>/add-ta', methods=['POST'])
@jwt_required()
def add_ta_to_course(course_id):
    """添加助教到课程（仅教师可用）"""
    identity_str = get_jwt_identity()
    teacher_id, error_response = parse_identity(
        identity_str, expected_role="teacher")
    if error_response:
        return error_response

    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400

    from app.handlers.teacher_handler import handle_add_ta_to_course
    return handle_add_ta_to_course(teacher_id, course_id, data)

# 导出课程成绩
@teacher_bp.route('/me/courses/<int:course_id>/export-grades', methods=['GET'])
@jwt_required()
def export_grades(course_id):
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")
    if error_response:
        return error_response

    # 解析可选过滤参数：homework_ids 和 student_ids（逗号分隔的 ID 列表）
    homework_ids_param = request.args.get('homework_ids')
    student_ids_param = request.args.get('student_ids')

    def parse_id_list(raw):
        if not raw:
            return None
        ids = []
        for part in raw.split(','):
            part = part.strip()
            if not part:
                continue
            try:
                ids.append(int(part))
            except ValueError:
                # 忽略非法 ID
                continue
        return ids or None

    homework_ids = parse_id_list(homework_ids_param)
    student_ids = parse_id_list(student_ids_param)

    return handle_export_course_grades(staff_id, course_id, homework_ids, student_ids)


@teacher_bp.route('/me/courses/<int:course_id>/homeworks/<int:homework_id>/publish-grades', methods=['POST'])
@jwt_required()
def publish_homework_grades(course_id, homework_id):
    """发布某次作业的成绩（学生在发布前看不到成绩）"""
    identity_str = get_jwt_identity()
    staff_id, error_response = parse_identity(
        identity_str, expected_role="staff")
    if error_response:
        return error_response

    return handle_publish_homework_grades(staff_id, course_id, homework_id)
