"""
调用链: router -> handler -> service
- router: 路由层,由此层与前端直接交互
- handler: 处理层,router调用handler来处理业务
- service: 服务层,实际的处理业务层,handler只负责调用对应的服务
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.handlers.student_handler import (
    handle_student_login,
    handle_student_register,
    handle_get_student_profile,
    handle_get_student_courses,
    handle_enroll_course,
    handle_get_enrolled_course_homeworks,
    handle_submit_homework,
    handle_upload_homework_image,
    handle_update_student_profile,
    handle_update_student_password,
    handle_get_student_submission,
    handle_get_course_teachers,
    handle_get_course_tas,
)
from app.util.parse_identity import (
    parse_identity
)

# 认证相关路由蓝图
student_auth_bp = Blueprint('student_auth', __name__, url_prefix='/api/auth/students')

# 学生资源路由蓝图
student_bp = Blueprint('students', __name__, url_prefix='/api/students')

# 认证接口


@student_auth_bp.route('/login', methods=['POST'])
def login():
    """学生登录接口"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_student_login(data)


@student_auth_bp.route('/register', methods=['POST'])
def register():
    """学生注册接口"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    return handle_student_register(data)


@student_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """学生重置密码接口（登录界面使用，无需JWT认证）"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    
    student_no = data.get('student_no')
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not student_no or not old_password or not new_password:
        return jsonify({"error": "学号、原密码和新密码不能为空"}), 400
    
    from app.services.student_service import reset_student_password_by_student_no
    success, error_msg = reset_student_password_by_student_no(student_no, old_password, new_password)
    
    if success:
        return jsonify({"message": "密码修改成功，请使用新密码登录"}), 200
    return jsonify({"error": error_msg}), 400


@student_auth_bp.route('/check-identifier', methods=['POST'])
def check_identifier():
    """检查学号是否存在"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求数据不能为空"}), 400
    
    identifier = data.get('identifier')
    if not identifier:
        return jsonify({"error": "学号不能为空"}), 400
    
    from app.services.student_service import check_student_identifier
    success, result = check_student_identifier(identifier)
    if success:
        return jsonify(result), 200
    return jsonify({"error": result}), 400


@student_auth_bp.route('/send-verification-code', methods=['POST'])
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
    
    # 验证联系方式是否匹配
    success, error_msg = verify_student_contact(user_id, contact, method)
    if not success:
        return jsonify({"error": error_msg}), 400
    
    # 生成验证码
    from app.util.verification_code import generate_verification_code, store_verification_code
    code = generate_verification_code()
    
    # 存储验证码
    store_verification_code(user_id, 'student', contact, method, code)
    
    # TODO: 实际发送验证码到邮箱或电话
    # 这里先打印到控制台，实际项目中应该调用邮件服务或短信服务
    print(f"验证码已生成: {code} (发送到 {contact})")
    
    # 实际项目中应该这样发送：
    # if method == 'email':
    #     send_email(contact, code)
    # elif method == 'phone':
    #     send_sms(contact, code)
    
    return jsonify({"message": "验证码已发送"}), 200


@student_auth_bp.route('/reset-password-with-verification', methods=['POST'])
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
    
    # 获取存储的验证码（需要知道验证方式，这里简化处理，实际应该从请求中获取）
    # 为了简化，我们假设验证码存储时包含了方法信息
    # 实际应该从请求中获取 method，或者从存储中查找
    from app.util.verification_code import get_verification_code, delete_verification_code
    from app.services.student_service import reset_student_password_with_verification
    
    # 尝试从email和phone两种方式获取验证码
    stored_code_email, _ = get_verification_code(user_id, 'student', 'email')
    stored_code_phone, _ = get_verification_code(user_id, 'student', 'phone')
    
    stored_code = stored_code_email or stored_code_phone
    method = 'email' if stored_code_email else 'phone'
    
    if not stored_code:
        return jsonify({"error": "验证码已过期或不存在"}), 400
    
    # 验证并重置密码
    success, error_msg = reset_student_password_with_verification(
        user_id, verification_code, new_password, stored_code
    )
    
    if success:
        # 删除验证码
        delete_verification_code(user_id, 'student', method)
        return jsonify({"message": "密码重置成功，请使用新密码登录"}), 200
    return jsonify({"error": error_msg}), 400

# 学生个人信息接口


@student_bp.route('/me', methods=['GET'])
@jwt_required()
def get_student_profile():
    """获取当前登录学生或助教的个人资料"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student_or_ta")
    if error_response:
        return error_response
    return handle_get_student_profile(student_id)


@student_bp.route('/me', methods=['PATCH'])
@jwt_required()
def update_student_profile_route():
    """修改当前登录学生或助教的个人资料"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student_or_ta")
    if error_response:
        return error_response

    update_data = request.get_json()
    if not update_data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_update_student_profile(student_id, update_data)


@student_bp.route('/me/password', methods=['PATCH'])
@jwt_required()
def update_password():
    """修改当前登录学生或助教的密码"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student_or_ta"
    )
    if error_response:
        return error_response

    password_data = request.get_json()
    if not password_data:
        return jsonify({"error": "请求数据不能为空"}), 400

    return handle_update_student_password(student_id, password_data)
# 学生课程相关接口


@student_bp.route('/me/courses', methods=['GET'])
@jwt_required()
def get_enrolled_courses():
    """获取当前学生或助教已选课程"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student_or_ta")
    if error_response:
        return error_response

    return handle_get_student_courses(student_id)


@student_bp.route('/me/courses', methods=['POST'])
@jwt_required()
def enroll_course():
    """学生或助教选课(准确的说是加入班级)"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student_or_ta")
    if error_response:
        return error_response

    data = request.get_json()
    return handle_enroll_course(student_id, data.get('course_code'))


@student_bp.route('/me/courses/<course_id>/homeworks', methods=['GET'])
@jwt_required()
def get_enrolled_course_homeworks(course_id):
    """获取某门课程的所有作业（支持学生和助教）"""
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student_or_ta")
    if error_response:
        return error_response

    return handle_get_enrolled_course_homeworks(student_id, course_id)


@student_bp.route('/me/courses/<course_id>/homeworks/<homework_id>/submission', methods=['GET'])
@jwt_required()
def get_homework_submission(course_id, homework_id):
    """查看当前学生或助教在某课程中某作业的提交内容"""
    # 解析身份信息
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student_or_ta"
    )
    if error_response:
        return error_response

    # 参数校验（确保ID为数字）
    try:
        course_id = int(course_id)
        homework_id = int(homework_id)
    except ValueError:
        return jsonify({"error": "课程ID和作业ID必须为数字"}), 400

    return handle_get_student_submission(student_id, course_id, homework_id)


@student_bp.route('/me/homeworks/<homework_id>/upload-image', methods=['POST', 'OPTIONS'])
@jwt_required(optional=True)
def upload_homework_image(homework_id):
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        return response, 200
    
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student_or_ta")
    if error_response:
        # 确保错误响应也包含CORS头
        if isinstance(error_response, tuple):
            response, status_code = error_response
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, status_code
        error_response.headers['Access-Control-Allow-Origin'] = '*'
        return error_response

    # 检查文件字段（支持 'file' 和 'homework_files'）
    files = None
    if 'file' in request.files:
        files = request.files.getlist('file')
    elif 'homework_files' in request.files:
        files = request.files.getlist('homework_files')
    
    if not files or all(file.filename == '' for file in files):
        response = jsonify({"error": "未找到文件或未选择有效文件"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, 400

    result = handle_upload_homework_image(student_id, homework_id, files)
    # 确保响应包含CORS头
    if isinstance(result, tuple):
        response, status_code = result
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, status_code
    result.headers['Access-Control-Allow-Origin'] = '*'
    return result


@student_bp.route('/me/homeworks/<homework_id>/submission', methods=['POST'])
@jwt_required()
def submit_homework(homework_id):
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student_or_ta")
    if error_response:
        return error_response
    homework_data = request.get_json()
    if not homework_data:
        return jsonify({"error": "提交数据不能为空"}), 400

    return handle_submit_homework(student_id=student_id, homework_id=homework_id, homework_data=homework_data)


@student_bp.route('/me/courses/<int:course_id>/teachers', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def get_course_teachers_for_student_route(course_id):
    """获取课程的教师列表（学生端使用）"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        return response, 200
    
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student_or_ta")
    if error_response:
        # 确保错误响应也包含CORS头
        if isinstance(error_response, tuple):
            response, status_code = error_response
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, status_code
        error_response.headers['Access-Control-Allow-Origin'] = '*'
        return error_response
    result = handle_get_course_teachers(student_id, course_id)
    # 确保响应包含CORS头
    if isinstance(result, tuple):
        response, status_code = result
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, status_code
    result.headers['Access-Control-Allow-Origin'] = '*'
    return result


@student_bp.route('/me/courses/<int:course_id>/tas', methods=['GET', 'OPTIONS'])
@jwt_required(optional=True)
def get_course_tas_for_student_route(course_id):
    """获取课程的助教列表（学生端使用）"""
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        return response, 200
    
    identity_str = get_jwt_identity()
    student_id, error_response = parse_identity(
        identity_str, expected_role="student_or_ta")
    if error_response:
        # 确保错误响应也包含CORS头
        if isinstance(error_response, tuple):
            response, status_code = error_response
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response, status_code
        error_response.headers['Access-Control-Allow-Origin'] = '*'
        return error_response
    result = handle_get_course_tas(student_id, course_id)
    # 确保响应包含CORS头
    if isinstance(result, tuple):
        response, status_code = result
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response, status_code
    result.headers['Access-Control-Allow-Origin'] = '*'
    return result
