from flask import Blueprint, jsonify, send_from_directory, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from app.models import StaffCourseRelation, StudentCourseRelation, StudentTARelation
from app.util.parse_identity import parse_identity

upload_bp = Blueprint('uploads', __name__)


@upload_bp.route('/uploads/<path:filename>')  # 使用path转换器支持多级目录
@jwt_required(optional=True)  # 允许可选认证（支持 URL 参数中的 token）
def uploaded_file(filename):
    """
    验证图片访问权限：
    - 老师：仅能访问自己所属课程的post目录和所有学生的submit目录
    - 学生：仅能访问自己的submit目录，可以访问已选课程的post目录
    - 助教：可以访问自己作为助教的课程的post目录，可以访问所有学生的submit目录
    """
    # 支持从 URL 参数中获取 token（用于 el-upload 等组件的图片预览）
    identity_str = get_jwt_identity()
    
    # 如果从 header 中没有获取到 token，尝试从 URL 参数中获取
    if not identity_str:
        token = request.args.get('token')
        if token:
            try:
                # 使用 decode_token 解码 token（验证签名和过期时间）
                # decode_token 返回字典，identity 存储在 'sub' 字段中
                decoded = decode_token(token, allow_expired=False)
                # Flask-JWT-Extended 将 identity 存储在 'sub' 字段中
                # decoded 是一个字典
                if isinstance(decoded, dict):
                    identity_str = decoded.get('sub')
                elif hasattr(decoded, 'sub'):
                    identity_str = decoded.sub
                else:
                    # 尝试通过 getattr 获取
                    identity_str = getattr(decoded, 'sub', None)
                
                # 调试信息
                print(f"Token decoded successfully. Identity: {identity_str}, Type: {type(decoded)}")
            except Exception as e:
                # 记录错误以便调试
                import traceback
                print(f"Token decode error for URL: {request.url}")
                print(f"Error: {str(e)}")
                print(traceback.format_exc())
                return jsonify({"error": f"无效的认证令牌: {str(e)}"}), 401
    
    if not identity_str:
        return jsonify({"error": "需要认证"}), 401
    
    # 解析身份：支持 student、teacher 和 ta（助教）
    # parse_identity 在失败时返回 3 个值 (None, error_response, status_code)
    # 成功时返回 2 个值 (user_id, None)
    # 我们需要正确处理这两种情况
    
    # 首先尝试解析为 staff（teacher 或 ta）
    staff_result = parse_identity(identity_str, expected_role="staff")
    if len(staff_result) == 3:
        staff_id = None
        is_ta = False
    else:
        staff_id, staff_error_response = staff_result
        if staff_error_response:
            staff_id = None
            is_ta = False
        else:
            # 检查是否是助教
            role, _ = identity_str.split(':', 1)
            is_ta = (role == "ta")
    
    # 尝试解析为学生（包括助教，因为助教也是学生）
    student_result = parse_identity(identity_str, expected_role="student_or_ta")
    if len(student_result) == 3:
        student_id = None
    else:
        student_id, student_error_response = student_result
        if student_error_response:
            student_id = None
    
    # 如果既不是 staff 也不是 student，返回错误
    if staff_id is None and student_id is None:
        return jsonify({"error": "无权访问"}), 403

    path_parts = filename.split('/')
    if len(path_parts) < 5 or path_parts[0] != "course":
        return jsonify({"error": "无效的文件路径格式"}), 400

    try:
        course_id = int(path_parts[1])  # 提取课程ID
        course_hw_no = int(path_parts[3])      # 提取作业ID
        resource_type = path_parts[4]   # 提取资源类型：post 或 submit
    except (IndexError, ValueError):
        return jsonify({"error": "文件路径参数无效"}), 400

    # 3. 验证资源类型（仅允许post或submit）
    if resource_type not in ["post", "submit"]:
        return jsonify({"error": "不支持的资源类型"}), 400

    # 4. 解析学生提交路径中的student_id（仅submit类型需要）
    submit_student_id = None
    if resource_type == "submit":
        # submit路径格式：course/{c}/hw/{h}/submit/student/{s_id}/...
        if len(path_parts) < 7 or path_parts[5] != "student":
            return jsonify({"error": "学生提交资源路径格式无效"}), 400
        try:
            submit_student_id = int(path_parts[6])  # 提取提交者学生ID
        except (IndexError, ValueError):
            return jsonify({"error": "学生ID格式无效"}), 400

    # 5. 权限校验逻辑
    # 对于助教（ta），需要根据访问的资源类型来判断应该使用学生权限还是教师权限
    # - 如果访问 post 目录：优先使用学生权限（检查选课），如果没有选课，再检查助教关系（教师端权限）
    # - 如果访问 submit 目录：如果是自己的提交，使用学生权限；如果是其他学生的提交，使用教师权限（检查助教关系）
    
    # 5.1 访问者是老师（非助教）
    if staff_id is not None and not is_ta:
        # 老师：验证是否属于当前课程（通过StaffCourseRelation关联）
        is_course_teacher = StaffCourseRelation.query.filter_by(
            staff_id=staff_id,
            course_id=course_id
        ).first() is not None

        if not is_course_teacher:
            return jsonify({"error": "无权访问非所属课程的资源"}), 403

        # 老师可以访问所属课程的post目录和所有学生的submit目录（无需额外校验）
        pass  # 权限通过

    # 5.2 访问者是助教或学生
    # 对于助教，优先使用学生权限（检查选课），如果没有选课，再使用助教权限
    # 对于普通学生，只使用学生权限
    elif student_id is not None:
        if resource_type == "post":
            # 访问 post 目录：优先检查是否已选该课程（学生权限）
            is_enrolled = StudentCourseRelation.query.filter_by(
                student_id=student_id,
                course_id=course_id
            ).first() is not None
            
            if is_enrolled:
                # 已选课，允许访问（学生权限）
                pass  # 权限通过
            elif is_ta:
                # 助教但没有选课：检查是否是助教（教师端权限）
                is_course_ta = StudentTARelation.query.filter_by(
                    student_id=student_id,
                    course_id=course_id
                ).first() is not None
                
                if not is_course_ta:
                    return jsonify({"error": "未选修该课程且非助教，无权访问作业资源"}), 403
                # 是助教，允许访问（教师端权限）
                pass  # 权限通过
            else:
                # 普通学生且未选课，拒绝访问
                return jsonify({"error": "未选修该课程，无权访问作业资源"}), 403

        elif resource_type == "submit":
            # 访问 submit 目录
            if submit_student_id == student_id:
                # 访问自己的提交：使用学生权限，允许访问
                pass  # 权限通过
            elif is_ta:
                # 助教访问其他学生的提交：检查是否是助教（教师端权限）
                is_course_ta = StudentTARelation.query.filter_by(
                    student_id=student_id,
                    course_id=course_id
                ).first() is not None
                
                if not is_course_ta:
                    return jsonify({"error": "无权访问其他学生的提交资源"}), 403
                # 是助教，允许访问（教师端权限）
                pass  # 权限通过
            else:
                # 普通学生访问其他学生的提交，拒绝访问
                return jsonify({"error": "无权访问其他学生的提交资源"}), 403

    # 5.3 既不是 staff 也不是学生（身份无效）
    else:
        return jsonify({"error": "无效的用户身份"}), 403

    # 发送文件，并确保包含CORS头
    response = send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    # 添加CORS头以确保PDF文件可以跨域加载
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response
